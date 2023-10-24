from django.utils.translation import ugettext as _
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.conf import settings
import requests
import os
from .viz import jprint, add_file, get_stat_df, load_full_project, load_data
from visualizations.models import DataPortal, UploadFile, DataType, Project
import copy
import sqlalchemy
import d6tstack.utils
from django.db import connection
import pandas as pd
import datetime
from datetime import date
import re

#search dataset
def search_dataset(request, portal_link, dataset):
    data = {'success': False, 'message': _('Impossible to access the api of the portal. Please make sure your link is correct or upload your file directly.')}
    if "current_platform" in request.session and request.session["current_platform"] is not None:
        sportal = request.session["current_platform"]
    else:
        sportal = soft_portal(request, portal_link)
        request.session["current_platform"] = sportal

    if sportal is not None:
        sportal = str(sportal)
        more_details = request.session["list_platformportals"][sportal]["more_details"]
        link = portal_link + more_details["suffix"] + more_details["search_dt"]
        #dataset = dataset.encode('UTF-8')
        if sportal == "1": #ODS
            link = link.replace("'#dt_id#'", '"'+str(dataset)+'"')
        elif sportal == "2": #CKAN
            link = link.replace("#dt_id#", str(dataset))
            link = link.replace("#start#", str(request.session["start"]))
            link = link.replace("#rows#", str(settings.NB_ROWS))

        #print(link)
        response = requests.get(link)
        if response and int(response.status_code) == 200:
            myresults = response.json()
            if sportal == "1": #ODS
                if myresults["total_count"] == 0:
                    data = {'success': False, 'message': _('No datasets match your request.')}
                else:
                    explore_link = portal_link + more_details["explore_dt"]
                    data = {'success': True, 'data': myresults, 'current_platform': sportal, 'explore_link': explore_link}
                    request.session["all_datasets"] += myresults["datasets"]
            elif sportal == "2": #CKAN
                if not myresults["success"]:
                    data = {'success': False, 'message': _('Impossible to retrieve data.')}
                elif "result" in myresults and "count" in myresults["result"] and  myresults["result"]["count"] == 0:
                    data = {'success': False, 'message': _('No datasets match your request.')}
                elif "result" in myresults and "results" in myresults["result"]:
                    final_results = convert_ckan_to_ods_format(request, portal_link, dataset, sportal, myresults)
                    explore_link = portal_link + more_details["explore_dt"]
                    data = {'success': True, 'data': final_results, 'current_platform': sportal, 'explore_link': explore_link}
                    request.session["all_datasets"] += final_results["datasets"]
        else:
            data = {'success': False, 'message': _('Impossible to retrieve data. Please try again later.')}
            #jprint(myresults)
    return data

#check if portal using ckan or ods
def soft_portal(request, portal_link):
    for key, platform in request.session["list_platformportals"].items():
        check = platform["more_details"]["check"]
        link = portal_link + check
        request = requests.get(link)
        if int(request.status_code) == 200:
            return key
    return None

#Convert results CKAn to ODS format
def convert_ckan_to_ods_format(request, portal_link, dataset, sportal, myresults):
    more_details = request.session["list_platformportals"][sportal]["more_details"]
    final_results = {}
    total_count = (int(request.session["start"])+1)*int(settings.NB_ROWS)
    next_link = ""
    links = []
    if myresults["result"]["count"] > total_count :
        next_link = portal_link + more_details["suffix"] + more_details["search_dt"]
        next_link = next_link.replace("#dt_id#", str(dataset))
        next_link = next_link.replace("#start#", str(total_count))
        next_link = next_link.replace("#rows#", str(settings.NB_ROWS))
        links.append({'href': next_link, 'rel': "next"})
        total_count = myresults["result"]["count"] - total_count
    else:
        total_count = 0

    mydatasets = []
    for mydata in myresults["result"]["results"]:
        name_data = None
        title_data = None
        description_data = None
        package_id = mydata["id"]
        if "name" in mydata:
            name_data = mydata["name"]
        if "title" in mydata:
            name_data = mydata["title"]
        if "notes" in mydata:
            description_data = mydata["notes"]
        if int(mydata["num_resources"]) > 0:
            for resource in mydata["resources"]:
                format = resource["format"].lower()
                if format == settings.EXPORT_ODP_FORMAT:
                    format_data = {}
                    format_data["dataset"] = {}
                    format_data["dataset"]["fields"] = []
                    format_data["dataset"]["metas"] = {}
                    format_data["dataset"]["metas"]["default"] = {}
                    format_data["dataset"]["dataset_id"] = resource["id"]
                    format_data["dataset"]["package_id"] = resource["package_id"]
                    format_data["dataset"]["url"] = resource["url"]
                    description = description_data
                    name = name_data
                    title = title_data
                    if "description" in resource and resource["description"] is not None:
                        description = resource["description"]
                    if "name" in resource and resource["name"] is not None:
                        title = resource["name"]
                        name = title.lower()
                        name = re.sub("[^0-9a-zA-Z]+", "-", name)
                    if "description" in resource and resource["description"] is not None:
                        description = resource["description"]

                    if "fields" in resource:
                        for fd in resource["fields"]:
                            format_data["dataset"]["fields"].append({"description":"", "name": fd["name"], "label": fd["title"], "type": fd["type"]+"#"+fd["sub_type"]})

                    format_data["dataset"]["package_id"] = resource["package_id"]
                    language = settings.LANGUAGE_CODE
                    if LANGUAGE_SESSION_KEY in request.session:
                        language = request.session[LANGUAGE_SESSION_KEY]
                    format_data["dataset"]["metas"]["default"]["language"] = language
                    modified = None
                    if "created" in resource:
                        modified = resource["created"]
                    if "last_modified" in resource and resource["last_modified"] and resource["last_modified"] is not None:
                        modified = resource["last_modified"]
                    format_data["dataset"]["metas"]["default"]["language"] = language
                    format_data["dataset"]["metas"]["default"]["modified"] = modified
                    format_data["dataset"]["metas"]["default"]["description"] = description
                    format_data["dataset"]["metas"]["default"]["title"] = title
                    format_data["dataset"]["metas"]["default"]["name"] = name
                    mydatasets.append(format_data)

    final_results = {'total_count': total_count+len(mydatasets), 'datasets':mydatasets, 'links':links}

    return final_results

#add op dataset to project
def add_opd(request, dataset_id, dataset_inc):
    data = {'is_valid': False, 'message': _('Unable to retrieve dataset')}
    sportal = str(request.session["current_platform"])
    if request.session["current_portal"] is None:
        new_portal = DataPortal()
        new_portal.name = request.session["current_portal_link"]
        new_portal.platform_id = int(sportal)
        new_portal.more_details = {"link": request.session["current_portal_link"]}
        new_portal.save()
        request.session["current_portal"] = str(new_portal.pk)

    if sportal == "1" or sportal == "2": #ODS  && CKAN
        portal_link = request.session["current_portal_link"]
        more_details = request.session["list_platformportals"][sportal]["more_details"]
        if sportal == "1":
            export_dt_link = portal_link + more_details["suffix"] + more_details["export_dt"]
            export_dt_link = export_dt_link.replace("#dt_id#", str(dataset_id))
            export_dt_link = export_dt_link.replace("#format#", str(settings.EXPORT_ODP_FORMAT))
            export_dt_link = export_dt_link.replace("#delimiter#", str(settings.DELIMITER_ODP))
        elif sportal == "2":
            export_dt_link = request.session["all_datasets"][int(dataset_inc)]["dataset"]["url"]
        data = None
        try:
            current_dst = request.session["all_datasets"][int(dataset_inc)]["dataset"]
            file_link = export_dt_link
            title = dataset_id
            if sportal == "2":
                if "name" in current_dst["metas"]["default"]:
                    title = current_dst["metas"]["default"]["name"]

            file_ext = "."+str(settings.EXPORT_ODP_FORMAT)
            portal_id = int(request.session["current_portal"])
            fields = {}
            for field in current_dst["fields"]:
                field_name = field["name"]
                field_desc = field["description"]
                field_label = field["label"]
                field_type= field["type"]

                if not field_label or field_label is None or field_label == "":
                    field_label = field_name

                fields[field_name] = {"name": field_name, "description": field_desc, "label": field_label, "online_type": field_type}

            db_title = current_dst["metas"]["default"]["title"]

            if not db_title or db_title is None or db_title == "":
                db_title = title

            more_details = {"title": db_title, "dataset_id": dataset_id,
             "description": current_dst["metas"]["default"]["description"], "modified": current_dst["metas"]["default"]["modified"],
             "language": [current_dst["metas"]["default"]["language"]], "fields": fields}
            if sportal == "2":
                if "package_id" in current_dst:
                    more_details["package_id"] = current_dst["package_id"]

            data, created = UploadFile.objects.get_or_create(title=title, portal_id=portal_id,
            defaults={'file_link': file_link, 'title': title,
            'file_ext': file_ext, 'portal_id': portal_id, 'more_details': more_details})

            current_file = {"id":data.pk, "code":data.code, "file_link":data.file_link, "title":data.title, "file_ext":data.file_ext
            , "is_demo":data.is_demo, "refresh_timeout":data.refresh_timeout, "init_settings":data.init_settings, "updated_at":data.updated_at
            , "more_details": data.more_details}
            insight = _("Add new open data #{}# to project").format(current_file["title"])

            if data.code in request.session["list_selectedfiles"]:
                data = {'is_valid': False, 'message': _('Dataset already exists in project')}
            else:
                data = add_file(request, current_file, insight)
        except Exception as e:
            print('Error details: '+ str(e))
            if data is not None:
                file_link = settings.MEDIA_ROOT+settings.UPLOAD_FILES+data.code+data.file_ext
                if os.path.isfile(file_link):
                    os.remove(file_link)
                data.delete()
            data = {'is_valid': False, 'message': _('File invalid')}

    return data

#Combine datasets
def combine_datasets(request):
    data = {'is_valid': False, 'message': _('Something went wrong')}
    try:
        query = "SELECT "
        dt1 = request.POST.get('combdata_dt1')
        dt2 = request.POST.get('combdata_dt2')
        rel = request.POST.get('combdata_rel')
        #col1 = request.POST.get('combdata_col1')
        #col2 = request.POST.get('combdata_col2')
        dtname = request.POST.get('combdata_dtname')
        col1_cols = request.POST.get('h_combdata_col1').split("##")
        col2_cols = request.POST.get('h_combdata_col2').split("##")

        load_data(request, DataType, "list_datatypes", 0)
        cols = []
        init_datatypes = {}
        init_columns = {}
        convert_dict = {}
        fields = {}

        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        database_uri  = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}'.format(
                user=user,
                password=password,
                database_name=database_name,
                host=host,
                port=port,
            )

        for dt in [dt1, dt2]:
            if dt in request.session["current_project"]["project_settings"]["files"]:
                myfile = request.session["current_project"]["project_settings"]["files"][str(dt)]
                for key, col in myfile["columns"].items():
                    if key in cols:
                        mycol = key+settings.SUFFIX_DUPLICATE_COL
                    else:
                        mycol = key
                    init_datatypes[mycol] = col["datatype"]
                    init_columns[mycol] = request.session["list_selectedfiles"][dt]["init_settings"]["init_columns"][key]
                    convert_dict[mycol] = request.session["list_datatypes"][str(col["datatype"])]["pandas_name"]
                    fields[mycol] = request.session["list_selectedfiles"][dt]["more_details"]["fields"][key]
                    fields[mycol]["label"] = col["label"]
                    fields[mycol]["description"] = col["description"]

                    cols.append(mycol)
                    add_col = "df_"+dt+"."+key+" as "+mycol+","
                    query += add_col
        query = query[:-1]
        query += " FROM df_"+dt1+" "+rel+" df_"+dt2+" ON "
        query_join = []
        icc = 0
        for ic in col1_cols:
            if ic and ic != "":
                col1 = col1_cols[icc]
                col2 = col2_cols[icc]
                query_join.append("df_"+dt1+"."+col1+"="+"df_"+dt2+"."+col2)
            icc = icc + 1
        query += ' AND '.join(query_join)
        #print("query=============================================================")
        #print(query)
        #print("init_datatypes=============================================================")
        #print(init_datatypes)
        #print("init_datatypes=============================================================")
        #print(init_columns)
        #print("convert_dict=============================================================")
        #print(convert_dict)

        new_file = UploadFile()
        desc1 = request.session["current_project"]["project_settings"]["files"][str(dt1)]["data_info"]["description"]
        tit1 = request.session["current_project"]["project_settings"]["files"][str(dt1)]["data_info"]["title"]
        desc2 = request.session["current_project"]["project_settings"]["files"][str(dt2)]["data_info"]["description"]
        tit2 = request.session["current_project"]["project_settings"]["files"][str(dt2)]["data_info"]["title"]
        description = _("Combination of datasets: {}, {} -- Description of {}: {} -- Description of {}: {}").format(tit1, tit2, tit1, desc1, tit2, desc2)
        language = request.session["list_selectedfiles"][dt1]["more_details"]["language"] + list(set(request.session["list_selectedfiles"][dt2]["more_details"]["language"]) - set(request.session["list_selectedfiles"][dt1]["more_details"]["language"]))
        more_details = {"query": query, "title": dtname, "dataset_id":"", "description": description, "language": language, "fields": fields}
        refresh_timeout = None
        if request.session["list_selectedfiles"][dt1]["refresh_timeout"]:
            refresh_timeout = request.session["list_selectedfiles"][dt1]["refresh_timeout"]
        if request.session["list_selectedfiles"][dt2]["refresh_timeout"]:
            if refresh_timeout and refresh_timeout is not None and int(refresh_timeout) > int(request.session["list_selectedfiles"][dt2]["refresh_timeout"]) :
                refresh_timeout = request.session["list_selectedfiles"][dt2]["refresh_timeout"]
            elif not refresh_timeout or refresh_timeout is None:
                refresh_timeout = request.session["list_selectedfiles"][dt2]["refresh_timeout"]

        new_file.title = dtname
        new_file.file_ext = settings.DEFAULT_FILE_SAVE
        new_file.from_query = True
        new_file.refresh_timeout = refresh_timeout
        new_file.more_details = more_details
        new_file.save()
        new_file.file_link = settings.MEDIA_URL[:-1] + settings.UPLOAD_FILES + new_file.code + ".csv"
        new_file.related_files.add(request.session["list_selectedfiles"][dt1]["id"])
        new_file.related_files.add(request.session["list_selectedfiles"][dt2]["id"])
        new_file.save(update_fields=['file_link'])

        current_file = {"id":new_file.pk, "code":new_file.code, "file_link":new_file.file_link, "title":new_file.title, "file_ext":new_file.file_ext
        , "is_demo":new_file.is_demo, "refresh_timeout":new_file.refresh_timeout, "init_settings":new_file.init_settings, "updated_at":new_file.updated_at, "more_details": new_file.more_details}
        insight = _("Add combined dataset #{}# to project").format(current_file["title"])

        #print("current_file=============================================================")
        #print(current_file)
        #print("=============================================================")

        engine = sqlalchemy.create_engine(database_uri, echo=False)
        if query is not None:
            df = pd.read_sql(sqlalchemy.text(query), con=engine)
            file_link = settings.BASE_DIR + current_file["file_link"]
            df.to_csv(file_link, encoding='utf-8', index=False)
            if bool(convert_dict):
            	df = df.astype(convert_dict)
            df_pkl = "df_" + current_file["code"]
            d6tstack.utils.pd_to_psql(df, database_uri, df_pkl, if_exists='replace', sep=';')
            data = add_df(request, df, init_datatypes, init_columns, current_file, insight)
    except Exception as e:
        print('Error details: '+ str(e))

    return data

#Delete some columns from datasets
def dropcol_dataset(request):
    data = {'is_valid': False, 'message': _('Something went wrong')}
    try:
        query = "SELECT "
        dt = request.POST.get('dropcol_dt')
        drop_cols = request.POST.get('h_dropcol_col').split("##")
        print(drop_cols)
        more_details = {}
        dtname = ""
        drop_dt = ""

        if request.POST.get('dropcol_dtname'):
            dtname = request.POST.get('dropcol_dtname')
        elif dt in request.session["list_selectedfiles"]:
            dtname = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["title"]
            drop_dt = dt

        if dt in request.session["list_selectedfiles"]:
            more_details = request.session["list_selectedfiles"][dt]["more_details"]

        dropcol_keep = request.POST.get("dropcol_keep")
        if dropcol_keep:
            dropcol_keep = True
        else:
            dropcol_keep = False

        if dropcol_keep == True:
            final_drop_cols = []
            if dt in request.session["current_project"]["project_settings"]["files"]:
                myfile = request.session["current_project"]["project_settings"]["files"][str(dt)]
                for key, col in myfile["columns"].items():
                    if key not in drop_cols:
                        final_drop_cols.append(key)
                drop_cols = copy.deepcopy(final_drop_cols)

        load_data(request, DataType, "list_datatypes", 0)
        cols = []
        init_datatypes = {}
        init_columns = {}
        convert_dict = {}
        fields = {}

        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        database_uri  = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}'.format(
                user=user,
                password=password,
                database_name=database_name,
                host=host,
                port=port,
            )

        if dt in request.session["current_project"]["project_settings"]["files"]:
            myfile = request.session["current_project"]["project_settings"]["files"][str(dt)]
            for key, col in myfile["columns"].items():
                if key not in drop_cols:
                    mycol = key
                    init_datatypes[mycol] = col["datatype"]
                    init_columns[mycol] = request.session["list_selectedfiles"][dt]["init_settings"]["init_columns"][key]
                    convert_dict[mycol]=request.session["list_datatypes"][str(col["datatype"])]["pandas_name"]
                    fields[mycol] = request.session["list_selectedfiles"][dt]["more_details"]["fields"][key]
                    fields[mycol]["label"] = col["label"]
                    fields[mycol]["description"] = col["description"]

                    cols.append(mycol)
                    add_col = "df_"+dt+"."+key+" as "+mycol+","
                    query += add_col
        query = query[:-1]
        query += " FROM df_"+dt
        print("query=============================================================")
        print(query)
        print("init_datatypes=============================================================")
        print(init_datatypes)
        print("init_columns=============================================================")
        print(init_columns)
        print("convert_dict=============================================================")
        print(convert_dict)

        new_file = UploadFile()
        new_file.title = dtname
        new_file.file_ext = settings.DEFAULT_FILE_SAVE
        new_file.from_query = True
        final_cols = []
        for col1 in drop_cols:
            if col1 and col1 != "":
                final_cols.append(col1)

        desc1 = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["description"]
        tit1 = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["title"]

        description = _("Deletion columns: {} from {} -- Description of {}: {}").format(', '.join(final_cols), tit1, tit1, desc1)
        language = request.session["list_selectedfiles"][str(dt)]["more_details"]["language"]
        more_details = {"query": query, "title": dtname, "dataset_id":"", "description": description, "language": language, "fields": fields}

        more_details["query"] = query
        more_details["fields"] = fields
        more_details["title"] = dtname
        more_details["dataset_id"] = ""
        more_details["description"] = description
        new_file.more_details = more_details
        refresh_timeout = None
        if request.session["list_selectedfiles"][str(dt)]["refresh_timeout"]:
            refresh_timeout = request.session["list_selectedfiles"][str(dt)]["refresh_timeout"]
        new_file.refresh_timeout = refresh_timeout

        new_file.save()
        new_file.file_link = settings.MEDIA_URL[:-1] + settings.UPLOAD_FILES + new_file.code + ".csv"
        new_file.related_files.add(request.session["list_selectedfiles"][dt]["id"])
        new_file.save(update_fields=['file_link'])

        current_file = {"id":new_file.pk, "code":new_file.code, "file_link":new_file.file_link, "title":new_file.title, "file_ext":new_file.file_ext
        , "is_demo":new_file.is_demo, "refresh_timeout":new_file.refresh_timeout, "init_settings":new_file.init_settings, "updated_at":new_file.updated_at, "more_details": new_file.more_details}
        insight = _("Drop columns and add new file #{}# to project").format(current_file["title"])

        #print("current_file=============================================================")
        #print(current_file)
        #print("=============================================================")

        engine = sqlalchemy.create_engine(database_uri, echo=False)
        if query is not None:
            df = pd.read_sql(sqlalchemy.text(query), con=engine)
            file_link = settings.BASE_DIR + current_file["file_link"]
            df.to_csv(file_link, encoding='utf-8', index=False)
            if bool(convert_dict):
            	df = df.astype(convert_dict)

            df_pkl = "df_" + current_file["code"]
            d6tstack.utils.pd_to_psql(df, database_uri, df_pkl, if_exists='replace', sep=';')
            data = add_df(request, df, init_datatypes, init_columns, current_file, insight, drop_dt)
    except Exception as e:
        print('Error details: '+ str(e))

    return data

#Search and replace in columns from datasets
def se_rep_dataset(request):
    data = {'is_valid': False, 'message': _('Something went wrong')}
    try:
        query = "SELECT "
        dt = request.POST.get('repval_dt')
        rep_cols = request.POST.get('h_repval_col').split("##")
        repval_rep = request.POST.get('repval_rep')
        repval_search = request.POST.get('repval_search')
        more_details = {}
        dtname = ""
        drop_dt = ""

        if request.POST.get('repval_dtname'):
            dtname = request.POST.get('repval_dtname')
        elif dt in request.session["list_selectedfiles"]:
            dtname = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["title"]
            drop_dt = dt

        if dt in request.session["list_selectedfiles"]:
            more_details = request.session["list_selectedfiles"][dt]["more_details"]

        load_data(request, DataType, "list_datatypes", 0)
        cols = []
        init_datatypes = {}
        init_columns = {}
        convert_dict = {}
        fields = {}

        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        database_uri  = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}'.format(
                user=user,
                password=password,
                database_name=database_name,
                host=host,
                port=port,
            )

        if dt in request.session["current_project"]["project_settings"]["files"]:
            myfile = request.session["current_project"]["project_settings"]["files"][str(dt)]
            for key, col in myfile["columns"].items():
                mycol = key
                init_datatypes[mycol] = col["datatype"]
                init_columns[mycol] = request.session["list_selectedfiles"][dt]["init_settings"]["init_columns"][key]
                convert_dict[mycol]=request.session["list_datatypes"][str(col["datatype"])]["pandas_name"]
                fields[mycol] = request.session["list_selectedfiles"][dt]["more_details"]["fields"][key]
                fields[mycol]["label"] = col["label"]
                fields[mycol]["description"] = col["description"]

                cols.append(mycol)
                add_col = "df_"+dt+"."+key+" as "+mycol+","
                query += add_col
        query = query[:-1]
        query += " FROM df_"+dt
        #print("query=============================================================")
        #print(query)
        #print("init_datatypes=============================================================")
        #print(init_datatypes)
        #print("init_datatypes=============================================================")
        #print(init_columns)
        #print("convert_dict=============================================================")
        #print(convert_dict)

        new_file = UploadFile()
        new_file.title = dtname
        new_file.file_ext = settings.DEFAULT_FILE_SAVE
        new_file.from_query = True
        more_details["query"] = query
        more_details["fields"] = fields
        more_details["title"] = dtname
        more_details["dataset_id"] = ""
        final_cols = []
        for col1 in rep_cols:
            if col1 and col1 != "":
                final_cols.append(col1)

        desc1 = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["description"]
        tit1 = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["title"]

        if repval_search:
            description = _("Search {} and replace by {} in columns: {} of {} -- Description of {}: {}").format(repval_search, repval_rep, ', '.join(final_cols), tit1, tit1, desc1)
        else:
            description = _("Replace null values by {} in columns: {} of {} -- Description of {}: {}").format(repval_rep, ', '.join(final_cols), tit1, tit1, desc1)

        more_details["description"] = description
        new_file.more_details = more_details
        refresh_timeout = None
        if request.session["list_selectedfiles"][str(dt)]["refresh_timeout"]:
            refresh_timeout = request.session["list_selectedfiles"][str(dt)]["refresh_timeout"]
        new_file.refresh_timeout = refresh_timeout
        new_file.save()
        new_file.file_link = settings.MEDIA_URL[:-1] + settings.UPLOAD_FILES + new_file.code + ".csv"
        new_file.related_files.add(request.session["list_selectedfiles"][dt]["id"])
        new_file.save(update_fields=['file_link'])

        current_file = {"id":new_file.pk, "code":new_file.code, "file_link":new_file.file_link, "title":new_file.title, "file_ext":new_file.file_ext
        , "is_demo":new_file.is_demo, "refresh_timeout":new_file.refresh_timeout, "init_settings":new_file.init_settings, "updated_at":new_file.updated_at, "more_details": new_file.more_details}
        insight = _("Drop columns and add new file #{}# to project").format(current_file["title"])

        #print("current_file=============================================================")
        #print(current_file)
        #print("=============================================================")

        engine = sqlalchemy.create_engine(database_uri, echo=False)
        if query is not None:
            df = pd.read_sql(sqlalchemy.text(query), con=engine)
            final_rep_cols = []
            for col1 in rep_cols:
                if col1 and col1 != "":
                    final_rep_cols.append(col1)

            if repval_search:
                df[final_rep_cols] = df[final_rep_cols].replace(repval_search,repval_rep)
            else:
                df[final_rep_cols] = df[final_rep_cols].fillna(repval_rep)

            file_link = settings.BASE_DIR + current_file["file_link"]
            df.to_csv(file_link, encoding='utf-8', index=False)
            if bool(convert_dict):
            	df = df.astype(convert_dict)
            df_pkl = "df_" + current_file["code"]
            d6tstack.utils.pd_to_psql(df, database_uri, df_pkl, if_exists='replace', sep=';')
            data = add_df(request, df, init_datatypes, init_columns, current_file, insight, drop_dt)
    except Exception as e:
        print('Error details: '+ str(e))

    return data


#Add df to project
def add_df(request, df, init_datatypes, init_columns, current_file, insight="", drop_dt=""):
    data = {'is_valid': False, 'message': _('Something went wrong')}
    if current_file:
        file_code = current_file["code"]
        current_project = request.session["current_project"]
        if not current_project:
            return data
        project_history = []
        project_settings = {}
        nb_dfs = 0
        json_columns = {}
        current_state = 0
        all_stat = {}
        data_info = {"title": "","description": ""}
        quality = {"complete_data":0, "column_labels":0,"column_descriptions":0,"data_info":0, "average": 0}
        nb_tot_values = 0

        if bool(current_project["project_settings"]):
            project_history = copy.deepcopy(current_project["project_history"])
            project_settings = copy.deepcopy(current_project["project_settings"])
            nb_dfs = project_settings["nb_dfs"]

        if df is None:
            return {'is_valid': False, 'message': _('Unable to load the file')}

        all_stat = get_stat_df(request, df, init_datatypes)

        more_details = {}
        if bool(current_file["more_details"]):
            more_details = current_file["more_details"]

        if bool(more_details) and "title" in more_details:
            data_info["title"] = more_details["title"]
            if data_info["title"] and data_info["title"] != "":
                quality["data_info"] = quality["data_info"] + 1

        if not data_info["title"] and data_info["title"] is None or data_info["title"] == "":
            data_info["title"] = current_file["title"]

        if bool(more_details) and "description" in more_details:
            data_info["description"] = more_details["description"]
            if data_info["description"] and data_info["description"] != "":
                quality["data_info"] = quality["data_info"] + 1

        if bool(more_details) and "modified" in more_details:
            if more_details["modified"] and more_details["modified"] != "":
                quality["data_info"] = quality["data_info"] + 1


        my_file = UploadFile.objects.get(code__exact=file_code)
        my_file.init_settings = {"columns":init_datatypes, "init_columns": init_columns, "all_stat": all_stat}
        #print(my_file.init_settings)

        #request.session["list_demofiles"][file_code]["init_settings"] = {"columns":init_datatypes}

        inc = 1
        for col, datatype in init_datatypes.items():
            id = request.session['project_code']+file_code+"c"+str(inc)
            if not more_details["fields"][col]["label"] and more_details["fields"][col]["label"] is None or more_details["fields"][col]["label"] == "":
                more_details["fields"][col]["label"] = col

            json_columns[col] = {"datatype": datatype, "id": id, "label": more_details["fields"][col]["label"], "description": more_details["fields"][col]["description"]}
            if more_details["fields"][col]["description"] and more_details["fields"][col]["description"] != "":
                quality["column_descriptions"] = quality["column_descriptions"] + 1
            if more_details["fields"][col]["label"] and more_details["fields"][col]["label"] != "" and more_details["fields"][col]["label"] != col:
                quality["column_labels"] = quality["column_labels"] + 1

            if "stat" in all_stat and col in all_stat["stat"]:
                nb_tot_values = nb_tot_values + all_stat["stat"][col]["nb_total"]
                quality["complete_data"] = quality["complete_data"] + (int(all_stat["stat"][col]["nb_total"]) - int(all_stat["stat"][col]["mis_val"]))
            inc += 1

        quality["data_info"] = round(float(quality["data_info"])*100.0/3.0, 2)
        quality["column_descriptions"] = round(float(quality["column_descriptions"])*100.0/float(inc-1), 2)
        quality["column_labels"] = round(float(quality["column_labels"])*100.0/float(inc-1), 2)
        quality["complete_data"] = round(float(quality["complete_data"])*100.0/float(nb_tot_values), 2)
        quality["average"] = round((settings.WEIGHT_DATA_INFO * float(quality["data_info"]) + settings.WEIGHT_COLUMN_DESCRIPTIONS * float(quality["column_descriptions"]) + settings.WEIGHT_COLUMN_LABELS * float(quality["column_labels"]) + settings.WEIGHT_COMPLETE_DATA * float(quality["complete_data"]))/float(settings.WEIGHT_COMPLETE_DATA + settings.WEIGHT_COLUMN_LABELS + settings.WEIGHT_COLUMN_DESCRIPTIONS + settings.WEIGHT_DATA_INFO), 2)

        my_file.more_details = more_details
        my_file.save(update_fields=['init_settings', 'more_details'])

        if bool(project_settings):
            previous_settings = copy.deepcopy(project_settings)
            project_history.append(previous_settings)
            current_state = len(project_history)

        if "files" not in project_settings:
            project_settings["files"] = {}

        if drop_dt != "" and drop_dt in project_settings["files"]:
            del project_settings["files"][drop_dt]

        project_settings["files"][file_code] = {"df_file_code":file_code,"columns":copy.deepcopy(json_columns),"all_stat":all_stat, "data_info": data_info, "quality":quality}
        project_settings["nb_dfs"] = nb_dfs + 1
        project_settings["state"] = current_state
        project_settings["insight"] = insight
        project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        project = Project.objects.get(code__exact=request.session['project_code'])
        project.project_settings = project_settings
        project.project_history = project_history
        project.save(update_fields=['project_settings','project_history'])
        my_file.related_projects.add(project.pk)
        #get current project
        load_full_project(request, Project, "current_project", 1)
        #get select files
        load_data(request, UploadFile, "list_selectedfiles", 1)

    nbfiles = len(request.session['file_codes'])
    data = {'is_valid': True, 'title': current_file["title"], 'file_link': current_file["file_link"],
    'code': current_file["code"], 'nbfiles': nbfiles, 'message': _('Action done successfully')}
    return data

#replace last occurence in string
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

#Aggregate dataset
def agg_dataset(request):
    data = {'is_valid': False, 'message': _('Something went wrong')}
    try:
        query = "SELECT "
        dt = request.POST.get('aggdata_dt')
        agg_cols = request.POST.get('h_aggdata_col').split("##")
        print(agg_cols)
        more_details = {}
        dtname = ""
        agg_dt = ""

        if request.POST.get('aggdata_dtname'):
            dtname = request.POST.get('aggdata_dtname')
        elif dt in request.session["list_selectedfiles"]:
            dtname = request.session["list_selectedfiles"][dt]["title"]
            agg_dt = dt

        if dt in request.session["list_selectedfiles"]:
            more_details = request.session["list_selectedfiles"][dt]["more_details"]

        load_data(request, DataType, "list_datatypes", 0)
        cols = []
        init_datatypes = {}
        init_columns = {}
        convert_dict = {}
        fields = {}

        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        database_name = settings.DATABASES['default']['NAME']
        host = settings.DATABASES['default']['HOST']
        port = settings.DATABASES['default']['PORT']
        database_uri  = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}'.format(
                user=user,
                password=password,
                database_name=database_name,
                host=host,
                port=port,
            )

        if dt in request.session["current_project"]["project_settings"]["files"]:
            myfile = request.session["current_project"]["project_settings"]["files"][str(dt)]
            graph_parameters = {"attribs": [], "data_filters": []}
            for aggkey in agg_cols:
                if aggkey and aggkey != '':
                    agg_key = request.session["all_agg_dict"][dt][aggkey]
                    graph_parameters["attribs"].append(agg_key)
                    key = agg_key["name"]
                    mycol = agg_key["col_full"]
                    if agg_key["type"] != "auto":
                        col = myfile["columns"][key]
                        init_datatypes[mycol] = col["datatype"]
                        init_columns[mycol] = request.session["list_selectedfiles"][dt]["init_settings"]["init_columns"][key]
                        convert_dict[mycol]=request.session["list_datatypes"][str(col["datatype"])]["pandas_name"]
                        my_current_field = request.session["list_selectedfiles"][dt]["more_details"]["fields"][key]
                        fields[mycol] = {"name": mycol, "label": agg_key["optionlabel"], "description": agg_key["description"], "online_type": my_current_field["online_type"]}
                    else:
                        init_datatypes[mycol] = int(settings.DATATYPE_INT)
                        current_datatype = request.session["list_datatypes"][settings.DATATYPE_INT]
                        init_columns[mycol] = current_datatype["pandas_name"]
                        convert_dict[mycol] = current_datatype["pandas_name"]
                        fields[mycol] = {"name": mycol, "label": "count", "description": "number of occurences", "online_type": current_datatype["abbreviation"]}

            agg_query = aggregate_query(request, graph_parameters, dt)
            query = agg_query["final_query"]

        print("query=============================================================")
        print(query)
        print("init_datatypes=============================================================")
        print(init_datatypes)
        print("init_datatypes=============================================================")
        print(init_columns)
        print("convert_dict=============================================================")
        print(convert_dict)

        new_file = UploadFile()
        new_file.title = dtname
        new_file.file_ext = settings.DEFAULT_FILE_SAVE
        new_file.from_query = True
        more_details["query"] = query
        more_details["fields"] = fields
        more_details["title"] = dtname
        more_details["dataset_id"] = ""

        final_cols = []
        for col1 in agg_cols:
            if col1 and col1 != "":
                final_cols.append(col1)

        desc1 = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["description"]
        tit1 = request.session["current_project"]["project_settings"]["files"][str(dt)]["data_info"]["title"]


        description = _("Aggregate dataset {} using columns: {} -- Description of {}: {}").format(tit1, ', '.join(final_cols), tit1, desc1)
        more_details["description"] = description

        new_file.more_details = more_details
        refresh_timeout = None
        if request.session["list_selectedfiles"][str(dt)]["refresh_timeout"]:
            refresh_timeout = request.session["list_selectedfiles"][str(dt)]["refresh_timeout"]
        new_file.refresh_timeout = refresh_timeout
        new_file.save()
        new_file.file_link = settings.MEDIA_URL[:-1] + settings.UPLOAD_FILES + new_file.code + ".csv"
        new_file.related_files.add(request.session["list_selectedfiles"][dt]["id"])
        new_file.save(update_fields=['file_link'])

        current_file = {"id":new_file.pk, "code":new_file.code, "file_link":new_file.file_link, "title":new_file.title, "file_ext":new_file.file_ext
        , "is_demo":new_file.is_demo, "refresh_timeout":new_file.refresh_timeout, "init_settings":new_file.init_settings, "updated_at":new_file.updated_at, "more_details": new_file.more_details}
        insight = _("Aggregate data and add new file #{}# to project").format(current_file["title"])

        #print("current_file=============================================================")
        #print(current_file)
        #print("=============================================================")

        engine = sqlalchemy.create_engine(database_uri, echo=False)
        if query is not None:
            df = pd.read_sql(sqlalchemy.text(query), con=engine)
            file_link = settings.BASE_DIR + current_file["file_link"]
            df.to_csv(file_link, encoding='utf-8', index=False)
            if bool(convert_dict):
            	df = df.astype(convert_dict)
            df_pkl = "df_" + current_file["code"]
            d6tstack.utils.pd_to_psql(df, database_uri, df_pkl, if_exists='replace', sep=';')
            data = add_df(request, df, init_datatypes, init_columns, current_file, insight, agg_dt)
    except Exception as e:
        print('Error details: '+ str(e))

    return data

#generate query from data
def aggregate_query(request, graph_parameters, file_code):
    # get the parameters
    data_operator = 'and'
    datakeep_operator = 'keep'

    data = {"final_query": None, "graph_parameters": None}
    current_project = request.session["current_project"]

    #try:
    #initialize variables to be returned
    df_pkl = "df_"+current_project["project_settings"]["files"][file_code]["df_file_code"]
    data_select = []
    data_where = []
    data_groupby = []
    data_having = []

    analysis_attrs = []
    analysis_where = []

    #features calculation
    col_num = []
    col_cat = []
    col_geo = []
    col_temp = []
    col_avg = []

    col_num_real = []
    col_cat_real = []
    col_geo_real = []
    col_temp_real = []

    # to manage bin columns
    before_select = ""
    after_from = ""
    list_bins = []
    order_by = []
    order_by_bins = []

    key_column = "vzm"+settings.VIZ_Y
    need_group_by = 0

    viztypemarks = ""

    for key, value in graph_parameters.items():
        if "vzm" in key:
            graph_parameters[key] = []
            continue
        if key == "data_filters" or key == "attribs":
            key2 = 0
            nb_num = 0
            for filt in value:
                if "dimmeasopt" not in filt:
                    filt["dimmeasopt"] = ""
                select_d = ""
                where_d = ""
                groupby_d = ""
                having_d = 0
                col = filt["name"]
                col_name = col
                graph_parameters[key][key2]["is_num"] = 0
                if (filt["type"] == "float64" or filt["type"] == "int64" or filt["realtype"] == "auto") and filt["dimmeasopt"] != "bins":
                    graph_parameters[key][key2]["is_num"] = 1
                    nb_num = nb_num + 1

                if filt["dimmeasopt"] in ['sum', 'avg', 'min', 'max'] or filt["realtype"] == "auto":
                    need_group_by = 1

                if key == "data_filters":
                    analysis_where.append(filt["fulltext"])
                if key == "attribs":
                    if filt["dimmeasopt"] == 'sum':
                        analysis_attrs.append(_("sum of ")+col)
                    elif filt["dimmeasopt"] == 'avg':
                        analysis_attrs.append(_("average of ")+col)
                    elif filt["dimmeasopt"] == 'min':
                        analysis_attrs.append(_("minimum of ")+col)
                    elif filt["dimmeasopt"] == 'max':
                        analysis_attrs.append(_("maximum of ")+col)
                    else:
                        analysis_attrs.append(filt["fulltext"])
                    graph_parameters[key][key2]["analysis"] = analysis_attrs[len(analysis_attrs)-1]

                if (filt["realtype"] == "date"):
                    where_d = "(TO_CHAR("+col+"::date,'"+settings.DATE_FORMAT[filt["dimmeasopt"]]+"'))::text"
                    groupby_d = where_d
                    if filt["dimmeasopt"] != "valexact":
                        col_name += "_" + filt["dimmeasopt"]
                    select_d = where_d + " as " + col_name
                elif (filt["dimmeasopt"] and filt["dimmeasopt"] == "bins" and int(filt["bins"])>0):
                    where_d = col
                    suffix_col = filt["dimmeasopt"]+str(filt["bins"])
                    col_name += "_" + suffix_col
                    if col_name not in list_bins:
                        list_bins.append(col_name)
                        groupby_d = col_name+"_bucket"
                        order_by_bins.append(groupby_d)
                        groupby_d = col_name+"_bucket, "+col_name
                    if before_select == "":
                        before_select += "with "
                    else:
                        before_select += ", "
                    before_select +=col_name+ "_stats as (select min("+col+") as "+col_name+"_min, max("+col+") as "+col_name+"_max, "
                    if filt["type"] == "int64":
                        before_select += " CEIL(((max("+col+") - min("+col+"))/"+str(float(filt["bins"]))+")::numeric) as "+col_name+"_marg "
                    elif filt["type"] == "float64":
                        calcul = "((max("+col+") - min("+col+"))/"+str(float(filt["bins"]))+")"
                        before_select += " CASE "
                        before_select += " WHEN ROUND("+calcul+"::numeric, 2) >= "+calcul+" THEN ROUND("+calcul+"::numeric, 2)::numeric "
                        before_select += " WHEN ROUND("+calcul+"::numeric, 2) < "+calcul+" THEN ROUND("+calcul+"::numeric, 2)::numeric + 0.01 "
                        #before_select += " ROUND("+calcul+"::numeric, 2) as "+col_name+"_marg "
                        before_select += " END " +col_name+"_marg "

                    before_select +=" from "+df_pkl+" ) "

                    after_from += ", "+col_name+ "_stats"
                    bucket_bins = int(filt["bins"]) - 1
                    #select_d = "width_bucket("+col+", "+col_name+"_min, "+col_name+"_max, "+str(bucket_bins)+")" + " as " + col_name+"_bucket"
                    select_d = " CASE "
                    for b in range(int(filt["bins"])):
                        born_inf = col_name + "_min + ("+str(b)+"*"+col_name+"_marg )"
                        born_sup = col_name + "_min + ("+str(b+1)+"*"+col_name+"_marg)"
                        if filt["type"] == "float64":
                            born_inf = "ROUND(("+born_inf+")::numeric,2)"
                            born_sup = "ROUND(("+born_sup+")::numeric,2)"
                        if b == bucket_bins:
                            select_d += " WHEN "+col+" >= ("+born_inf+") AND "+col+" <= ("+born_sup+") then ("+str(b)+")::numeric"
                        else:
                            select_d += " WHEN "+col+" >= ("+born_inf+") AND "+col+" < ("+born_sup+") then ("+str(b)+")::numeric"
                    select_d += " END " + col_name+ "_bucket"

                    select_d += ", CASE "
                    for b in range(int(filt["bins"])):
                        born_inf = col_name + "_min + ("+str(b)+"*"+col_name+"_marg )"
                        born_sup = col_name + "_min + ("+str(b+1)+"*"+col_name+"_marg)"
                        if filt["type"] == "float64":
                            born_inf = "ROUND(("+born_inf+")::numeric,2)"
                            born_sup = "ROUND(("+born_sup+")::numeric,2)"
                        if b == bucket_bins:
                            select_d += " WHEN "+col+" >= ("+born_inf+") AND "+col+" <= ("+born_sup+") then CONCAT('[',("+born_inf+")::text,',',("+born_sup+")::text,']')"
                        else:
                            select_d += " WHEN "+col+" >= ("+born_inf+") AND "+col+" < ("+born_sup+") then CONCAT('[',("+born_inf+")::text,',',("+born_sup+")::text,'[')"
                    select_d += " END " + col_name
                elif (filt["dimmeasopt"] and filt["dimmeasopt"] in ['sum', 'avg', 'min', 'max']):
                    where_d = filt["dimmeasopt"] + "("+col+")"
                    col_name += "_" + filt["dimmeasopt"]
                    select_d = "COALESCE(" + where_d + ", 0)" + " as " + col_name
                    having_d = 1
                elif (filt["realtype"] == "auto"):
                    where_d = "count(*)"
                    select_d = "COALESCE(" + where_d + ", 0)" + " as " + col_name
                    having_d = 1
                else:
                    where_d = col
                    col_name = col
                    select_d = where_d
                    groupby_d = col

                datatype = ""
                if filt["realtype"] == "auto":
                    datatype = settings.MEASURES_TYPES[0]
                else:
                    current_datatype = request.session["list_datatypes"][str(filt["dt"])]
                    datatype = current_datatype["parent"]

                if key == "attribs" :
                    viztypemarks += "vti-"+col_name+"__"+datatype+"__"+col_name+"__nb-"+col_name+"__or-"+col_name+"__"+filt["dimmeasopt"]+"__"+str(filt["dt"])+"**"

                if key == "attribs" and datatype == settings.MEASURES_TYPES[0]:
                    if "coalesce" in select_d.lower() and "avg(" in select_d.lower() and col_name not in col_avg:
                        col_avg.append(col_name)

                if key == "attribs":
                    graph_parameters[key][key2]["full_datatype"] = datatype
                    if datatype == settings.ALL_TYPES[0] and filt["dimmeasopt"] != "bins" and col_name not in col_num:
                        col_num.append(col_name)
                        col_num_real.append(col)
                    elif (datatype == settings.ALL_TYPES[3] or filt["dimmeasopt"] == "bins") and col_name not in col_cat:
                        col_cat.append(col_name)
                        col_cat_real.append(col)
                    elif datatype == settings.ALL_TYPES[2] and col_name not in col_geo:
                        col_geo.append(col_name)
                        col_geo_real.append(col)
                    elif datatype == settings.ALL_TYPES[1] and col_name not in col_temp:
                        col_temp.append(col_name)
                        col_temp_real.append(col)

                #if key == "attribs" and datatype == settings.ALL_TYPES[0] and ((filt["dimmeasopt"] and filt["dimmeasopt"] in ['sum', 'avg', 'min', 'max']) or filt["realtype"] == "auto"):
                #    order_by.append(col_name+" desc")
                if key == "attribs" and datatype == settings.ALL_TYPES[3]:
                    order_by.append(col_name+" asc")

                if "valuefilt" in filt and len(filt["valuefilt"]) > 0 and "optionfilt" in filt and len(filt["optionfilt"]) > 0:
                    filter_values = filt["valuefilt"].split("##")
                    filter_value1 = None
                    filter_value2 = None

                    if filter_values and len(filter_values)==1:
                        filter_value1 = filter_values[0]
                        if filt["type"] != "float64" and filt["type"] != "int64" and "contains" not in filt["optionfilt"]:
                            filter_value1 = "'"+filter_value1+"'"
                    elif filter_values and len(filter_values)==2:
                        filter_value1 = filter_values[0]
                        filter_value2 = filter_values[1]
                        if filt["type"] != "float64" and filt["type"] != "int64" and "contains" not in filt["optionfilt"]:
                            filter_value1 = "'"+filter_value1+"'"
                            filter_value2 = "'"+filter_value2+"'"

                    if filt["optionfilt"] == "set":
                        where_d += " is null "
                    elif filt["optionfilt"] == "notset":
                        where_d += " is not null "
                    elif filt["optionfilt"] == "istrue":
                        where_d += " is TRUE "
                    elif filt["optionfilt"] == "isfalse":
                        where_d += " is FALSE "
                    elif filt["optionfilt"] == "contains" and filter_value1 is not None:
                        where_d = " LOWER("+where_d+")" + " LIKE '%"+filter_value1+"%' "
                    if filt["optionfilt"] == "notcontains" and filter_value1 is not None:
                        where_d = " LOWER("+where_d+")" + " NOT LIKE '%"+filter_value1+"%' "
                    elif filt["optionfilt"] == "equalto" and filter_value1 is not None:
                        where_d += " = "+filter_value1
                    elif filt["optionfilt"] == "notequalto" and filter_value1 is not None:
                        where_d += " != "+filter_value1
                    elif filt["optionfilt"] == "greaterthan" and filter_value1 is not None:
                        where_d += " > "+filter_value1
                    elif filt["optionfilt"] == "lessthan" and filter_value1 is not None:
                        where_d += " < "+filter_value1
                    elif filt["optionfilt"] == "greaterequalthan" and filter_value1 is not None:
                        where_d += " >= "+filter_value1
                    elif filt["optionfilt"] == "lessequalthan" and filter_value1 is not None:
                        where_d += " <= "+filter_value1
                    elif filt["optionfilt"] == "isbetween" and filter_value1 is not None and filter_value2 is not None:
                        where_d = where_d + " >= " + filter_value1 + " and " + where_d + " <= " + filter_value2
                    elif filt["optionfilt"] == "in" and filter_values:
                        where_d += " IN ('" + "', '".join(filter_values) + "') "
                    elif filt["optionfilt"] == "notin" and filter_values:
                        where_d += " NOT IN ('" + "', '".join(filter_values) + "') "

                    where_d = "("+where_d+")"
                    if having_d == 0 and where_d not in data_where:
                        data_where.append(where_d)
                    if having_d == 1 and where_d not in data_having:
                        data_having.append(where_d)

                graph_parameters[key][key2]["col_name"] = col_name

                key2 = key2 + 1

                if select_d not in data_select and key == "attribs":
                    data_select.append(select_d)
                if groupby_d and groupby_d not in data_groupby and key == "attribs":
                    data_groupby.append(groupby_d)

            #if nb_num == key2 and key2 != 0:
            #    key_column = key

    #Create final query
    final_query = ""
    if len(data_select) == 0:
        return data
    else:
        if before_select != "":
            final_query += " "+ before_select

        final_query +=" SELECT " + ', '.join(data_select)
        final_query += " FROM "+ df_pkl+after_from
    if len(data_where) > 0:
        if data_operator == 'and':
            final_query +=" WHERE " + ' AND '.join(data_where)
        else:
            final_query +=" WHERE " + ' OR '.join(data_where)
    else:
        final_query +=" WHERE 1 = 1"

    if len(data_groupby) > 0 and need_group_by == 1:
        final_query +=" GROUP BY " + ', '.join(data_groupby)

    if len(order_by_bins) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by_bins)
    elif len(col_temp) > 0:
        final_query +=" ORDER BY " + ', '.join(col_temp)
    elif len(col_geo) == 0 and len(col_temp) == 0 and len(order_by) > 0 and len(col_cat) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by)


    if len(data_having) > 0:
        if data_operator == 'and':
            final_query +=" HAVING " + ' AND '.join(data_having)
        else:
            final_query +=" HAVING " + ' OR '.join(data_having)

    data = {"final_query": final_query, "final_graph_parameters": graph_parameters, "key_column": key_column,"analysis_attrs": analysis_attrs,
    "analysis_where": analysis_where, "need_group_by": need_group_by, "col_num":col_num, "col_cat":col_cat, "col_geo":col_geo, "col_temp":col_temp, "col_avg":col_avg,
    "data_select": data_select, "data_where": data_where, "data_groupby": data_groupby, "data_having": data_having, "viztypemarks": viztypemarks,
    "after_from": after_from, "before_select": before_select, "order_by": order_by, "order_by_bins": order_by_bins, "col_num_real":col_num_real, "col_cat_real":col_cat_real,
    "col_geo_real":col_geo_real, "col_temp_real":col_temp_real}
    #print("final_query=============================")
    #print(final_query)
    return data
