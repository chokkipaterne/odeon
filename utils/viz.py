from django.utils.translation import ugettext as _
from django.conf import settings
import numpy as np
import pandas as pd
import os, time
import json
import math
import decimal
import plotly.express as px
from plotly.offline import plot
import matplotlib, random
import plotly.graph_objects as go
import os.path
import datetime
from datetime import date
from visualizations.models import *
from django.core import serializers
from django.core.cache import cache
import copy
import io
import requests
import re
from django.template.defaulttags import register
from django.contrib import messages
#Import to save dataframe to table
import sqlalchemy
import d6tstack.utils
from django.db import connection
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from django.db.models import Q
import collections
import urllib.request
import ipinfo
from django.utils.text import slugify

with open(settings.COUNTRY_FR_JSON, encoding='utf-8') as f:
    data_fr = json.load(f)

#register a filter to get item from dictionary
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key).items()

#register a filter to get item from dictionary
@register.simple_tag
def get_project_type(key):
    if key in settings.PROJECT_TYPES:
        return _(settings.PROJECT_TYPES[key])
    else:
        return key

#register a filter to get item from dictionary
@register.simple_tag
def get_user_type(key):
    if key in settings.USER_REQUEST_TYPES:
        return _(settings.USER_REQUEST_TYPES[key])
    else:
        return key

@register.simple_tag
def get_utype(key):
    if key in settings.USER_TYPES:
        return _(settings.USER_TYPES[key])
    else:
        return key

#register hiracchical data from dictionnary
@register.filter
def get_from_dict(dictionary, key):
    hierachy_keys = key.split("#")
    rep = dictionary
    for hk in hierachy_keys:
        rep = dictionary[hk]
    return rep

#register a filter to get item from settings
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

#change link by html link
@register.filter
def deshtml(value):
    links = re.findall(r'(https?://[^\s]+)', value)
    for link in links:
        value = value.replace(link, "<a target='_blank' href='"+link+"'>"+link+"</a>")
    for isty in settings.ISSUE_TYPES:
        value = value.replace("#"+isty[0]+"#", "<b>"+_("Issue Type:")+"</b> "+_(isty[1]))

    for i in range(1, 6):
        value = value.replace("#"+str(i)+"#", "<div class='starrr"+str(i)+"'></div>")

    value = value.replace("#IMPREC#", "<b>"+_("Impacted Records:")+"</b> ")
    value = value.replace("#Data Provided#", "<b>"+_("#Data Provided#")+"</b> ")
    value = value.replace("#SUGG#", "<b>"+_("Suggestion for correction:")+"</b> ")
    value = value.replace("\n", "<br/>")
    return value

@register.filter
def generatelink(value):
    links = re.findall(r'(https?://[^\s]+)', value)
    for link in links:
        value = value.replace(link, "<a target='_blank' href='"+link+"'>"+link+"</a>")
    value = value.replace("\n", "<br/>")
    return value

@register.filter
def desfhtml(value):
    for isty in settings.ISSUE_TYPES:
        value = value.replace("#"+isty[0]+"#", _("Issue Type:")+" "+_(isty[1]))
    value = value.replace("#IMPREC#", _("Impacted Records:")+" ")
    value = value.replace("#Data Provided#", _("#Data Provided#")+" ")
    value = value.replace("#SUGG#", _("Suggestion for correction:")+" ")
    value = value.replace("\n", " - ")
    return value

@register.filter
def removehtml(raw_html):
    if not raw_html or raw_html == "":
        return raw_html
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

@register.filter
def getproject(dt):
    return dt.related_projects.all()[0].dash_code

@register.filter
def formatdate(dt):
    return dt.strftime("%d/%m/%Y")

@register.filter
def addslash(value):
    if value:
        value = value.replace("'", "##")
        value = value.replace("’", "##")
    return value

@register.filter
def show_steps(current_path):
    rep = "hide"
    if "get-started" in current_path or "visualization" in current_path:
        rep = ""
    return rep

@register.filter
def country_translate(country, lang):
    return translate_value(country, lang)

@register.filter
def slugifytext(text, key):
    if text == "":
        return text
    if key != "":
        text += " " + key
    slug_text = slugify(text)
    return slug_text

def translate_value(country, lang):
    if lang != settings.LANGUAGE_CODE:
        if country in data_fr.keys():
            country = data_fr[country]
    return country

@register.filter
def active_menu(current_path, step):
    rep = ""
    step = str(step)

    if "projects" in current_path and step == "1":
        rep = "mobile-bottom-nav__item--active"
    elif "topics" in current_path and step == "2":
        rep = "mobile-bottom-nav__item--active"
    elif "home-mobile" in current_path and step == "3":
        rep = "mobile-bottom-nav__item--active"
    elif "favorites" in current_path and step == "4" and "login" not in current_path:
        rep = "mobile-bottom-nav__item--active"
    elif ("login" in current_path or "register" in current_path) and step == "5":
        rep = "mobile-bottom-nav__item--active"
    return rep

@register.filter
def active_step(current_path, step):
    rep = ""
    step = str(step)

    if "get-started/" in current_path and step == "1":
        rep = "active"
    elif "get-started" in current_path and "get-started/" not in current_path and step == "2":
        rep = "active"
    elif "visualization/" in current_path and "visualization/get" not in current_path and step == "4":
        rep = "active"
    elif "visualization" in current_path and not ("visualization/" in current_path and "visualization/get" not in current_path) and step == "3":
        rep = "active"
    return rep

@register.filter
def active_moreopt(current_path):
    rep = "hide"
    if "visualization" in current_path and not ("visualization/" in current_path and "visualization/get" not in current_path):
        rep = ""
    return rep

@register.filter
def oppactive_moreopt(current_path):
    rep = ""
    if "visualization" in current_path and not ("visualization/" in current_path and "visualization/get" not in current_path):
        rep = "hide"
    return rep

#register a filter to get dashboard vizs
@register.filter
def dash_info(project, key):
    if "showhide" in key:
        print(key)
        arrkey = key.split("#")
        displaytype = arrkey[1]
        project_settings = project["project_settings"]

        if "shdsp_typ" not in project_settings:
            for k, v in settings.SETUP_DASH.items():
                project_settings[k] = v

        return {"shdsp_typ": project_settings["shdsp_typ"],"shfilt": project_settings["shfilt_"+displaytype], "shcstmen": project_settings["shcstmen_"+displaytype],
        "shvizdes": project_settings["shvizdes_"+displaytype], "shviztit": project_settings["shviztit_"+displaytype],
        "shvizmark": project_settings["shvizmark_"+displaytype], "shdtsource": project_settings["shdtsource_"+displaytype]}
    elif "vzshde" in key:
        arrkey = key.split("#")
        displaytype = arrkey[1]
        val_show = project["show_"+displaytype]
        return bool(val_show)
    elif key == "vizs":
        vizs = {}
        layout = 12
        if "dashboard" in project["project_settings"]:
            layout = int(project["project_settings"]["dashboard"]["layout"])

        if key not in project["project_settings"]:
            return vizs
        else:
            for key, viz in project["project_settings"]["vizs"].items():
                if viz["add_dash"] == 1:
                    file_code = viz["file_code"]
                    allinfo = ""
                    data_title = ""
                    if "dash_files" in project and file_code in project["dash_files"]:
                        file = project["dash_files"][file_code]
                        title = file["title"]
                        description = ""
                        if "more_details" in file and "title" in file["more_details"]:
                            title = file["more_details"]["title"]
                        title = '<a href="'+file["file_link"]+'"'+key+'>'+title+'</a>'
                        if "more_details" in file and "description" in file["more_details"]:
                            description = file["more_details"]["description"]

                        if "related_files" in file:
                            for key_related, related in file["related_files"].items():
                                title_related = related["title"]
                                if "more_details" in related and "title" in related["more_details"]:
                                    title_related = related["more_details"]["title"]
                                title_related = '<a href="'+file["file_link"]+'"'+key_related+'>'+title_related+'</a>'
                                if key_related in title:
                                    title.replace("#"+key_related+"#",title_related)

                        allinfo +="<b>"+_("Title: ")+"</b>"+title
                        data_title = title
                        if description != "":
                            allinfo +="<br/><b>"+_("Description: ")+"</b><br/>"+description
                        if description != "":
                            allinfo +="<br/><b>"+_("Description: ")+"</b><br/>"+description
                        allinfo +="<br/><b>"+_("Created At: ")+"</b>"+file["created_at"]
                        if "source" in file and file["source"] != "":
                            allinfo +="<br/><b>"+_("Source: ")+"</b>"+file["source"]

                    viz_encodings = ""
                    if "list_vizmarks" in project:
                        for key_graph, value_graph in viz["result"]["final_graph_parameters"].items():
                            if key_graph == "data_filters" or "vzm" in key_graph:
                                if len(value_graph) != 0:
                                    if viz_encodings != "":
                                        viz_encodings += "<br/>"
                                    if "vzm" in key_graph:
                                        mykey = key_graph.replace("vzm", "")
                                        viz_encodings += "<b>"+project["list_vizmarks"][mykey]["name"]+": "+"</b>"
                                    else:
                                        viz_encodings += "<b>"+"Initial Filters: "+"</b>"
                                    for viz_enc in value_graph:
                                        viz_encodings += "<a href='javascript:void(0)' class='chosen'>"+ viz_enc["fulltext"]+ "</a>, "
                                    viz_encodings = viz_encodings[:-2]
                    #if len(viz_encodings) > 0:
                    #    viz_encodings = viz_encodings[:-2]
                    vztype = ""
                    if "list_viztypes" in project:
                        vztype = project["list_viztypes"][str(viz["type_viz"])]["name"]

                    vizs[key] = {"plot_div": viz["plot_div"], "viz_notes": viz["viz_notes"], "layout": layout, "suffix": viz["suffix"], "file_code": viz["file_code"],
                    "viz_data": json.dumps(viz), "data_used": allinfo, "data_title": data_title, "viz_encodings": viz_encodings, "vztype": vztype, "show_nov": viz["show_nov"]
                    , "show_less": viz["show_less"], "show_adv": viz["show_adv"], "width": viz["width"], "height": viz["height"], "viz_final_title": viz["viz_final_title"]}

        return vizs.items()
    elif key == "shared":
        return bool(project["shared"])
    elif key == "dash_code" and "dash_code" in project:
        return project["dash_code"]
    elif key in settings.SETUP_DASH.keys():
        if key in project["project_settings"]:
            return project["project_settings"][key]
        else:
            return settings.SETUP_DASH[key]
    elif key == "code" and "code" in project:
        return project["code"]
    elif key == "allinfo":
        allinfo = ""
        if "dash_code" in project:
            allinfo +="<b>"+_("Code: ")+"</b>"+project["dash_code"]
        if "dash_code" in project:
            allinfo +="<br/><b>"+_("Last Modified: ")+"</b>"+project["updated_at"]
        allinfo += "<br/><hr/><b>"+_("Dataset Used: ")+"</b>"

        if "dash_files" in project:
            for key, file in project["dash_files"].items():
                title = file["title"]
                description = ""
                if "more_details" in file and "title" in file["more_details"]:
                    title = file["more_details"]["title"]
                title = '<a href="'+file["file_link"]+'"'+key+'>'+title+'</a>'
                if "more_details" in file and "description" in file["more_details"]:
                    description = file["more_details"]["description"]

                """if "related_files" in file:
                    for key_related, related in file["related_files"].items():
                        title_related = related["title"]
                        if "more_details" in related and "title" in related["more_details"]:
                            title_related = related["more_details"]["title"]
                        title_related = '<a href="'+file["file_link"]+'"'+key_related+'>'+title_related+'</a>'
                        if key_related in title:
                            title.replace("#"+key_related+"#",title_related)"""

                allinfo +="<br/><b>"+_("Title: ")+"</b>"+title
                if description != "":
                    allinfo +="<br/><b>"+_("Description: ")+"</b><br/>"+description
                #if description != "":
                #    allinfo +="<br/><b>"+_("Description: ")+"</b><br/>"+description
                allinfo +="<br/><b>"+_("Created At: ")+"</b>"+file["created_at"]
                if "source" in file and file["source"] != "":
                    allinfo +="<br/><b>"+_("Source: ")+"</b>"+file["source"]
                allinfo +="<div class='center' style='max-width:20%; height:5px; border-top:2px solid gray;'>&nbsp;</div>"

        return allinfo

        #return True
    else:
        if key == "layout":
            value = 12
        elif key == "filters":
            value = []
        else:
            value = ""

        if "dashboard" in project["project_settings"]:
            if key in project:
                value = project[key]
            elif key in project["project_settings"]:
                value = project["project_settings"][key]
            elif key in project["project_settings"]["dashboard"]:
                value = project["project_settings"]["dashboard"][key]
        return value

#Get delimiter of csv file
def detectDelimiter(header, can=False):
    if header.find(";") != -1:
        return ";"
    if header.find(",") != -1:
        return ","
    if can:
        return ""
    #default delimiter (MS Office export)
    return ";"

#test regex for geo point and geo shape
def geo_regex(df, col, type=0):
    result = False
    if df is None:
        return result
    reg_geo_point = "(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)"
    nb_rows = int(df.shape[0])
    nb_test = 0
    nbtotal_test = 0
    if type == 0 and df[col].dtype.name == "object": #geo_point
        for i in range(2):
            if nb_rows > i:
                nbtotal_test = nbtotal_test + 1
                val = df.at[i,col]
                val = val.lower()
                if re.search(reg_geo_point, val):
                    nb_test = nb_test + 1
        #print(col+"========="+str(nbtotal_test)+"========"+str(nb_test))
        if nb_test == nbtotal_test:
            result = True
    elif type == 1 and df[col].dtype.name == "object": # geo_shape
        for i in range(2):
            if nb_rows > i:
                nbtotal_test = nbtotal_test + 1
                val = df.at[i,col]
                val = val.lower()
                if re.search(reg_geo_point, val) and (re.search("type", val) or re.search("polygon", val) or re.search("coordinates", val)):
                    nb_test = nb_test + 1
        #print(col+"========="+str(nbtotal_test)+"========"+str(nb_test))
        if nb_test == nbtotal_test:
            result = True
    return result

#Get file name from link
def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    file_name = fname[0].replace('"', "")
    file_name = file_name.replace("'", "")
    return file_name

#get visitor address ip
def visitor_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

#Check if the link is downloadable
def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'zip' in content_type.lower():
        return False
    elif 'html' in content_type.lower():
        return False
    content_length = header.get('content-length', 0)
    content_length = int(content_length)
    if content_length and content_length > settings.MAX_UPLOAD_FILE:  # 200 mb approx
        return False
    return True

# load some useful data in session
def load_data(request, model, variable, reload=0, proj_type=''):
    if reload >= 1 or variable not in request.session:
        #print("refreshing "+variable+" ........")
        list_data = {}
        all_data = []
        if variable == "list_datatyperules":
            if request.user and request.user.id:
                all_data = model.objects.select_related('datatype').filter(Q(datatype__active__exact=True) & (Q(user_type__exact=settings.EXPERT) | Q(user__id=request.user.id) | Q(address_ip__exact=visitor_ip_address(request)))).order_by('-updated_at', '-created_at')
            else:
                all_data = model.objects.select_related('datatype').filter(Q(datatype__active__exact=True) & (Q(user_type__exact=settings.EXPERT) | Q(address_ip__exact=visitor_ip_address(request)))).order_by('-updated_at', '-created_at')
        elif variable == "list_viztypes":
            all_data = model.objects.filter(active__exact=True).order_by('sequence', 'name')
        elif variable == "list_vizmarks":
            all_data = model.objects.filter(active__exact=True).order_by('sequence', 'name')
        elif variable == "list_themes":
            all_data = model.objects.filter(active__exact=True).order_by('name', 'sequence')
        elif variable == "list_themes_mobile":
            all_data = model.objects.filter(active__exact=True).order_by('name', 'sequence_mobile')
        elif variable == "list_demofiles":
            if request.user and request.user.id:
                all_data = model.objects.filter((Q(is_demo__exact=True) | Q(user__id=request.user.id)), active__exact=True)
            else:
                all_data = model.objects.filter(is_demo__exact=True, active__exact=True)
        elif variable == "list_selectedfiles":
            if 'file_codes' in request.session and len(request.session['file_codes']) > 0:
                all_data = model.objects.filter(code__in=request.session['file_codes'])
        elif variable == "my_projects":
            if request.user and request.user.id:
                proj_filter = (Q(user__id=request.user.id) | Q(address_ip__exact=visitor_ip_address(request)))
            else:
                proj_filter = Q(address_ip__exact=visitor_ip_address(request))

            if proj_type == 'internal':
                proj_filter = proj_filter & Q(project_type__exact=proj_type)

            all_data = model.objects.filter(proj_filter).order_by('-updated_at', '-created_at')
        elif variable == "trans_projects":
            if request.user and request.user.is_superuser:
                proj_filter = Q(project_type__exact=proj_type)
            else:
                if request.user and request.user.id:
                    proj_filter = (Q(user__id=request.user.id) | Q(address_ip__exact=visitor_ip_address(request)))
                else:
                    proj_filter = Q(address_ip__exact=visitor_ip_address(request))
                proj_filter = proj_filter & Q(project_type__exact=proj_type)

            all_data = model.objects.filter(proj_filter).order_by('-updated_at', '-created_at')
            #list_data = []
        elif variable == "current_project":
            if 'project_code' in request.session:
                try:
                    data = model.objects.select_related('theme', 'status').get(code__exact=request.session['project_code'])
                except:
                    data = None
            if 'project_code' not in request.session or data is None:
                request.session[variable] = {}
                request.session['project_code'] = None
                request.session['file_codes'] = []
                return request.session[variable]
            if data:
                if variable not in request.session and 'file_codes' in request.session:
                    del request.session['file_codes']
                request.session[variable] = {"id":data.pk, "project_settings":data.project_settings,
                "project_history":data.project_history, "user":(data.user and data.user.username), "title":data.title, "notes":data.notes, "shared":data.shared, "code":data.code, "dash_code":data.dash_code,
                "updated_at": data.updated_at.strftime('%d/%m/%Y'), "project_type": data.project_type, "contact": data.contact, "image": (data.image and data.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": data.static_image,
                "theme": str(data.theme.pk), "link": data.link, "country": data.country, "state": data.state, "status": str(data.status.pk), "list_datasets": data.list_datasets}
                if data.project_type == 'internal':
                    request.session['show_vizmenu'] = True
                else:
                    request.session['show_vizmenu'] = False
                return request.session[variable]
        elif variable in ["list_datatypes"]:
            all_data = model.objects.filter(active__exact=True)
        elif variable in ["list_features"]:
            all_data = model.objects.filter(active__exact=True).order_by('sequence')
        elif variable in ["list_vizgoals"]:
            all_data = model.objects.filter(active__exact=True).order_by('name')
        elif variable in ["list_dataportals"]:
            all_data = model.objects.select_related('platform').filter(active__exact=True).order_by('name')
        elif variable in ["list_platformportals"]:
            all_data = model.objects.filter(active__exact=True).order_by('name')
        else:
            all_data = model.objects.all()
        try:
            print("Query====================================================================")
            print(all_data.query)
            print("Query====================================================================")
        except Exception as e:
            print('Error details: '+ str(e))

        for data in all_data:
            if variable == "list_datatypes":
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "icon":data.icon,
                "abbreviation":data.abbreviation, "pandas_name":data.pandas_name, "description":data.description,
                "parent":data.parent}
            elif variable == "list_features":
                is_num = 1
                if "?" in data.name:
                    is_num = 0
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "code":data.code,
                "formula":data.formula, "description":data.description, "is_num": is_num, "is_primary": data.is_primary, "apply_onlyto_viz": data.apply_onlyto_viz}
            elif variable == "list_datatyperules":
                list_data[str(data.pk)] = {"id":data.pk, "rule":data.rule, "datatype":data.datatype.pk,
                "user_type":data.user_type}
            elif variable == "list_viztypes":
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "description":data.description,
                "image":data.image.url, "include_marks":data.include_marks, "graph_function":data.graph_function}
            elif variable == "list_themes" or variable == "list_themes_mobile":
                #list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "description":data.description, "image":data.image.url}
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "image":data.image.url, "name_en": data.name_en}
            elif variable == "list_transthemes":
                if int(data.pk) not in settings.SKIP_THEMES:
                    list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "image":data.image.url, "name_en": data.name_en}
            elif variable == "list_vizgoals":
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "viz_types":data.viz_types}
            elif variable == "list_vizmarks":
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "description":data.description,
                "max_elements":data.max_elements, "is_orientation":data.is_orientation, "is_grouping":data.is_grouping}
            elif variable == "list_demofiles" or variable == "list_selectedfiles":
                has_tasks = 0
                if bool(data.init_settings) and "tasks" in data.init_settings and len(data.init_settings["tasks"])>0:
                    has_tasks = 1
                list_data[data.code] = {"id":data.pk, "code":data.code, "file_link":data.file_link, "title":data.title, "file_ext":data.file_ext
                , "is_demo":data.is_demo, "is_requested":data.is_requested, "has_tasks": has_tasks, "refresh_timeout":data.refresh_timeout, "init_settings":data.init_settings,
                "updated_at":data.updated_at, "more_details": data.more_details, "from_query": data.from_query, "full_title": data.title}

                if bool(data.more_details):
                    if "title" in data.more_details:
                        list_data[data.code]["full_title"] = data.more_details["title"]
                    if "description" in data.more_details:
                        list_data[data.code]["description"] = cleanhtml(data.more_details["description"])

                if (variable == "list_demofiles" or variable == "list_selectedfiles") and "current_project" in request.session:
                    current_project = request.session["current_project"]
                    if current_project and bool(current_project["project_settings"]):
                        if "files" in current_project["project_settings"]:
                            if data.code in current_project["project_settings"]["files"]:
                                if "data_info" in current_project["project_settings"]["files"][data.code]:
                                    list_data[data.code]["data_info"] = current_project["project_settings"]["files"][data.code]["data_info"]
                                    list_data[data.code]["full_title"] = current_project["project_settings"]["files"][data.code]["data_info"]["title"]
                                    list_data[data.code]["description"] = cleanhtml(current_project["project_settings"]["files"][data.code]["data_info"]["description"])
                                if "quality" in current_project["project_settings"]["files"][data.code]:
                                    list_data[data.code]["data_quality"] = current_project["project_settings"]["files"][data.code]["quality"]
                                    list_data[data.code]["quality"] = current_project["project_settings"]["files"][data.code]["quality"]["average"]

            elif variable == "my_projects" or variable == "my_projects_ip" or variable == "trans_projects":
                list_data[str(data.pk)] = {"id":data.pk, "code":data.code, "dash_code": data.dash_code, "image": (data.image and data.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": data.static_image,
                "notes":data.notes, "project_type":data.project_type, "title":data.title, "updated_at": (data.updated_at and data.updated_at.strftime("%d/%m/%Y")) or (data.created_at and data.created_at.strftime("%d/%m/%Y")) }
            elif variable == "list_dataportals":
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "more_details":data.more_details, "platform": data.platform.pk}
            elif variable == "list_platformportals":
                list_data[str(data.pk)] = {"id":data.pk, "name":data.name, "more_details":data.more_details}
        request.session[variable] = list_data

    return request.session[variable]

#Read csv pandas & Save dataframe in .pkl
#Need later to switch to HDF5
#https://stackoverflow.com/questions/17098654/how-to-store-a-dataframe-using-pandas
#convert file to dataframe
def convert_file_to_df(request, file_ext, file_link):
    df = None
    is_local = True
    if "http" in file_link:
        is_local = False
        if not is_downloadable(file_link):
            return df
        r = requests.get(file_link, allow_redirects=True)
        content = r.content
        if not content or content is None:
            return df
        file_link = io.StringIO(content.decode('utf-8'))
    else:
        file_link = settings.BASE_DIR+file_link

    if (file_ext).lower() == ".csv":
        if is_local:
            with open(file_link, 'r', encoding='utf-8') as myCsvfile:
                header=myCsvfile.readline()
            separator=detectDelimiter(header)
        else:
            for header in file_link.getvalue().split('\n'):
                separator=detectDelimiter(header)
                break
            #separator = ";"
        df = pd.read_csv(file_link, sep=separator, encoding='utf8')
    elif (file_ext).lower() == ".json":
        df = pd.read_json(file_link, encoding='utf8')
    elif (file_ext).lower() == ".xls" or (file_ext).lower() == ".xlsx":
        df = pd.read_excel(file_link, 0)

    init_labels = {}
    init_columns = []
    if df is not None:
        init_columns  = df.columns.tolist()
        df.columns = map(str.lower, df.columns)
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('(', '_')
        df.columns = df.columns.str.replace(')', '')
        #if (file_ext).lower() == ".csv" and separator != ";":
        #df = df.replace('\,', '-', regex=True)
        inc = 0
        for col in df.columns:
            init_labels[col] = init_columns[inc]
            inc = inc + 1
        df = df.replace({r'\s+$': '', r'^\s+': ''}, regex=True).replace(r'\n',  ' ', regex=True)
    return {"df": df, "init_labels":init_labels}

#check if need to reload file
def need_reload(request, file_code, df_file_code, refresh_timeout):
    if refresh_timeout is None:
        refresh_timeout = 0

    if refresh_timeout > 0:
        my_file = UploadFile.objects.get(code__exact=file_code)
        date_file = ""
        updated_at = my_file.updated_at
        diff = -9876
        if df_file_code in updated_at:
            date_file = updated_at[df_file_code]
            diff = time.time() - float(date_file)
        if abs(diff) >= refresh_timeout or diff == -9876:
            updated_at[df_file_code] = time.time()
            my_file.updated_at = updated_at
            my_file.save(update_fields=['updated_at'])
            return 1
    return 0

#hande year column
def handle_year(request, df, convert_dict):
    convert_keys = list(convert_dict.keys())
    convert_values = convert_dict.values()

    indices = [index for index, element in enumerate(convert_values) if "date" in element]

    if len(indices) > 0:
    	for index in indices:
            col_name = convert_keys[index]
            if int(df.shape[0]) > 0:
                val = df.at[0,col_name]
                if df[col_name].dtype.name == "int64" and val and len(str(val)) == 4:
                    df[col_name] = df[col_name].apply(lambda x: str(x)+"-01-01 00:00:00")
    df.astype(convert_dict)
    return df


#Save dataframe
def save_read_df(request, file_code, file_ext, file_link, refresh_timeout, df_file_code, reload=0, convert_dict={}, query=None):
    df = None
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
    #engine = sqlalchemy.create_engine(database_uri, echo=False)

    df_pkl = "df_"+df_file_code
    init_datatypes = {}
    init_columns = {}
    init_labels = {}
    if reload == 2:
        result_convert = convert_file_to_df(request, file_ext, file_link)
        df = result_convert["df"]
        init_labels = result_convert["init_labels"]

        if df is not None:
            result_init = get_init_datatype(request, df)
            init_datatypes = result_init["list_columns"]
            init_columns = result_init["init_columns"]
            convert_dict = get_convert_dict_from_columns(request, init_datatypes)
            if bool(convert_dict):
                df = handle_year(request, df, convert_dict)

            d6tstack.utils.pd_to_psql(df, database_uri, df_pkl, if_exists='replace', sep=';')
            need_reload(request, file_code, df_file_code, refresh_timeout)
    else:
        if reload == 0:
            reload = need_reload(request, file_code, df_file_code, refresh_timeout)
        if reload == 1:
            result_convert = convert_file_to_df(request, file_ext, file_link)
            df = result_convert["df"]
            init_labels = result_convert["init_labels"]
            if df is not None:
                if bool(convert_dict):
                    df = handle_year(request, df, convert_dict)
                d6tstack.utils.pd_to_psql(df, database_uri, df_pkl, if_exists='replace', sep=';')
                if query is not None:
                    engine = sqlalchemy.create_engine(database_uri, echo=False)
                    df = pd.read_sql(query, con=engine)
        else:
            engine = sqlalchemy.create_engine(database_uri, echo=False)
            if query is not None:
                df = pd.read_sql(sqlalchemy.text(query), con=engine)
            else:
                df = pd.read_sql_table(df_pkl,engine)
    return {"df":df, "init_datatypes":init_datatypes, "init_columns":init_columns, "init_labels": init_labels}


#update column datatype and create new df using old df
def update_column_from_df(request, df, new_df_file_code, convert_dict={}):
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
    df_new_pkl = "df_"+new_df_file_code
    if df is not None:
        if bool(convert_dict):
            df = handle_year(request, df, convert_dict)
        d6tstack.utils.pd_to_psql(df, database_uri, df_new_pkl, if_exists='replace', sep=';')
    return df

#get convert all columns datatype of each file of the current project
def get_convert_dict_from_project(request, files):
    load_data(request, DataType, "list_datatypes", 0)
    convert_dict={}
    real_convert_dict={}
    id_convert_dict={}
    dimensions={}
    measures={}
    all_options = []
    all_options_filters = []
    all_agg_dict={}
    all_col_dict = {}
    for key, value in files.items():
        convert_dict[key] = {}
        real_convert_dict[key] = {}
        id_convert_dict[key] = {}
        dimensions[key] = {}
        measures[key] = {}
        all_agg_dict[key] = {}
        all_col_dict[key] = {}
        if "columns" in value and bool(value["columns"]):
            columns = value["columns"]
            for keycol, col in columns.items():
                if col["label"] not in all_options_filters:
                    all_options_filters.append(col["label"])
                current_datatype = request.session["list_datatypes"][str(col["datatype"])]
                convert_dict[key][keycol] = current_datatype["pandas_name"]
                real_convert_dict[key][keycol] = current_datatype["name"]
                id_convert_dict[key][keycol] = col["datatype"]
                if current_datatype["parent"] in settings.MEASURES_TYPES:
                    measures[key][keycol] = {"id": col["id"], "dt_id": col["datatype"], "label": col["label"], "fulllabel": col["label"], "optionlabel": col["label"], "description": col["description"]
                    , "dt_pd": current_datatype["pandas_name"], "dt_abbr": current_datatype["abbreviation"]
                    , "dt_parent": current_datatype["parent"], "dt_icon": current_datatype["icon"]}
                    option = {
                        "id": col["id"], "ty": "meas", "dt": col["datatype"], "label": col["label"], "fulllabel": col["label"], "optionlabel": col["label"], "description": col["description"]
                        , "type": current_datatype["pandas_name"],
                        "realtype": current_datatype["abbreviation"], "name": keycol, "file": key, "fulltext": keycol,
                        "optionname": keycol, "col_full": keycol
                    }
                    #all_agg_dict[key][option["fulltext"]] = option
                    all_col_dict[key][keycol] = option
                    all_options.append(option)
                    #all_options_filters.append(option)
                    option_bins = copy.deepcopy(option)
                    option_bins["fulltext"] = option_bins["name"]+_("(bins:")+str(settings.DEFAULT_BINS)+")"
                    option_bins["optionname"] = option_bins["name"]+_(" cut into ")+str(settings.DEFAULT_BINS)+_(" intervals")

                    option_bins["fulllabel"] = option_bins["label"]+_("(bins:")+str(settings.DEFAULT_BINS)+")"
                    option_bins["optionlabel"] = option_bins["label"]+_(" cut into ")+str(settings.DEFAULT_BINS)+_(" intervals")

                    option_bins["bins"] = str(settings.DEFAULT_BINS)
                    option_bins["dimmeasopt"] = "bins"
                    all_options.append(option_bins)

                    for dimmeasopt in ['sum', 'avg', 'min', 'max']:
                        option_new = copy.deepcopy(option)
                        option_new["dimmeasopt"] = dimmeasopt
                        option_new["fulltext"] = option_new["name"]+"("+_(str(dimmeasopt))+")"
                        option_new["col_full"] = option_new["name"]+"_"+_(str(dimmeasopt))

                        option_new["fulllabel"] = option_new["label"]+"("+_(str(dimmeasopt))+")"
                        if dimmeasopt == 'sum':
                            option_new["optionname"] = _("sum of ") + option_new["name"]
                            option_new["optionlabel"] = _("sum of ") + option_new["label"]
                        elif dimmeasopt == 'avg':
                            option_new["optionname"] = _("average of ") + option_new["name"]
                            option_new["optionlabel"] = _("average of ") + option_new["label"]
                        elif dimmeasopt == 'min':
                            option_new["optionname"] = _("minimum of ") + option_new["name"]
                            option_new["optionlabel"] = _("minimum of ") + option_new["label"]
                        elif dimmeasopt == 'max':
                            option_new["optionname"] = _("maximum of ") + option_new["name"]
                            option_new["optionlabel"] = _("maximum of ") + option_new["label"]
                        all_options.append(option_new)
                        all_agg_dict[key][option_new["fulltext"]] = option_new
                        #all_options_filters.append(option_new)
                else:
                    dimensions[key][keycol] = {"id": col["id"], "dt_id": col["datatype"], "label": col["label"], "fulllabel": col["label"], "optionlabel": col["label"], "description": col["description"]
                    , "dt_pd": current_datatype["pandas_name"], "dt_abbr": current_datatype["abbreviation"]
                    , "dt_parent": current_datatype["parent"], "dt_icon": current_datatype["icon"]}
                    option = {
                        "id": col["id"], "ty": "meas", "dt": col["datatype"], "label": col["label"], "fulllabel": col["label"], "optionlabel": col["label"], "description": col["description"], "type": current_datatype["pandas_name"],
                        "realtype": current_datatype["abbreviation"], "name": keycol, "file": key, "fulltext": keycol,
                        "optionname": keycol, "col_full": keycol
                    }
                    all_options.append(option)
                    all_col_dict[key][keycol] = option
                    all_agg_dict[key][option["fulltext"]] = option
                    #if current_datatype["abbreviation"] not in ["lat", "lon", "shape"]:
                    #    all_options_filters.append(option)
                    if current_datatype["abbreviation"] in ["date"]:
                        for dimmeasopt in ['y', 'ym', 'ymd', 'hi']:
                            option_new = copy.deepcopy(option)
                            option_new["dimmeasopt"] = dimmeasopt
                            option_new["fulltext"] = option_new["name"]+"("+_(str(dimmeasopt))+")"
                            option_new["col_full"] = option_new["name"]+"_"+_(str(dimmeasopt))

                            option_new["fulllabel"] = option_new["label"]+"("+_(str(dimmeasopt))+")"

                            if dimmeasopt == 'y':
                                option_new["optionname"] = _("year of ") + option_new["name"]
                                option_new["optionlabel"] = _("year of ") + option_new["label"]
                            elif dimmeasopt == 'ym':
                                option_new["optionname"] = _("year-month of ") + option_new["name"]
                                option_new["optionlabel"] = _("year-month of ") + option_new["label"]
                            elif dimmeasopt == 'ymd':
                                option_new["optionname"] = _("year-month-day of ") + option_new["name"]
                                option_new["optionlabel"] = _("year-month-day of ") + option_new["label"]
                            elif dimmeasopt == 'hi':
                                option_new["optionname"] = _("hour-minute of ") + option_new["name"]
                                option_new["optionlabel"] = _("hour-minute of ") + option_new["label"]
                            all_options.append(option_new)
                            all_agg_dict[key][option_new["fulltext"]] = option_new
                            #all_options_filters.append(option_new)

            measures[key]["count"] = {"id": key+"c0", "dt_id": "0", "label": "number of occurences", "fulllabel": "number of occurences",
            "optionlabel": "number of occurences", "description": "number of occurences", "dt_pd": "auto", "dt_abbr": "auto"
            , "dt_parent": settings.MEASURES_TYPES[0], "dt_icon": settings.ICON_NUM}
            option = {
                "id": key+"c0", "ty": "meas", "dt": "0", "type": "auto",
                "realtype": "auto", "name": "count", "file": key, "fulltext": "count",
                "optionname": "count", "col_full": "count", "label": "number of occurences", "fulllabel": "number of occurences", "optionlabel": "number of occurences", "description": "number of occurences"
            }
            all_options.append(option)
            all_agg_dict[key][option["fulltext"]] = option
    all_options_filters.append("number of occurences")
    request.session["convert_dict"] = convert_dict
    request.session["real_convert_dict"] = real_convert_dict
    request.session["id_convert_dict"] = id_convert_dict
    request.session["dimensions"] = dimensions
    request.session["measures"] = measures
    request.session["all_options"] = all_options
    request.session["all_options_filters"] = all_options_filters
    request.session["all_agg_dict"] = all_agg_dict
    request.session["all_col_dict"] = all_col_dict
    return convert_dict

#get convert all file codes of current project
def get_file_codes_from_project(request, files):
    file_codes = []
    if bool(files):
        file_codes = list(files.keys())
    request.session["file_codes"] = file_codes
    return file_codes

#get pandas datatype from columns
def get_convert_dict_from_columns(request, columns):
    load_data(request, DataType, "list_datatypes", 0)
    convert_dict={}
    for keycol, col in columns.items():
        convert_dict[keycol]=request.session["list_datatypes"][str(col)]["pandas_name"]
    return convert_dict

#load current project
def load_full_project(request, model, variable, reload=0):
    load_data(request, model, variable, reload)
    if (reload >= 1 or 'file_codes' not in request.session) and "project_settings" in request.session["current_project"] and "files" in request.session["current_project"]["project_settings"]:
        files = request.session["current_project"]["project_settings"]["files"]
        get_file_codes_from_project(request, files)
        get_convert_dict_from_project(request, files)

    if 'file_codes' not in request.session:
        request.session["file_codes"] = []

#retrieve datatype based on rules defined by experts and other users
def get_datatype_from_rules(request, df, col):
    datatype = None
    rules = load_data(request, DataTypeRule, "list_datatyperules", 0)
    df_notnull = df.dropna(subset=[col])
    df_notnull = df_notnull.reset_index()
    for key, rule in rules.items():
        result = False
        expr = rule["rule"]
        codeBlock = str(expr)
        compiledCodeBlock = compile(codeBlock, '<string>', 'single')
        loc = {'result': result, "df":df, "col":col, "settings":settings, 'df_notnull':df_notnull, 'geo_regex':geo_regex}
        try:
            exec(compiledCodeBlock, {}, loc)
            result = loc["result"]
        except Exception as e:
            print('Error details: '+ str(e))

        #print("===========================================")
        #print(expr)
        #print(result)
        #print("===========================================")
        if result == True:
            datatype = rule["datatype"]
            break
    return datatype

#get all datatype of columns
def get_init_datatype(request, df):
    list_columns = {}
    init_columns = {}
    load_data(request, DataTypeRule, "list_datatyperules", 1)
    for col in df.columns:
        init_columns[col] = df[col].dtype.name
        datatype = get_datatype_from_rules(request, df, col)
        if datatype is None:
            datatype = settings.DEFAULT_DATATYPE
        list_columns[col] = datatype
    return {"list_columns":list_columns, "init_columns":init_columns}

#get full statistic data about all the columns
def get_stat_df(request, df, init_datatypes, init=1):
    nunique = df.nunique()
    mis_val = df.isnull().sum()
    corr = {}
    stat = {}
    nb_total = int(df.shape[0])
    load_data(request, DataType, "list_datatypes", 0)

    list_cat = []
    list_temp = []
    list_geo = []
    list_num = []

    comp_cat = []
    comp_temp = []
    comp_geo = []
    comp_num = []

    col_temp = {}
    col_geo = {}
    col_num = {}
    col_cat = {}

    keys_num = []
    for keycol, col in init_datatypes.items():
        if init == 0:
            current_datatype = request.session["list_datatypes"][str(col["datatype"])]
        else:
            current_datatype = request.session["list_datatypes"][str(col)]
        datatype = current_datatype["parent"]
        if datatype == settings.ALL_TYPES[0]:
            keys_num.append(keycol)


    if len(keys_num) > 0:
        df_num = df[keys_num]
        corr = df_num.corr()
        corr = corr.fillna(0)

    for keycol, col in init_datatypes.items():
        stat[keycol] = {}
        stat[keycol]["nb_distinct"] = int(nunique[keycol])
        stat[keycol]["nb_total"] = nb_total
        stat[keycol]["mis_val"] = int(mis_val[keycol])
        stat[keycol]["percent_distinct"] = 0
        if int(stat[keycol]["nb_total"]-stat[keycol]["mis_val"]) != 0:
            stat[keycol]["percent_distinct"] = float(nunique[keycol])/float(stat[keycol]["nb_total"]-stat[keycol]["mis_val"])
        if keycol in corr:
            tot_corr = 0.0
            nb_corr = 0
            stat[keycol]["corr"] = {}
            for col2, val in corr[keycol].items():
                if col2 != keycol:
                    stat[keycol]["corr"][col2] = abs(val)
                    if abs(val) >= settings.GOOD_CORR:
                        nb_corr = nb_corr + 1
                    tot_corr = tot_corr + abs(val)
            stat[keycol]["corr"]["tot_corr"] = tot_corr
            stat[keycol]["corr"]["nb_corr"] = int(nb_corr)
        if init == 0:
            current_datatype = request.session["list_datatypes"][str(col["datatype"])]
        else:
            current_datatype = request.session["list_datatypes"][str(col)]
        datatype = current_datatype["parent"]
        if datatype == settings.ALL_TYPES[0]:
            list_num.append(keycol)
            comp_num.append(stat[keycol]["corr"]["nb_corr"])
        elif datatype == settings.ALL_TYPES[3]:
            list_cat.append(keycol)
            comp_cat.append(stat[keycol]["percent_distinct"])
        elif datatype == settings.ALL_TYPES[2]:
            list_geo.append(keycol)
            comp_geo.append(stat[keycol]["percent_distinct"])
        elif datatype == settings.ALL_TYPES[1] :
            list_temp.append(keycol)
            comp_temp.append(stat[keycol]["percent_distinct"])

    if len(list_temp) > 0:
        array = np.array(comp_temp)
        tmp = array.argsort()
        ranks = np.empty_like(tmp)
        ranks[tmp] = np.arange(len(array))
        ic = 0
        for k in list_temp:
            stat[k]["order"] = int(ranks[ic])
            col_temp[str(ranks[ic])] = k
            ic += 1

    if len(list_geo) > 0:
        array = np.array(comp_geo)
        tmp = array.argsort()
        ranks = np.empty_like(tmp)
        ranks[tmp] = np.arange(len(array))
        ic = 0
        for k in list_geo:
            stat[k]["order"] = int(ranks[ic])
            col_geo[str(ranks[ic])] = k
            ic += 1

    if len(list_cat) > 0:
        array = np.array(comp_cat)
        tmp = array.argsort()
        ranks = np.empty_like(tmp)
        ranks[tmp] = np.arange(len(array))
        ic = 0
        for k in list_cat:
            stat[k]["order"] = int(ranks[ic])
            col_cat[str(ranks[ic])] = k
            ic += 1

    if len(list_num) > 0:
        array = np.array(comp_num)
        tmp = array.argsort()
        ranks = np.empty_like(tmp)
        ranks[tmp] = np.arange(len(array))
        ic = 0
        for k in list_num:
            stat[k]["order"] = int(ranks[ic])
            col_num[str(ranks[ic])] = k
            ic += 1
    all_stat = {"stat":stat, "col_num": col_num, "col_temp": col_temp, "col_geo": col_geo, "col_cat": col_cat}
    #print(all_stat)
    #all_stat = {"stat":stat, "col_num": col_num, "col_temp": col_temp, "col_geo": col_geo, "col_cat": col_cat}
    return all_stat

#Add file to project
def add_file(request, current_file, insight=""):
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

        # set columns info
        if "is_requested" in current_file and current_file["is_requested"]:
            data_info = {"title": current_file["more_details"]["title"],"description": current_file["more_details"]["description"]}
        elif bool(current_file["init_settings"]) and "columns" in current_file["init_settings"]:
            if "more_details" in current_file and "title" in current_file["more_details"]:
                data_info["title"] = current_file["more_details"]["title"]
                if data_info["title"] and data_info["title"] != "":
                    quality["data_info"] = quality["data_info"] + 1

            if not data_info["title"] or data_info["title"] is None or data_info["title"] == "":
                data_info["title"] = current_file["title"]

            if "more_details" in current_file and "description" in current_file["more_details"]:
                data_info["description"] = current_file["more_details"]["description"]
                if data_info["description"] and data_info["description"] != "":
                    quality["data_info"] = quality["data_info"] + 1

            if "more_details" in current_file and "modified" in current_file["more_details"]:
                if current_file["more_details"]["modified"] and current_file["more_details"]["modified"] != "":
                    quality["data_info"] = quality["data_info"] + 1

            inc = 1
            for col, datatype in current_file["init_settings"]["columns"].items():
                id = request.session['project_code']+file_code+"c"+str(inc)
                col_desc = ""
                col_label = ""
                if "more_details" in current_file and "fields" in current_file["more_details"]:
                    if col in current_file["more_details"]["fields"]:
                        if "description" in current_file["more_details"]["fields"][col]:
                            col_desc = current_file["more_details"]["fields"][col]["description"]
                        if "label" in current_file["more_details"]["fields"][col]:
                            col_label = current_file["more_details"]["fields"][col]["label"]

                    if not col_label or col_label is None or col_label == "":
                        col_label = col

                json_columns[col] = {"datatype": datatype, "id": id, "label": col_label, "description": col_desc}
                if col_desc and col_desc != "":
                    quality["column_descriptions"] = quality["column_descriptions"] + 1
                if col_label and col_label != "" and col_label != col:
                    quality["column_labels"] = quality["column_labels"] + 1
                if "all_stat" in current_file["init_settings"]:
                    if "stat" in current_file["init_settings"]["all_stat"] and col in current_file["init_settings"]["all_stat"]["stat"]:
                        nb_tot_values = nb_tot_values + current_file["init_settings"]["all_stat"]["stat"][col]["nb_total"]
                        quality["complete_data"] = quality["complete_data"] + (int(current_file["init_settings"]["all_stat"]["stat"][col]["nb_total"]) - int(current_file["init_settings"]["all_stat"]["stat"][col]["mis_val"]))
                inc += 1
            if "all_stat" in current_file["init_settings"]:
                all_stat = copy.deepcopy(current_file["init_settings"]["all_stat"])

            quality["data_info"] = round(float(quality["data_info"])*100.0/3.0, 2)
            quality["column_descriptions"] = round(float(quality["column_descriptions"])*100.0/float(inc-1), 2)
            quality["column_labels"] = round(float(quality["column_labels"])*100.0/float(inc-1), 2)
            quality["complete_data"] = round(float(quality["complete_data"])*100.0/float(nb_tot_values), 2)
            quality["average"] = round((settings.WEIGHT_DATA_INFO * float(quality["data_info"]) + settings.WEIGHT_COLUMN_DESCRIPTIONS * float(quality["column_descriptions"]) + settings.WEIGHT_COLUMN_LABELS * float(quality["column_labels"]) + settings.WEIGHT_COMPLETE_DATA * float(quality["complete_data"]))/float(settings.WEIGHT_COMPLETE_DATA + settings.WEIGHT_COLUMN_LABELS + settings.WEIGHT_COLUMN_DESCRIPTIONS + settings.WEIGHT_DATA_INFO), 2)
        else:
            try:
                result_df = save_read_df(request, file_code, current_file["file_ext"], current_file["file_link"], current_file["refresh_timeout"], current_file["code"], 2)
            except Exception as e:
                print('Error details: '+ str(e))
                return data
            df = result_df["df"]
            if df is None:
                return {'is_valid': False, 'message': _('Unable to load the file')}

            init_datatypes = result_df["init_datatypes"]
            init_columns = result_df["init_columns"]
            init_labels = result_df["init_labels"]

            all_stat = get_stat_df(request, df, init_datatypes)

            my_file = UploadFile.objects.get(code__exact=file_code)
            my_file.init_settings = {"columns":init_datatypes, "init_columns": init_columns, "all_stat": all_stat}
            more_details = {}
            if bool(current_file["more_details"]):
                more_details = current_file["more_details"]
            inc = 1
            load_data(request, DataType, "list_datatypes", 0)
            init_check = 0
            if bool(more_details) and "fields" in more_details and not bool(more_details["fields"]):
                init_check = 1

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


            for col, datatype in init_datatypes.items():
                if init_check == 1:
                    current_datatype = request.session["list_datatypes"][str(datatype)]["abbreviation"]
                    label = ""
                    if bool(init_labels) and col in init_labels:
                        if init_labels[col] != col:
                            label = init_labels[col]
                    if not label or label is None or label == "":
                        label = col
                    more_details["fields"][col] = {"name": col, "description": "", "label": label, "online_type": current_datatype}

                if not more_details["fields"][col]["label"] and more_details["fields"][col]["label"] is None or more_details["fields"][col]["label"] == "":
                    more_details["fields"][col]["label"] = col

                id = request.session['project_code']+file_code+"c"+str(inc)
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
        project_settings["files"][file_code] = {"df_file_code":file_code,"columns":copy.deepcopy(json_columns),"all_stat":all_stat, "data_info": data_info, "quality":quality}
        project_settings["nb_dfs"] = nb_dfs + 1
        project_settings["state"] = current_state
        project_settings["insight"] = insight
        project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        project = Project.objects.get(code__exact=request.session['project_code'])
        project.project_settings = project_settings
        project.project_history = project_history
        project.save(update_fields=['project_settings','project_history'])
        my_file = UploadFile.objects.get(code__exact=file_code)
        my_file.related_projects.add(project.pk)
        #get current project
        load_full_project(request, Project, "current_project", 1)
        #get select files
        load_data(request, UploadFile, "list_selectedfiles", 1)

    nbfiles = len(request.session['file_codes'])

    full_title = current_file["title"]
    if "title" in data_info and data_info["title"] != "":
        full_title = data_info["title"]

    data = {'is_valid': True, 'title': current_file["title"], 'file_link': current_file["file_link"],
    'code': current_file["code"], 'nbfiles': nbfiles, 'message': _('Added successfully'), 'full_title': full_title, 'quality': quality['average']}
    return data

#remove file from project
def remove_file(request, file_code, insight=""):
    data = {'deleted': False, 'message': _('Something went wrong')}
    if file_code:
        current_project = request.session["current_project"]
        if not current_project:
            return data
        project_history = []
        project_settings = {}
        current_state = 0

        if bool(current_project["project_settings"]):
            project_history = copy.deepcopy(current_project["project_history"])
            project_settings = copy.deepcopy(current_project["project_settings"])

        if bool(project_settings):
            previous_settings = copy.deepcopy(project_settings)
            project_history.append(previous_settings)
            current_state = len(project_history)

        if "files" not in project_settings:
            project_settings["files"] = {}
        if file_code in project_settings["files"]:
            del project_settings["files"][file_code]

        project_settings["state"] = current_state
        project_settings["insight"] = insight
        project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        project = Project.objects.get(code__exact=request.session['project_code'])
        project.project_settings = project_settings
        project.project_history = project_history
        project.save(update_fields=['project_settings','project_history'])
        my_file = UploadFile.objects.get(code__exact=file_code)
        my_file.related_projects.remove(project.pk)
        #get current project
        load_full_project(request, Project, "current_project", 1)
        #get select files
        load_data(request, UploadFile, "list_selectedfiles", 1)

    nbfiles = len(request.session['file_codes'])
    data = {'deleted': True, 'code': file_code, 'message':_('Deleted successfully'),  'nbfiles': nbfiles}
    return data


#Update column datatype
def update_column(request, old_df, file_code, column_data, type_data, insight=""):
    df = None
    if file_code not in request.session["list_selectedfiles"]:
        return df

    current_file = request.session["list_selectedfiles"][file_code]
    if current_file:
        current_project = request.session["current_project"]
        if not current_project:
            return data
        project_history = []
        project_settings = {}
        nb_dfs = 0
        json_columns = {}
        current_state = 0

        if bool(current_project["project_settings"]):
            project_history = copy.deepcopy(current_project["project_history"])
            project_settings = copy.deepcopy(current_project["project_settings"])
            nb_dfs = project_settings["nb_dfs"]

        new_df_file_code = request.session["project_code"]+"d"+str(nb_dfs+1)
        #old_datatype = DataType.objects.get(pk=int(request.session["id_convert_dict"][file_code][column_data]))
        old_datatype_name = current_file["init_settings"]["init_columns"][column_data]
        new_datatype = DataType.objects.get(pk=int(type_data))
        request.session["convert_dict"][file_code][column_data] = request.session["list_datatypes"][str(type_data)]["pandas_name"]

        df = update_column_from_df(request, old_df, new_df_file_code, request.session["convert_dict"][file_code])

        if df is None:
            return df

        #Create new datatype rules : 1) correct datatype & 2) opposite datatype
        new_datatype_rule = DataTypeRule()
        new_datatype_rule.user_type = request.session["current_user_type"]
        new_datatype_rule.datatype = new_datatype
        rule = settings.NEW_DATATYPE_RULE
        rule = rule.replace("datatype_name", old_datatype_name)
        rule = rule.replace("column_name", column_data)
        new_datatype_rule.rule = rule
        num_results = DataTypeRule.objects.filter(rule = rule).count()
        new_datatype_rule.address_ip = visitor_ip_address(request)
        if request.user and request.user.id:
            new_datatype_rule.user_id = request.user.id

        if num_results == 0:
            new_datatype_rule.save()
            #opposite datatype
            #op_datatype_rule = DataTypeRule()
            #op_datatype_rule.user_type = request.session["current_user_type"]
            #op_datatype_rule.datatype = old_datatype
            #rule = settings.OPPOSITE_DATATYPE_RULE
            #rule = rule.replace("datatype_name", old_datatype.pandas_name)
            #rule = rule.replace("column_name", column_data)
            #op_datatype_rule.rule = rule
            #op_datatype_rule.save()

        if bool(project_settings):
            previous_settings = copy.deepcopy(project_settings)
            project_history.append(previous_settings)
            current_state = len(project_history)

        if "files" not in project_settings:
            project_settings["files"] = {}
        project_settings["files"][file_code]["df_file_code"] = new_df_file_code
        project_settings["files"][file_code]["columns"][column_data]["datatype"] = int(type_data)
        project_settings["nb_dfs"] = nb_dfs + 1
        project_settings["state"] = current_state
        project_settings["insight"] = insight
        project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        all_stat = get_stat_df(request, df, project_settings["files"][file_code]["columns"], 0)
        project_settings["files"][file_code]["all_stat"] = all_stat

        project = Project.objects.get(code__exact=request.session['project_code'])
        project.project_settings = project_settings
        project.project_history = project_history
        project.save(update_fields=['project_settings','project_history'])
        #get current project
        load_full_project(request, Project, "current_project", 1)
        #get select files
        #load_data(request, UploadFile, "list_selectedfiles", 1)
    return df


#Summary of missing values in df
def missing_values_table(df, keys, values):
    df = df[keys]
    mis_val = df.isnull().sum()
    my_columns = df.columns
    mis_val_percent = 100 * df.isnull().sum() / len(df)
    mz_table = pd.concat([mis_val, mis_val_percent], axis=1)
    mz_table = mz_table.rename(columns = {0 : _('Missing Values'), 1 : _('% of Missing Values')})
    mz_table[_('Data Type')] = values
    mz_table = mz_table.reset_index()
    return mz_table

#Check if user uploads some files(if not return user to upload data page)
def check_files(request):
    file_codes = []
    if 'file_codes' in request.session:
        file_codes = request.session['file_codes']
    if len(file_codes) <= 0:
        messages.warning(request, _("Please first upload data"))
    return file_codes


#retrieve the unique values of specificed column from df
def retrieve_unique_values(request,file_code, column, df=None):
    unique_values = []
    if "unique_values" in request.session and file_code in request.session["unique_values"] and column in request.session["unique_values"][file_code]:
        return request.session["unique_values"][file_code][column]
    else:
        current_project = request.session["current_project"]
        if not current_project:
            return []
        if df is None:
            result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
            request.session["list_selectedfiles"][file_code]["file_link"], request.session["list_selectedfiles"][file_code]["refresh_timeout"],
            current_project["project_settings"]["files"][file_code]["df_file_code"], 0, request.session["convert_dict"][file_code])
            df = result_df["df"]

        if df is None:
            return []
        if "unique_values" not in request.session:
            request.session["unique_values"] = {}
        if file_code not in request.session["unique_values"]:
            request.session["unique_values"][file_code] = {}

        df_notnull = df.dropna(subset=[column])
        unique_values = df_notnull[column].unique().tolist()
        request.session["unique_values"][file_code][column] = unique_values
    return unique_values

#retrieve the list of previous actions
def retrieve_action_traceability(request):
    results = []
    state = -1
    current_project = request.session["current_project"]
    if not current_project:
        return []

    if "action_traceability" in request.session and request.session["action_traceability"] and request.session["action_traceability"] is not None:
        return request.session["action_traceability"]

    if 'project_history' in request.session["current_project"]:
        project_history = request.session["current_project"]["project_history"]
        nb_tracks = len(project_history)
        if nb_tracks > 0:
            for act in project_history:
                results.append({"date": act["date"], "state": act["state"], "insight": act["insight"]})
                if state < act["state"]:
                    state = act["state"]
    if 'project_settings' in request.session["current_project"]:
        act = request.session["current_project"]["project_settings"]
        if act["state"] > state:
            results.append({"date": act["date"], "state": act["state"], "insight": act["insight"]})

    request.session["action_traceability"] = results
    return results

#Create table based on data
def create_table(df, view_file=False, start=None, nbrows=None, is_corr=2, show_all=False):
    column_values = []
    nbcolumns = len(df.columns)
    top_text = ""
    if is_corr == 1:
        top_text = "<p><b>"+_("Correlation Information")+ "</b></p>"
    elif is_corr == 0:
        top_text = "<p><b>"+_("Data Type Information")+ "</b></p>"
    elif not show_all:
        top_text = "<p><b>"+_("Data contains ") + str(df.shape[1]) + _(" columns and ") + str(df.shape[0]) + _(" Rows.\n")+ "</b></p>"

    if start is None:
        start = 0
    if nbrows is None:
        nbrows = len(df)

    if not show_all:
        if nbcolumns > 10:
            nbcolumns = 10
        if nbrows > 50:
            nbrows = 50

    df = df.iloc[start:nbrows,0:nbcolumns]

    for col in df.columns:
        column_values.append(df[col])

    columns =  [str(x) for x in list(df.columns)]

    fig = go.Figure(data=[go.Table(
        header=dict(values=columns,
                    fill_color='royalblue',
                    line_color='darkslategray',
                    font=dict(color='white', size=12),
                    height=30,
                    align='left'),
        cells=dict(values=column_values,
                   fill_color='lavender',
                   line_color='darkslategray',
                   height=30,
                   font_size=12,
                   align='left'))
    ])

    params = {}
    params["width"] = nbcolumns * 150
    params["height"] = 32*(len(df)+1)
    if params["height"] > 512 and view_file:
        params["height"] = 512
    elif params["height"] > 320 and not view_file:
        params["height"] = 320

    fig.update_layout(**params)

    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            b=5,
            t=5,
            pad=4
        ),
    )
    plot_table = top_text + plot(fig, output_type='div', include_plotlyjs=False)
    return plot_table

#Create correlation table based on data
def create_corr(df, view_file=False, start=None, nbrows=None, is_corr=2):
    column_values = []
    nbcolumns = len(df.columns)
    top_text = "<p><b>"+_("Correlation Information")+ "</b></p>"

    if start is None:
        start = 0
    if nbrows is None:
        nbrows = len(df)

    if nbcolumns > 10:
        nbcolumns = 10
    if nbrows > 50:
        nbrows = 50

    df = df.iloc[start:nbrows,0:nbcolumns]

    for col in df.columns:
        column_values.append(df[col])

    columns =  [str(x) for x in list(df.columns)]

    fig = go.Figure(data=go.Heatmap(
                   z=column_values,
                   x=columns,
                   y=columns,
                   hoverongaps = False))
    fig.update_layout(
        margin=dict(
            l=0,
            r=0,
            b=5,
            t=5,
            pad=4
        ),
    )
    plot_table = top_text + plot(fig, output_type='div', include_plotlyjs=False)
    return plot_table

#generate query from data
def generate_query(request, graph_parameters):
    # get the parameters
    data_operator = graph_parameters['data_operator'] or 'and'
    datakeep_operator = graph_parameters['datakeep_operator'] or 'keep'
    file_code = graph_parameters['files'][0]

    data = {"final_query": None, "graph_parameters": None}
    current_project = request.session["current_project"]
    type_viz = graph_parameters['type_viz']
    mark_settings_str = " 1 = 1 "

    #try:
    #initialize variables to be returned
    df_pkl = "df_"+current_project["project_settings"]["files"][file_code]["df_file_code"]
    data_select = []
    data_where = []
    data_groupby = []
    data_having = []

    vzmx = "vzm"+settings.VIZ_X
    vzmy = "vzm"+settings.VIZ_Y
    vzmcolor = "vzm"+settings.VIZ_COLOR
    vzmfaccetcol = "vzm"+settings.VIZ_FACET_COLUMN
    vzmfacetrow = "vzm"+settings.VIZ_FACET_ROW
    vzmanimation = "vzm"+settings.VIZ_ANIMATION
    vzmshape = "vzm"+settings.VIZ_SHAPE
    vzmsize = "vzm"+settings.VIZ_SIZE
    vzmlabel = "vzm"+settings.VIZ_LABEL
    vzmhierachy = "vzm"+settings.VIZ_HIERACHY

    vzm_dimensions = [vzmx, vzmcolor, vzmfaccetcol, vzmfacetrow, vzmanimation, vzmshape, vzmhierachy]
    vzm_measures = [vzmy]
    vzm_size = [vzmsize]

    analysis_dimensions = []
    analysis_measures = []
    analysis_size = []
    analysis_where = []
    columns_dimensions = []
    columns_measures = []

    #features calculation
    col_num = []
    col_cat = []
    col_geo = []
    col_temp = []
    columns_dimensions_num = []
    columns_measures_num = []
    col_avg = []
    first_x = None

    key_column = ""
    need_group_by = 0
    # to manage bin columns
    before_select = ""
    after_from = ""
    list_bins = []
    order_by = []
    order_by_proposed = []
    order_by_bins = []

    viz_orientation = graph_parameters['viz_orientation'] or ''
    viztypemarks = str(settings.VIZ_ORIENTATION)+"__"+viz_orientation+"**"
    viz_grouping = graph_parameters['viz_grouping'] or ''
    viztypemarks += str(settings.VIZ_GROUPING)+"__"+viz_grouping+"**"

    for key, value in graph_parameters.items():
        if key == "data_filters" or "vzm" in key:
            key2 = 0
            nb_num = 0
            for filt in value:
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
                if key in vzm_dimensions:
                    if filt["dimmeasopt"] == 'sum' and (_("sum of ")+col) not in analysis_dimensions:
                        analysis_dimensions.append(_("sum of ")+col)
                    elif filt["dimmeasopt"] == 'avg' and (_("average of ")+col) not in analysis_dimensions:
                        analysis_dimensions.append(_("average of ")+col)
                    elif filt["dimmeasopt"] == 'min' and (_("minimum of ")+col) not in analysis_dimensions:
                        analysis_dimensions.append(_("minimum of ")+col)
                    elif filt["dimmeasopt"] == 'max' and (_("maximum of ")+col) not in analysis_dimensions:
                        analysis_dimensions.append(_("maximum of ")+col)
                    elif filt["fulltext"] not in analysis_dimensions:
                        analysis_dimensions.append(filt["fulltext"])
                    graph_parameters[key][key2]["analysis"] = analysis_dimensions[len(analysis_dimensions)-1]
                if key in vzm_measures:
                    if filt["dimmeasopt"] == 'sum' and (_("sum of ")+col) not in analysis_measures:
                        analysis_measures.append(_("sum of ")+col)
                    elif filt["dimmeasopt"] == 'avg' and (_("average of ")+col) not in analysis_measures:
                        analysis_measures.append(_("average of ")+col)
                    elif filt["dimmeasopt"] == 'min' and (_("minimum of ")+col) not in analysis_measures:
                        analysis_measures.append(_("minimum of ")+col)
                    elif filt["dimmeasopt"] == 'max' and (_("maximum of ")+col) not in analysis_measures:
                        analysis_measures.append(_("maximum of ")+col)
                    elif filt["fulltext"] not in analysis_measures:
                        analysis_measures.append(filt["fulltext"])
                    graph_parameters[key][key2]["analysis"] = analysis_measures[len(analysis_measures)-1]
                if key in vzm_size:
                    if filt["dimmeasopt"] == 'sum' and (_("sum of ")+col) not in analysis_size:
                        analysis_size.append(_("sum ")+col)
                    elif filt["dimmeasopt"] == 'avg' and (_("average of ")+col) not in analysis_size:
                        analysis_size.append(_("average ")+col)
                    elif filt["dimmeasopt"] == 'min' and (_("minimum of ")+col) not in analysis_size:
                        analysis_size.append(_("minimum ")+col)
                    elif filt["dimmeasopt"] == 'max' and (_("maximum of ")+col) not in analysis_size:
                        analysis_size.append(_("maximum ")+col)
                    elif filt["fulltext"] not in analysis_size:
                        analysis_size.append(filt["fulltext"])
                    graph_parameters[key][key2]["analysis"] = analysis_size[len(analysis_size)-1]

                if type_viz in [1,2]:
                    if (filt["realtype"] == "date"):
                        where_d = "(TO_CHAR("+col+"::date,'"+settings.DATE_FORMAT[filt["dimmeasopt"]]+"'))::text"
                        if filt["dimmeasopt"] != "valexact":
                            col_name += "_" + filt["dimmeasopt"]
                        select_d = where_d + " as " + col_name
                    elif (filt["realtype"] == "auto"):
                        where_d = "count(*)"
                        select_d = "COALESCE(" + where_d + ", 0)" + " as " + col_name
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
                        #select_d += ", (numrange(min("+col+")::numeric, max("+col+")::numeric, '[]'))::text as " + col_name
                        #select_d += ", (numrange(min("+col+"), max("+col+"), '[]'))::text as " + col_name
                    else:
                        where_d = col
                        col_name = col
                        select_d = where_d
                        groupby_d = col
                else:
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
                        #select_d += ", (numrange(min("+col+")::numeric, max("+col+")::numeric, '[]'))::text as " + col_name
                        #select_d += ", (numrange(min("+col+"), max("+col+"), '[]'))::text as " + col_name
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
                if key in vzm_dimensions or key in vzm_measures or key in vzm_size:
                    viztype_id = re.findall('\d+', key)[0]
                    if key in vzm_dimensions:
                        viztypemarks += str(viztype_id)+"__"+datatype+"__"+col_name+"__nb-"+col_name+"__or-"+col_name+"__"+filt["dimmeasopt"]+"__"+str(filt["dt"])+"**"
                        mark_settings_str += " AND LOWER(vot.mark_settings_str)" + " LIKE '%"+str(viztype_id)+"__"+datatype+"%' "
                    else:
                        viztypemarks += str(viztype_id)+"__"+datatype+"__"+col_name+"__nbm-"+col_name+"__orm-"+col_name+"__"+filt["dimmeasopt"]+"__"+str(filt["dt"])+"**"
                        mark_settings_str += " AND LOWER(vot.mark_settings_str)" + " LIKE '%"+str(viztype_id)+"__"+datatype+"%' "

                if key in vzm_dimensions:
                    columns_dimensions.append(col_name)
                    if datatype == settings.MEASURES_TYPES[0] and col_name not in columns_dimensions_num and filt["dimmeasopt"] != "bins":
                        columns_dimensions_num.append(col_name)
                if key in vzm_measures or key in vzm_size:
                    columns_measures.append(col_name)
                    if datatype == settings.MEASURES_TYPES[0] and col_name not in columns_measures_num and filt["dimmeasopt"] != "bins":
                        columns_measures_num.append(col_name)
                        if "coalesce" in select_d.lower() and "avg(" in select_d.lower() and col_name not in col_avg:
                            col_avg.append(col_name)

                if key in vzm_dimensions or key in vzm_measures or key in vzm_size:
                    if datatype == settings.ALL_TYPES[0] and filt["dimmeasopt"] != "bins" and col_name not in col_num:
                        col_num.append(col_name)
                    elif (datatype == settings.ALL_TYPES[3] or filt["dimmeasopt"] == "bins") and col_name not in col_cat:
                        col_cat.append(col_name)
                    elif datatype == settings.ALL_TYPES[2] and col_name not in col_geo:
                        col_geo.append(col_name)
                    elif datatype == settings.ALL_TYPES[1] and col_name not in col_temp:
                        col_temp.append(col_name)

                if first_x is None and key in [vzmx, vzmhierachy, vzmcolor, vzmfaccetcol, vzmfacetrow]:
                    if (datatype == settings.ALL_TYPES[3] or datatype == settings.ALL_TYPES[1] or filt["dimmeasopt"] == "bins"):
                        first_x = col_name
                #if first_x in [vzmcolor]:
                #    first_x = col_name

                if key in vzm_measures and "graphorder" not in filt:
                    if viz_orientation == 'v':
                        order_by_proposed.append(col_name+" asc")
                    else:
                        order_by_proposed.append(col_name+" desc")
                elif key in [vzmx, vzmhierachy, vzmcolor, vzmfaccetcol, vzmfacetrow] and "graphorder" not in filt:
                    if ((filt["type"] == "float64" or filt["type"] == "int64" or filt["realtype"] == "auto" or filt["realtype"] == "cat" or filt["realtype"] == "str") and filt["dimmeasopt"] != "bins"):
                        order_by_proposed.append(col_name+" asc")

                if "graphorder" in filt:
                    if filt["graphorder"] != "" and ((filt["type"] == "float64" or filt["type"] == "int64" or filt["realtype"] == "auto" or filt["realtype"] == "cat" or filt["realtype"] == "str") and filt["dimmeasopt"] != "bins"):
                        order_by.append(col_name+" "+filt["graphorder"])

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

                if select_d not in data_select and "vzm" in key:
                    data_select.append(select_d)
                if groupby_d and groupby_d not in data_groupby and "vzm" in key:
                    data_groupby.append(groupby_d)

            if nb_num == key2 and key2 != 0:
                key_column = key

    key_column = "vzm"+settings.VIZ_Y

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
        final_query +=" WHERE 1 = 1 "
    if len(data_groupby) > 0 and need_group_by == 1:
        final_query +=" GROUP BY " + ', '.join(data_groupby)
    if len(order_by_bins) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by_bins)
    elif len(col_temp) > 0:
        final_query +=" ORDER BY " + ', '.join(col_temp)
    elif len(col_geo) == 0 and len(col_temp) == 0 and len(order_by) > 0 and len(col_cat) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by)
    elif len(col_geo) == 0 and len(col_temp) == 0 and len(order_by_proposed) > 0 and len(col_cat) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by_proposed)


    if len(data_having) > 0:
        if data_operator == 'and':
            final_query +=" HAVING " + ' AND '.join(data_having)
        else:
            final_query +=" HAVING " + ' OR '.join(data_having)

    data = {"final_query": final_query, "final_graph_parameters": graph_parameters, "key_column": key_column,"analysis_dimensions": analysis_dimensions,
    "analysis_measures": analysis_measures, "analysis_size": analysis_size, "analysis_where": analysis_where, "need_group_by": need_group_by,
    "columns_dimensions": columns_dimensions, "columns_measures":columns_measures, "col_num":col_num, "col_cat":col_cat, "col_geo":col_geo, "col_temp":col_temp,
    "columns_dimensions_num":columns_dimensions_num, "columns_measures_num":columns_measures_num, "col_avg":col_avg, "first_x": first_x, "viztypemarks": viztypemarks,
    "after_from": after_from, "before_select": before_select, "order_by": order_by, "order_by_bins": order_by_bins, "mark_settings_str": mark_settings_str}
    print("Final query=============================")
    print(final_query)
    return data


#generate graph based on data
def generate_graph(request, graph_parameters, use_previous_data=False, recommend_code="", require_div=True, require_analysis=True):
    plot_table = None
    plot_analysis = None
    score_settings = ""
    viztypemarks = ""
    result = None
    plot_div = None
    score = ""
    add_marg_score = 0
    real_recommend_code = recommend_code
    analysis_html = ""

    # get the parameters
    if recommend_code != "":
        graph_parameters = request.session["recommend_graph"][recommend_code]["final_graph_parameters"]
        if "need_reload" in request.session["recommend_graph"][recommend_code] and request.session["recommend_graph"][recommend_code]["need_reload"] == 1:
            recommend_code = ""
            result = request.session["recommend_graph"][recommend_code]
            score = str(int(result["previous_viz"]["score"]))
        else:
            result = request.session["recommend_graph"][recommend_code]
            score_settings = result["score_settings"]
            viztypemarks = result["viztypemarks"]
            score = str(int(result["previous_viz"]["score"]))

        if "add_marg_score" in graph_parameters:
            add_marg_score = graph_parameters["add_marg_score"]

    visualization_code = graph_parameters['visualization_code']
    title_viz = ''
    if 'title' in graph_parameters:
        title_viz = graph_parameters['title']

    viz_title = graph_parameters['viz_title'] or ''
    viz_notes = graph_parameters['viz_notes'] or ''
    viz_orientation = graph_parameters['viz_orientation'] or ''
    viz_grouping = graph_parameters['viz_grouping'] or ''
    file_code = graph_parameters['files'][0]
    type_viz = graph_parameters['type_viz']
    nb_viz = graph_parameters['nb_viz']


    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    if not current_project:
        return data
    #try:
    #initialize variables to be returned
    df_pkl = "df_"+current_project["project_settings"]["files"][file_code]["df_file_code"]

    if recommend_code == "" and use_previous_data:
        result = request.session["previous_data"]
        features = request.session["features"]
        score_settings = request.session["score_settings"]
        viztypemarks = result["viztypemarks"]
    elif recommend_code == "":
        result = generate_query(request, graph_parameters)
        full_feature = calculate_features(request, result)
        print(full_feature)
        features = full_feature["feature"]
        operators = full_feature["operators"]

        score_settings = ""

        for key, val in features.items():
            #apply_onlyto_viz = request.session["list_features"][str(key)]["apply_onlyto_viz"]
            #array_apply_onlyto_viz = apply_onlyto_viz.split(",")
            #if len(apply_onlyto_viz) > 0 and len(array_apply_onlyto_viz) > 0:
            #    if str(type_viz) not in array_apply_onlyto_viz:
            #        score_settings += str(key)+"_"+""+"**"
            #        continue
            if val is False:
                score_settings += str(key)+"_"+settings.OPTION_SCORE_FALSE+"**"
            elif val is True:
                score_settings += str(key)+"_"+settings.OPTION_SCORE_TRUE+"**"
            else:
                if str(key) in operators:
                    score_settings += str(key)+"_"+operators[str(key)]+"_"+str(val)+"**"
                elif str(key) in settings.OPTION_SCORE_NUM:
                    score_settings += str(key)+"_"+settings.OPTION_SCORE_NUM[str(key)]+"_"+str(val)+"**"
                else:
                    score_settings += str(key)+"_"+settings.DEFAULT_OPTION_SCORE_NUM+"_"+str(val)+"**"
        if score_settings:
            score_settings = score_settings[:-2]
        result["score_settings"] = score_settings

        viztypemarks = get_final_viztypemarks(request, result)
        if viztypemarks:
            viztypemarks = viztypemarks[:-2]
        result["viztypemarks"] = viztypemarks

        request.session["previous_data"] = result
        request.session["features"] = features
        request.session["score_settings"] = score_settings
        #print(viztypemarks)

    final_graph_parameters = result["final_graph_parameters"]
    final_query = result["final_query"]
    key_column = result["key_column"]

    result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
    request.session["list_selectedfiles"][file_code]["file_link"], request.session["list_selectedfiles"][file_code]["refresh_timeout"],
    current_project["project_settings"]["files"][file_code]["df_file_code"], 0, request.session["convert_dict"][file_code],
    final_query)
    df = result_df["df"]

    if df is None:
        return data

    df.fillna(0, inplace = True)

    #create graph
    if df.shape[0] == 0:
        data = {'success': True}
        plot_div = '<p class="sm-marg red-text center">'+_("No data to plot")+'</p>'
    else:
        fig = ""
        if require_div and type_viz:
            try:
                #Create table
                if type_viz == 27:
                    columns = result["columns_dimensions"]+result["columns_measures"]
                    df_order = df.loc[:, columns]
                    plot_div = create_table(df_order)
                else:
                    fig = handle_multi_graph(request, df, type_viz, final_graph_parameters, viz_orientation, viz_grouping, viz_title, key_column)
                    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
                data = {'success': True}
            except Exception as e:
                print('Error details: '+ str(e))
                data = {'success': False, 'message': _("Something went wrong")}
                plot_div = '<p class="sm-marg red-text center">'+_("Unable to display the plot")+'</p>'
                score = settings.BAD_VIZ_SCORE

    if not plot_div and require_div:
        plot_div ="<div class='center pdtb'>"+_('No data available for your request')+"</div>"
        plot_analysis =""

    if require_analysis:
        intersection = " depending on "
        left_analysis = ""
        right_analysis = ""
        where_analysis = ""

        analysis = _("This ")+request.session["list_viztypes"][str(type_viz)]["name"].lower()+_(" shows ")
        analysis_html = _("This ")+request.session["list_viztypes"][str(type_viz)]["name"].lower()+_(" shows ")
        #if len(result["analysis_size"]) > 0:
        #    left_analysis = ", ".join(result["analysis_size"])
        #    right_array = result["analysis_dimensions"] + result["analysis_measures"]
        #    right_analysis = ", ".join(right_array)
        #else:
        include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
        include_marks = include_marks.split(",")
        if type_viz in settings.MAP_VIZ:
            intersection = ""
            left_analysis = ", ".join(result["analysis_size"])
            left_analysis_html = "</span>, <span class='notes-meas'>".join(result["analysis_size"])
            if left_analysis_html != "":
                left_analysis_html = "<span class='notes-meas'>"+left_analysis_html+"</span>"
            right_analysis = ", ".join(result["analysis_dimensions"]+result["analysis_measures"])
            right_analysis_html = "</span>, <span class='notes-dim'>".join(result["analysis_dimensions"]+result["analysis_measures"])
            if right_analysis_html != "":
                right_analysis_html = "<span class='notes-dim'>"+right_analysis_html+"</span>"
            if len(result["analysis_size"]) > 0:
                intersection = _(" group by ")
            if len(result["analysis_where"]) > 0:
                where_analysis = _(" where ")+", ".join(result["analysis_where"])

            analysis += left_analysis + intersection + right_analysis + where_analysis
            analysis_html += left_analysis_html + intersection + right_analysis_html + where_analysis
        else:
            left_analysis = ", ".join(result["analysis_measures"]+result["analysis_size"])
            left_analysis_html = "</span>, <span class='notes-meas'>".join(result["analysis_measures"]+result["analysis_size"])
            if left_analysis_html != "":
                left_analysis_html = "<span class='notes-meas'>"+left_analysis_html+"</span>"
            if len(result["analysis_measures"]) > 0 and type_viz != 27 and (str(settings.VIZ_GROUPING) not in include_marks and str(settings.VIZ_ORIENTATION) not in include_marks):
                left_analysis = result["analysis_measures"][0]
                left_analysis_html = "<span class='notes-meas'>"+result["analysis_measures"][0]+"</span>"
            right_analysis = ", ".join(result["analysis_dimensions"])
            right_analysis_html = "</span>, <span class='notes-dim'>".join(result["analysis_dimensions"])
            if right_analysis_html != "":
                right_analysis_html = "<span class='notes-dim'>"+right_analysis_html+"</span>"

            if result["need_group_by"] == 1:
                intersection = _(" group by ")
            if len(result["analysis_where"]) > 0:
                where_analysis = _(" where ")+", ".join(result["analysis_where"])

            if len(result["analysis_measures"]) == 0 or len(result["analysis_dimensions"])==0:
                intersection = ""

            analysis += left_analysis + intersection + right_analysis + where_analysis
            analysis_html += left_analysis_html + intersection + right_analysis_html + where_analysis

        if viz_title == "":
            viz_title = left_analysis + intersection + right_analysis
            #if fig != "":
            #    fig.update_layout(title_text=viz_title, title_font_size=14)

        if viz_notes == "":
            viz_notes = analysis

        if "dimensions" in request.session and file_code in request.session["dimensions"]:
            init_dictitems = request.session["dimensions"][file_code].items()
            l = list(init_dictitems)
            l.sort(reverse=True)
            dictitems = dict(l)
            #print(dictitems)

            for col, dim in dictitems.items():
                if analysis_html != "":
                    analysis_html = analysis_html.replace(col,dim["fulllabel"])
                if analysis != "":
                    analysis = analysis.replace(col,dim["fulllabel"])
                if viz_title != "":
                    viz_title = viz_title.replace(col,dim["fulllabel"])
                if viz_notes != "":
                    viz_notes = viz_notes.replace(col,dim["fulllabel"])

        if "measures" in request.session and file_code in request.session["measures"]:
            init_dictitems = request.session["measures"][file_code].items()
            l = list(init_dictitems)
            l.sort(reverse=True)
            dictitems = dict(l)
            #print(dictitems)

            for col, meas in dictitems.items():
                if analysis_html != "":
                    analysis_html = analysis_html.replace(col,meas["fulllabel"])
                if analysis != "":
                    analysis = analysis.replace(col,meas["fulllabel"])
                if viz_title != "":
                    viz_title = viz_title.replace(col,meas["fulllabel"])
                if viz_notes != "":
                    viz_notes = viz_notes.replace(col,meas["fulllabel"])

        #plot_analysis ="<div class='center bg-analysis'><i class='left'><b>"+_('Analysis')+"</b></i><p>"+analysis+"</p></div>"

    #except Exception as e:
    #    print('Error details: '+ str(e))
    #    data = {'success': False, 'message': _("Something went wrong")}
    #    plot_div = '<p class="sm-marg red-text center">'+_("Unable to display the plot")+'</p>'

    plot_div = '<div class="plot-div" id="plot'+visualization_code+'">'+plot_div+'</div>'
    #print(df.head())
    viz_data = {"result": result, "viz_title": viz_title, "viz_orientation": viz_orientation, "viz_grouping": viz_grouping, "file_code": file_code, "add_dash": 0, "df_file_code": current_project["project_settings"]["files"][file_code]["df_file_code"]}
    #request.session["viz_data"] = viz_data
    viz_data = json.dumps(viz_data)
    show_spec = False
    if real_recommend_code != "":
        show_spec = True

    show_alter = False
    if "limit_nb_viz" in final_graph_parameters and final_graph_parameters["limit_nb_viz"] == 1:
        show_alter = True

    if "chviz" in graph_parameters and graph_parameters["chviz"] == 1:
        show_alter = True
    #print(graph_parameters["visualization_action"])

    top_viz = create_top_viz(request, title_viz, visualization_code, score_settings, viztypemarks, type_viz, viz_data, viz_notes,analysis_html, score, show_spec, add_marg_score, show_alter)
    class_div = "s12 m12"
    if nb_viz and nb_viz > 1:
        class_div = "s12 m12"

    div_all = top_viz+plot_div
    if real_recommend_code == "":
        div_all = '<div class="all_viz_details col '+class_div+'" id="'+visualization_code+'">'+div_all+'</div>'

    data["plot_div"] = plot_div
    data["top_viz"] = top_viz
    data["div_all"] = div_all
    #save_viz(request, viz_data)
    return data

#Handle multi measures in axis y
def handle_multi_graph(request, df, type_viz, final_graph_parameters, viz_orientation, viz_grouping, viz_title, key_column):
    step = 0
    nbrows = 0
    nbcols = 0
    colors = settings.COLORS_PLOT
    params_y = {}
    fig = None
    include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
    include_marks = include_marks.split(",")


    if len(final_graph_parameters[key_column]) == 0:
        info_graph = create_graph(request, df, type_viz, final_graph_parameters, viz_orientation, viz_grouping, viz_title, key_column, step)
        fig = info_graph["fig"]
        list_unique = info_graph["list_unique"]
    else:
        for axis_y in final_graph_parameters[key_column]:
            color = ""
            if len(final_graph_parameters[key_column]) > 1:
                if step < len(colors):
                    color = colors[step]
                else:
                    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

            if "graphcolor" in final_graph_parameters[key_column][step]:
                graphcolor = final_graph_parameters[key_column][step]["graphcolor"]
                if graphcolor and graphcolor != "":
                    color = "#"+final_graph_parameters[key_column][step]["graphcolor"]

            info_graph = create_graph(request, df, type_viz, final_graph_parameters, viz_orientation, viz_grouping, viz_title, key_column, step, color)
            new_trace = info_graph["fig"]
            list_unique = info_graph["list_unique"]
            if len(final_graph_parameters[key_column]) == 1 and color != "":
                try:
                    if "marker" in new_trace.data[0] and ("legendgroup" not in new_trace.data[0] or ("legendgroup" in new_trace.data[0] and len(new_trace.data[0]["legendgroup"])==0)):
                        for i in range(len(new_trace.data)):
                            new_trace.data[i].marker.color = color
                except:
                    print("color not defined")

                try:
                    if "line" in new_trace.data[0] and ("legendgroup" not in new_trace.data[0] or ("legendgroup" in new_trace.data[0] and len(new_trace.data[0]["legendgroup"])==0)):
                        for i in range(len(new_trace.data)):
                            new_trace.data[i].line.color = color
                except:
                    print("line not defined")

            if len(final_graph_parameters[key_column]) > 1 and (str(settings.VIZ_GROUPING) in include_marks or str(settings.VIZ_ORIENTATION) in include_marks) :
                try:
                    if "marker" in new_trace.data[0] and ("legendgroup" not in new_trace.data[0] or ("legendgroup" in new_trace.data[0] and len(new_trace.data[0]["legendgroup"])==0)):
                        for i in range(len(new_trace.data)):
                            new_trace.data[i].marker.color = color
                except:
                    print("color not defined")

                try:
                    if "line" in new_trace.data[0] and ("legendgroup" not in new_trace.data[0] or ("legendgroup" in new_trace.data[0] and len(new_trace.data[0]["legendgroup"])==0)):
                        for i in range(len(new_trace.data)):
                            new_trace.data[i].line.color = color
                except:
                    print("line not defined")

                if type_viz not in [19, 20] and (("legendgroup" not in new_trace.data[0] or ("legendgroup" in new_trace.data[0] and len(new_trace.data[0]["legendgroup"])==0))):
                    for i in range(len(new_trace.data)):
                        if i == 0:
                            new_trace.data[i].showlegend = True
                            new_trace.data[i].name = final_graph_parameters[key_column][step]["col_name"]
                            new_trace.data[i].legendgroup = final_graph_parameters[key_column][step]["col_name"]
                        else:
                            new_trace.data[i].showlegend = False
                            new_trace.data[i].name = final_graph_parameters[key_column][step]["col_name"]
                            new_trace.data[i].legendgroup = final_graph_parameters[key_column][step]["col_name"]
                        if "graphlabel" in final_graph_parameters[key_column][step]:
                            graphlabel = final_graph_parameters[key_column][step]["graphlabel"]
                            if graphlabel and graphlabel != "":
                                new_trace.data[i].name = graphlabel
                                new_trace.data[i].legendgroup = graphlabel
                elif type_viz not in [19, 20]:
                    for i in range(len(new_trace.data)):
                        if step == 0:
                            new_trace.data[i].showlegend = True
                        else:
                            new_trace.data[i].showlegend = False
                        #new_trace.data[i].name = new_trace.data[i]["legendgroup"]+ "("+final_graph_parameters[key_column][step]["col_name"]+")"
                        #new_trace.data[i].legendgroup = None

            if step == 0:
                fig = new_trace
                if (str(settings.VIZ_GROUPING) not in include_marks and str(settings.VIZ_ORIENTATION) not in include_marks):
                    break
            elif (str(settings.VIZ_GROUPING) in include_marks or str(settings.VIZ_ORIENTATION) in include_marks):
                for i in range(len(new_trace.data)):
                    fig.add_trace(new_trace.data[i])

            step = step + 1

    fig.update_layout(margin=dict(
            l=0,
            r=10,
            b=5,
            t=15,
            pad=4
        ),legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            tracegroupgap=5,
            font=dict(size=10)
        ), font=dict(size=11)
    )
    #Help to put axis x to the top
    #fig.update_xaxes(side='top')
    #Show a range slider
    #fig.update_xaxes(rangeslider_visible=True)
    try:
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    except Exception as e:
        print('Error details annot: '+ str(e))

    #try:
    #    fig.for_each_trace(lambda t: t.update(name=t.name.split("=")[1]))
    #except Exception as e:
    #    print('Error details trace: '+ str(e))

    nb_plots = len(df)
    if "x" in list_unique:
        nb_plots = list_unique["x"]

    if type_viz in [1, 2]:
        if "x" in list_unique:
            nb_plots = list_unique["x"]
        else:
            nb_plots  = 1

    if viz_grouping == "group":
        nb_plots = nb_plots * len(final_graph_parameters[key_column])

    plot_width = ''
    plot_height = ''
    max_plots = 10000000
    include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
    include_marks = include_marks.split(",")
    type_viz = int(type_viz)

    if type_viz in [15, 1, 2, 3, 10]:
        if viz_orientation == 'v':
            fig.update_yaxes(type='category')
        else:
            fig.update_xaxes(type='category')

    if type_viz == 15:
        #lollipop
        plot_width = 5 * (nb_plots)
        #fig.update_layout(bargap=0.95)
    elif type_viz in [1, 2]:
        #boxplot, violin
        plot_width = 60 * (nb_plots)
    elif type_viz in [3, 10]:
        #histogram, bar
        #plot_width = ""
        plot_width = 17 * (nb_plots)
    elif type_viz in [7]:
        #correlogram
        plot_width = 230 * len(final_graph_parameters['vzm'+settings.VIZ_HIERACHY])
        plot_height = 230 * len(final_graph_parameters['vzm'+settings.VIZ_HIERACHY])
    #elif type_viz in [9, 26]:
        #area, line
    #    plot_width = 25 * (nb_plots)
    #elif type_viz in [6, 26]:
        #connected scatter
    #    plot_width = 17 * (nb_plots)
    elif type_viz in [21]:
        #parallel_coordinates
        if len(final_graph_parameters['vzm'+settings.VIZ_HIERACHY]) > 2:
            plot_width = 135 * len(final_graph_parameters['vzm'+settings.VIZ_HIERACHY]) + 60
        fig.update_layout(margin=dict(
                l=50,
                r=10,
                b=5,
                t=50,
                pad=20
            )
        )

    if viz_orientation == 'v' and (str(settings.VIZ_ORIENTATION) in include_marks):
        interm = plot_width
        plot_width = plot_height
        plot_height = interm

    if "facet_col" in list_unique and list_unique["facet_col"]>0:
        if plot_width:
            plot_width = (plot_width+50) * list_unique["facet_col"]
        else:
            plot_width = 230 * list_unique["facet_col"]

    if "facet_row" in list_unique and list_unique["facet_row"]>0:
        if plot_height:
            plot_height = (plot_height+50) * list_unique["facet_row"]
        else:
            plot_height = 230 * list_unique["facet_row"]

    params = {}
    if plot_width:
        params["width"] = plot_width
    if plot_height:
        params["height"] = plot_height

    if "width" in params and params["width"] < 350:
        del params["width"]
        if type_viz == 15:
            fig.update_layout(bargap=0.85)

    if "height" in params and params["height"] < 350:
        del params["height"]
        if type_viz == 15:
            fig.update_layout(bargap=0.85)

    if "width" in params and params["width"] == "":
        del params["width"]

    if "height" in params and params["height"] == "":
        del params["height"]

    if bool(params):
        fig.update_layout(**params)

    params = {}
    #params_new = {}
    for key in fig.layout:
        if "yaxis" in key:
            params[key]=dict(title=None)
            #params_new[key]=dict(title=fig['layout']['yaxis']['title'])


    #if type_viz not in [7,5,6] and (len(params.keys()) > 1 or len(final_graph_parameters[key_column])>1):
    if type_viz not in [7,5,6] and (len(final_graph_parameters[key_column])>1):
        fig.update_layout(**params)

    return fig


#for get the height of the line for lollipop
def offset_signal(signal, marker_offset):
    if abs(signal) <= marker_offset:
        return 0
    return signal - marker_offset if signal > 0 else signal + marker_offset

#create graph based on parameters
def create_graph(request, df, type_viz, final_graph_parameters, viz_orientation, viz_grouping, viz_title, key_column, step, color=""):
    fig  = None
    type_viz = int(type_viz)
    params = {}
    nb_unique = df.nunique()
    list_unique = {}

    vzmx = "vzm"+settings.VIZ_X
    vzmy = "vzm"+settings.VIZ_Y
    vzmcolor = "vzm"+settings.VIZ_COLOR
    vzmfaccetcol = "vzm"+settings.VIZ_FACET_COLUMN
    vzmfacetrow = "vzm"+settings.VIZ_FACET_ROW
    vzmanimation = "vzm"+settings.VIZ_ANIMATION
    vzmshape = "vzm"+settings.VIZ_SHAPE
    vzmsize = "vzm"+settings.VIZ_SIZE
    vzmlabel = "vzm"+settings.VIZ_LABEL
    vzmhierachy = "vzm"+settings.VIZ_HIERACHY

    list_vzm = [vzmx, vzmy, vzmcolor, vzmfaccetcol, vzmfacetrow, vzmanimation,
    vzmshape, vzmsize, vzmlabel, vzmhierachy]
    params_vzm = ["x", "y", "color", "facet_col", "facet_row", "animation_frame",
    "symbol", "size", "hover_data", "dimensions"]

    include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
    include_marks = include_marks.split(",")
    #print(include_marks)
    if type_viz in [13, 17]:
        #donut & pie_chart
        params_vzm[0] = "names"
        params_vzm[1] = "values"
    elif type_viz in [19, 20]:
        #sunburst, treemap
        #params_vzm[0] = "names"
        params_vzm[9] = "path"
        params_vzm[1] = "values"
    elif type_viz in [11, 16]:
        #bubblemap & map
        px.set_mapbox_access_token(settings.MAPBOX_TOKEN)
        #params["mapbox_style"] = 'open-street-map'
        params_vzm[0] = "lat"
        params_vzm[1] = "lon"
    elif type_viz in [26]:
        #line
        params_vzm[6] = "line_dash"

    inc = 0
    is_num_x = 0
    is_num_y = 0
    bins = 0
    histfunc = "count"
    params["labels"] = {}
    col_name_point = ""
    col_name_shape = ""

    for key in list_vzm:
        vizmark_id = re.findall('\d+', key)[0]
        if str(vizmark_id) not in include_marks:
            inc = inc + 1
            continue
        if key in final_graph_parameters and len(final_graph_parameters[key]) > 0:
            key2 = 0
            if key == key_column:
                key2 = step

            key_graph = params_vzm[inc]
            col_name = final_graph_parameters[key][key2]["col_name"]

            if "graphlabel" in final_graph_parameters[key][key2]:
                graphlabel = final_graph_parameters[key][key2]["graphlabel"]
                if graphlabel and graphlabel != "":
                    params["labels"][col_name] = graphlabel
            if "realtype" in final_graph_parameters[key][key2]:
                realtype = final_graph_parameters[key][key2]["realtype"]
                if realtype == "point":
                    col_name_point = col_name
                if realtype == "shape":
                    col_name_shape = col_name

            #if "bins" in final_graph_parameters[key][key2] and key_graph in ["x","y"] and final_graph_parameters[key][key2]["bins"] != "":
            #    bins = int(final_graph_parameters[key][key2]["bins"])

            #if "dimmeasopt" in final_graph_parameters[key][key2] and key_graph in ["x","y"] and final_graph_parameters[key][key2]["dimmeasopt"] in ['sum', 'avg', 'min', 'max']:
            #    histfunc = final_graph_parameters[key][key2]["dimmeasopt"]

            if key_graph == "x":
                is_num_x = final_graph_parameters[key][key2]["is_num"]
            if key_graph == "y":
                is_num_y = final_graph_parameters[key][key2]["is_num"]

            if key_graph in ["x","facet_col","facet_row"]:
                list_unique[key_graph] = int(nb_unique[col_name])

            if key_graph == "x" and viz_orientation == 'v':
                key_graph = "y"
            elif key_graph == "y" and viz_orientation == 'v':
                key_graph = "x"
            elif key_graph in ["hover_data", "dimensions", "path"]:
                col_name = []
                #params["hover_name"] = col_name
                #params["text"] = col_name
                for dat in final_graph_parameters[key]:
                    col_name.append(dat["col_name"])

            elif key_graph in ["color"] and type_viz == 21 and final_graph_parameters[key][key2]["is_num"] == 0:
                df_notnull = df.dropna(subset=[col_name])
                unique_values = df_notnull[col_name].unique().tolist()
                ids = range(len(unique_values))
                new_values = dict(zip(unique_values, ids))
                df[col_name] = df[col_name].map(new_values)
            #elif key_graph == "animation_frame":
            #    params["animation_group"] = final_graph_parameters[key][key2]["col_name"]

            params[key_graph] = col_name

        inc = inc + 1

    if viz_orientation == 'v' and (str(settings.VIZ_ORIENTATION) in include_marks):
        params["orientation"] = 'h'
    if viz_grouping == "overlay" and "overlay" in include_marks and type_viz not in [1,2]:
        params["opacity"] = 0.5
    if not viz_grouping or viz_grouping == "" and viz_grouping is None:
        viz_grouping = "group"
    if type_viz in settings.MAP_VIZ:
        params["zoom"] = settings.ZOOM_MAP
        if "size" in params and "hover_data" not in params:
            params["hover_data"] = [params["size"]]
        elif "size" in params and "hover_data" in params:
            params["hover_data"].append(params["size"])
        if "size" in params and "color" not in params:
            params["color"] = params["size"]
        if col_name_point != "":
            df[['latitude','longitude']] = df[col_name_point].str.split(",",expand=True)
            df[['latitude','longitude']] = df[['latitude','longitude']].astype(float)
            params["lat"] = "latitude"
            params["lon"] = "longitude"
        if col_name_shape != "":
            points = []
            params["zoom"] = settings.ZOOM_MAP + 5
            for inc in df[col_name_shape]:
                inc = inc.replace('""""','"')
                inc = inc.replace('"""','')
                inc = inc.replace('""',"\'")
                feature = json.loads(inc)
                feature = feature.replace('\'','"')
                feature = json.loads(feature)
                #print(feature)

                if feature['type'] == 'Polygon':
                    points.extend(feature['coordinates'][0])
                    points.append([None, None]) # mark the end of a polygon
                elif feature['type'] == 'MultiPolygon':
                    for polyg in feature['coordinates']:
                        points.extend(polyg[0])
                        points.append([None, None]) #end of polygon
                elif feature['type'] == 'LineString':
                    points.extend(feature['coordinates'])
                    points.append([None, None])
                elif feature['type'] == 'MultiLineString':
                    for line  in feature['geometry']['coordinates']:
                        points.extend(line)
                        points.append([None, None])
                else: pass
                print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
            lons, lats = zip(*points)
            params["lat"] = lats
            params["lon"] = lons
        else:
            params["size_max"] = settings.SIZE_MAP
            params["color_continuous_scale"] = px.colors.cyclical.IceFire


    if type_viz == 16:
        if "size" in params:
            del params["size"]
    #if type_viz in [3,4]:
    #    params["histfunc"] = histfunc
    #    if bins > 0:
    #        params["nbins"] = bins

    params["data_frame"] = df
    params["template"] = 'plotly_white'
    #print(df)

    if "facet_col" in params:
        params["facet_col_spacing"] = 0.003
        if type_viz == 15:
            params["facet_col_spacing"] = 0.007
    if "facet_row" in params:
        params["facet_row_spacing"] = 0.005
    #if type_viz == 18:
       #connected scatter
    #   fig = px.scatter(**params)
    #   fig.update_traces(mode='lines+markers')

    #try:
    fig = get_fig(request, df, type_viz, fig, px, ff, params, viz_grouping, is_num_x, is_num_y, col_name_shape)
    #except Exception as e:
    #    print('Error details: '+ str(e))

    if type_viz in [13, 17] and int(df.shape[0]) > 9: #donut, pie
        fig.update_layout(showlegend=False)

    return {"fig":fig, "list_unique":list_unique}

#Create the buttons at the top of each visualization
def create_top_viz(request, title_viz, visualization_code, score_settings, viztypemarks, type_viz, viz_data, analysis, analysis_html, score='', show_spec=False, add_marg_score=0, show_alter=False, viz_score_settings=''):
    showfewbuttons = ""
    if request.session["current_user_type"] == settings.NON_EXPERT:
        showfewbuttons = "hide"

    top_div = '<div class="operator_sm center top_viz" data-id="'+visualization_code+'">'
    top_div += '<input type="hidden" id="scs'+visualization_code+'" value="'+score_settings+'"/>'
    top_div += '<input type="hidden" id="vtm'+visualization_code+'" value="'+viztypemarks+'"/>'
    top_div += '<input type="hidden" id="vt'+visualization_code+'" value="'+str(type_viz)+'"/>'
    top_div += '<textarea class="hide" id="vd'+visualization_code+'">'+str(viz_data)+'</textarea>'

    top_div += '<div class="col s12 m12 divsc hide" id="divsc'+visualization_code+'"><label class="lab">'+_("How appropriate is the visualization used to represent these data?")+'</label><div class="col s12 m12 center"><small>'+_("Not appriopriate")+'</small><div class="starrr" id="scr'+visualization_code+'" data-target="'+visualization_code+'"></div><small>'+_("Very appriopriate")+'</small><select data-position="top" data-tooltip="'+_("Rate this visualization")+'" id="sc'+visualization_code+'" name="score" class="browser-default tooltip score hide">'
    top_div += '<option value="">'+_("Rate this visualization")+'</option>'

    selected = ""
    score = str(score)
    if score != "" and int(score) < 0:
        selected = "selected"
    top_div += '<option '+selected+' value="'+settings.BAD_VIZ_SCORE+'">'+_("Bad")+'</option>'

    for i in range(settings.MAX_SCORE):
        selected = ""
        if str(i) == score:
            selected = "selected"
        top_div += '<option '+selected+' value="'+str(i)+'">'+str(i)+'/'+str(int(settings.MAX_SCORE)-1)+'</option>'

    top_div += '</select><input type="hidden" id="scmarg'+visualization_code+'" value="'+str(add_marg_score)+'"/></div>'
    top_div += '<div class="col s12 m12 center hide"><button class="left btn-flat btn waves-effect waves-light green toolti rounded lower submit-rate" style="padding:2px 3px !important; border:0px solid transparent !important; color: white !important;"'
    top_div += 'data-position="top" data-tooltip="'+_("Submit rate")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="subrt'+visualization_code+'" onclick="submit_rate(\''+visualization_code+'\')"><i class="material-icons left" style="margin-right:3px !important;">save_alt</i><span>'+_("Submit")+'</span>'
    top_div += '</button></div></div>'

    top_div += '<div class="clear"></div><div style="height:7px !important;">&nbsp;</div><div class="clear"></div>'

    #if "current_user_type" in request.session and (request.session["current_user_type"] in [settings.NON_EXPERT]):
    #top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower change-viz"'
    #top_div += 'data-position="top" data-tooltip="'+_("Change Visualization Type")+'"'
    #top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="change'+visualization_code+'" onclick="changeFieldsViz(\''+visualization_code+'\')"><i class="material-icons">bar_chart</i> '+_("Change Viz Type")+'</span>'
    #top_div += '</button>'

    #if "current_user_type" in request.session and (request.session["current_user_type"] in [settings.INTERMEDIATE, settings.EXPERT]):
    #if show_spec:
    top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower specify-viz"'
    top_div += 'data-position="top" data-tooltip="'+_("Edit visualization")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="spec'+visualization_code+'" onclick="loadFieldsViz(\''+visualization_code+'\')"><i class="material-icons">edit</i> '+_("Edit")+'</span>'
    top_div += '</button>'

    if show_alter:
        top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower '+showfewbuttons+' alter-viz"'
        top_div += 'data-position="top" data-tooltip="'+_("See alternative visualizations")+'"'
        top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="alt'+visualization_code+'" onclick="alterViz(\''+visualization_code+'\')"><i class="material-icons left">visibility</i> '+_("Alternative Vizs")+'</span>'
        top_div += '</button>'

    if type_viz not in settings.MAP_VIZ:
        top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower '+showfewbuttons+' zoom-viz"'
        top_div += 'data-position="top" data-tooltip="'+_("Zoom visualization")+'"'
        top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="zm'+visualization_code+'" onclick="zoom(\''+visualization_code+'\')"><i class="material-icons left">zoom_out_map</i> '+_("Zoom")+'</span>'
        top_div += '</button>'

    top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower remv-viz '+showfewbuttons+' red"'
    top_div += 'data-position="top" data-tooltip="'+_("Remove visualization")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="remove'+visualization_code+'" onclick="removeViz(\''+visualization_code+'\')"><i class="material-icons left">delete</i> '+_("Remove")+'</span>'
    top_div += '</button>'

    top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower add-embed"'
    top_div += 'data-position="top" data-tooltip="'+_("Embed")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="emb'+visualization_code+'" onclick="add_to_embed(\''+visualization_code+'\')"><i class="material-icons left">code</i> '+_("Embed")+'</span>'
    top_div += '</button>'

    top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower add-dash"'
    top_div += 'data-position="top" data-tooltip="'+_("Add to dashboard")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="ad'+visualization_code+'" onclick="add_to_dash(\''+visualization_code+'\')"><i class="material-icons left">addchart</i> '+_("Add to dashboard")+'</span>'
    top_div += '</button>'

    #myclass = "hide"
    myclass = "hide"

    if request.user and request.user.is_superuser:
        myclass = ""

    top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower settings-score '+myclass+'"'
    top_div += 'data-position="top" data-tooltip="'+_("Edit rate settings")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="ss'+visualization_code+'" onclick="score_settings(\''+visualization_code+'\')"><i class="material-icons left">settings</i> '+_("Settings")+'</span>'
    top_div += '</button>'

    top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower rate-viz hide"'
    top_div += 'data-position="top" data-tooltip="'+_("Rate visualization")+'"'
    top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="rt'+visualization_code+'" onclick="rate_viz(\''+visualization_code+'\')"><i class="material-icons left">insert_emoticon</i> '+_("Rate")+'</span>'
    top_div += '</button>'

    #top_div += '<button class="btn-flat waves-effect waves-light toolti rounded lower notes-dash hide"'
    #top_div += 'data-position="top" data-tooltip="'+_("Hide/Show details")+'"'
    #top_div += 'type="button" name="action" data-id="'+visualization_code+'" id="vn'+visualization_code+'" onclick="hide_vizdetails(\''+visualization_code+'\')"><i class="material-icons">info</i></span>'
    #top_div += '</button>'
    #if "current_user_type" in request.session and (request.session["current_user_type"] in [settings.EXPERT]):
    if score != "" and request.session["current_user_type"] != settings.NON_EXPERT:
        top_div += '<br/><span>'+_("Average Score")+'('+score+'/'+str(int(settings.MAX_SCORE)-1)+')</span>'
    top_div += '<div class="clear"></div>'


    if title_viz != '':
        top_div += '<div class="col s12 m12 ahtml hide" id="ahtml'+visualization_code+'">'+analysis_html+'</div>'
        top_div += '<div class="col s12 m12 a2html" id="a2html'+visualization_code+'"><b>'+title_viz+'</b></div>'
    else:
        top_div += '<div class="col s12 m12 ahtml" id="ahtml'+visualization_code+'">'+analysis_html+'</div>'

    top_div += '<div class="col s12 m12 hide" id="divvzn'+visualization_code+'"><textarea data-position="top" data-tooltip="'+_("Short interpretation of the graph")+'" placeholder="'+_("Visualisation notes")+'" id="vzn'+visualization_code+'" name="vzn" class="validate browser-default tooltipped">'+analysis+'</textarea></div>'

    top_div += '<div class="clear"></div>'

    top_div += '</div>'
    return top_div

#Calculate features values based on visulaisation marks chosen by the user
def calculate_features(request, params, is_primary=False):
    cursor = connection.cursor()
    feature = {}
    real_feature = {}
    featureDim = 0
    operators = {}
    operator = ""
    all_code = ""
    sql = ""
    row = None
    result = False
    str_dim = ""
    can = 0

    for key, feat in request.session["list_features"].items():
        if is_primary and not feat["is_primary"]:
            break
        expr = feat["formula"]
        codeBlock = str(expr)
        all_code += codeBlock+ "\n"

    compiledCodeBlock = compile(all_code, '<string>', 'exec')
    loc = {'cursor': cursor, 'sql': sql, "row":row, "result":result, "str_dim":str_dim,"feature":feature,"params":params,
     "settings":settings, "operators": operators, "operator": operator, "featureDim": featureDim, "can": can,
     "real_feature": real_feature}
    exec(compiledCodeBlock, {}, loc)

    feature = loc["feature"]
    operators = loc["operators"]
    return {"feature": feature, "operators": operators, "real_feature": real_feature}

#record the score of visulization
def record_scores(request, variables):
    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    if not current_project:
        return data
    # get the parameters
    viz_codes = variables['viz_codes']
    viz_scores = variables['viz_scores']
    viz_types = variables['viz_types']
    viz_type_marks = variables['viz_type_marks']
    viz_score_settings = variables['viz_score_settings']
    #print(variables)
    #try:
    if True:
        key = 0
        for score in viz_scores:
            vizinput, created = VizInput.objects.get_or_create(value=viz_score_settings[key])
            if created:
                feature_settings = {}
                score_settings = viz_score_settings[key].split("**")
                array_insights = []
                for score_setting in score_settings:
                    get_items = score_setting.split("_")
                    formula = ""
                    apply_onlyto_viz = request.session["list_features"][str(get_items[0])]["apply_onlyto_viz"]
                    feat_name = request.session["list_features"][str(get_items[0])]["name"]
                    array_apply_onlyto_viz = apply_onlyto_viz.split(",")
                    if len(apply_onlyto_viz) > 0 and len(array_apply_onlyto_viz) > 0:
                        if str(viz_types[key]) not in array_apply_onlyto_viz:
                            continue

                    if int(get_items[0]) == settings.FEATURE_HAS_BINNED:
                        if "1_equalto_1" in score_settings and "2_equalto_1" in score_settings and "5_equalto_1" in score_settings and "6_equalto_1" in score_settings:
                            print("feature binned is taken in account")
                        else:
                            continue

                    if get_items[1]:
                        vizinputfeature = VizInputFeature()
                        vizinputfeature.vizinput_id = vizinput.id
                        vizinputfeature.value = score_setting
                        vizinputfeature.feature_id = int(get_items[0])
                        vals = []
                        if len(get_items) == 3:
                            vals = get_items[2].split("#")
                        if get_items[1] == "isbetween" and len(vals) == 2 and len(vals[0]) > 0 and len(vals[1]) > 0:
                            formula = "(feature['"+get_items[0]+"'] >= "+str(vals[0])+" and feature['"+get_items[0]+"'] <= "+str(vals[1])+")"
                            ins = feat_name+" >= "+str(vals[0])+" and "+feat_name+" <= "+str(vals[1])
                            array_insights.append(ins)
                        elif get_items[1] in ["istrue", "isfalse"]:
                            formula = "(feature['"+get_items[0]+"'] "+settings.OPERATOR_CORRESPONDANTS[str(get_items[1])]+")"
                            ins = feat_name+" "+settings.OPERATOR_CORRESPONDANTS[str(get_items[1])]
                            array_insights.append(ins)
                        elif len(vals) == 1 and len(vals[0]) > 0:
                            formula = "(feature['"+get_items[0]+"'] "+settings.OPERATOR_CORRESPONDANTS[str(get_items[1])]+" "+str(vals[0])+")"
                            ins = feat_name+" "+settings.OPERATOR_CORRESPONDANTS[str(get_items[1])]+" "+str(vals[0])
                            array_insights.append(ins)
                        if formula != "":
                            feature_settings[vizinputfeature.feature_id] = formula
                            vizinputfeature.formula = formula
                            vizinputfeature.save()
                insight = ""
                if len(array_insights) > 0:
                    insight = "\n".join(array_insights)

                vizinput.feature_settings = feature_settings
                vizinput.insight = insight
                vizinput.save(update_fields=['feature_settings', 'insight'])

            vizoutput = None
            created = False
            input_scores = vizinput.scores


            if request.user and request.user.id:
                vizoutput, created = VizOutput.objects.get_or_create(viztype__id=int(viz_types[key]),
                vizinput__id= vizinput.id, user__id=int(request.user.id), viz_code=str(viz_codes[key]), project_code=request.session['project_code'],
                defaults={'score': float(score), 'vizinput_id': vizinput.id, 'viztype_id': int(viz_types[key]), 'user_type': request.session["current_user_type"]})
                if not created:
                    old_score = request.session["list_viztypes"][str(viz_types[key])]["name"]+":"+str(vizoutput.score)
                    new_score = request.session["list_viztypes"][str(viz_types[key])]["name"]+":"+str(score)

                    if input_scores and input_scores is not None:
                        input_scores = input_scores.replace(old_score, new_score)
                    else:
                        input_scores = request.session["list_viztypes"][str(viz_types[key])]["name"]+":"+str(score)+"\n"
                    vizoutput.score = float(score)
                    vizoutput.save(update_fields=['score'])
                else:
                    if not input_scores and input_scores is None:
                        input_scores = ""
                    input_scores = input_scores + request.session["list_viztypes"][str(viz_types[key])]["name"]+":"+str(score)+"\n"
                vizinput.scores = input_scores
                vizinput.save(update_fields=['scores'])
            else:
                vizoutput = VizOutput()
                vizoutput.viztype_id = int(viz_types[key])
                vizoutput.vizinput_id = vizinput.id
                vizoutput.viz_code = str(viz_codes[key])
                vizoutput.project_code = request.session['project_code']
                vizoutput.score = float(score)
                vizoutput.user_type = request.session["current_user_type"]
                vizoutput.save()
                if not input_scores and input_scores is None:
                    input_scores = ""
                input_scores = input_scores + request.session["list_viztypes"][str(viz_types[key])]["name"]+":"+str(score)+"\n"
                created = True
                vizinput.scores = input_scores
                vizinput.save(update_fields=['scores'])

            if created:
                mark_settings = {}
                mark_settings_str = ""
                type_marks = viz_type_marks[key].split("**")
                for type_mark in type_marks:
                    get_items = type_mark.split("__")
                    viztypemark = VizTypeMark()
                    viztypemark.user_type = request.session["current_user_type"]
                    viztypemark.viztype_id = int(viz_types[key])
                    viztypemark.vizmark_id = int(get_items[0])
                    viztypemark.viz_code = str(viz_codes[key])
                    viztypemark.project_code = request.session['project_code']
                    viztypemark.vizoutput_id = vizoutput.id
                    if get_items[0] != settings.VIZ_ORIENTATION and get_items[0] != settings.VIZ_GROUPING:
                        #print(get_items)
                        viztypemark.rule = {"coltype": str(get_items[1]), "nb_distinct": int(get_items[3]), "order": int(get_items[4]), "option": str(get_items[5]),
                        "real_datatype": str(get_items[6])}
                        mark_settings_str = mark_settings_str + str(viztypemark.vizmark_id)+"__"+str(get_items[1])+"__"+str(get_items[5])
                    elif get_items[0] == settings.VIZ_ORIENTATION and len(get_items[1])>0:
                        viztypemark.rule = {"orientation": str(get_items[1])}
                        mark_settings_str = mark_settings_str + str(viztypemark.vizmark_id)+"__"+str(get_items[1])
                    elif get_items[0] == settings.VIZ_GROUPING and len(get_items[1])>0:
                        viztypemark.rule = {"grouping": str(get_items[1])}
                        mark_settings_str = mark_settings_str + str(viztypemark.vizmark_id)+"__"+str(get_items[1])

                    viztypemark.save()
                    if viztypemark.vizmark_id not in mark_settings:
                        mark_settings[viztypemark.vizmark_id] = []
                    mark_settings[viztypemark.vizmark_id].append(viztypemark.rule)

                vizoutput.mark_settings = mark_settings
                vizoutput.mark_settings_str = mark_settings_str
                vizoutput.save(update_fields=['mark_settings', 'mark_settings_str'])

            key += 1
        data = {'success': True}
    #except Exception as e:
    #    print('Error details: '+ str(e))
    #    data = {'success': False, 'message': _("Something went wrong")}
    return data

#Get number of distict values per dimensions
def get_final_viztypemarks(request, params):
    cursor = connection.cursor()
    count = ""
    for colname in params["columns_dimensions"]:
        count += " count(distinct "+colname+"),"
    for colname in params["columns_measures"]:
        count += " count(distinct "+colname+"),"
    if count != "":
        count = count[:-1]

    sql = "select "+count+" from ("+params["final_query"]+") as q1"
    cursor.execute(sql)
    row = cursor.fetchall()
    len_dim = len(params["columns_dimensions"])
    len_meas = len(params["columns_measures"])
    viztypemarks = params["viztypemarks"]
    order_dim = {}
    order_meas = {}
    dim_temp = []
    dist_temp = []
    dim_other = []
    dist_other = []

    if len_dim > 0:
        if len(params["col_temp"]) > 0:
            dist = row[0][:len_dim]
            inj = 0
            for colname in params["columns_dimensions"]:
                if colname in params["col_temp"]:
                    dim_temp.append(colname)
                    dist_temp.append(dist[inj])
                else:
                    dim_other.append(colname)
                    dist_other.append(dist[inj])
                inj = inj + 1
            #order temporal
            array = np.array(dist_temp)
            temp = array.argsort()
            ranks = np.empty_like(temp)
            ranks[temp] = np.arange(len(array))
            key = 0
            for colname in dim_temp:
                order_dim[colname] = {'order':str(ranks[key]), 'nb':str(dist_temp[key])}
                viztypemarks = viztypemarks.replace("or-"+colname, str(ranks[key]))
                viztypemarks = viztypemarks.replace("nb-"+colname, str(dist_temp[key]))
                key += 1

            #order other type
            inc_temp = len(params["col_temp"])
            array = np.array(dist_other)
            temp = array.argsort()
            ranks = np.empty_like(temp)
            ranks[temp] = np.arange(len(array))
            key = 0
            for colname in dim_other:
                order_dim[colname] = {'order':str(int(ranks[key])+int(inc_temp)), 'nb':str(dist_other[key])}
                viztypemarks = viztypemarks.replace("or-"+colname, str(int(ranks[key])+int(inc_temp)))
                viztypemarks = viztypemarks.replace("nb-"+colname, str(dist_other[key]))
                key += 1
        else:
            dist = row[0][:len_dim]
            array = np.array(dist)
            temp = array.argsort()
            ranks = np.empty_like(temp)
            ranks[temp] = np.arange(len(array))
            key = 0
            for colname in params["columns_dimensions"]:
                viztypemarks = viztypemarks.replace("or-"+colname, str(ranks[key]))
                viztypemarks =viztypemarks.replace("nb-"+colname, str(dist[key]))
                key += 1
    if len_meas > 0:
        dist = row[0][-len_meas:]
        array = np.array(dist)
        temp = array.argsort()
        ranks = np.empty_like(temp)
        ranks[temp] = np.arange(len(array))
        key = 0
        for colname in params["columns_measures"]:
            viztypemarks = viztypemarks.replace("orm-"+colname, str(ranks[key]))
            viztypemarks = viztypemarks.replace("nbm-"+colname, str(dist[key]))
            key += 1
    return viztypemarks

#Save the information about the visulization
def add_viz(request, visualization_code, type_viz, viz_data, viz_notes, plot_div):
    result = {'success': False, 'plot_div': ''}
    current_project = request.session["current_project"]

    if not current_project:
        return result

    project_history = []
    project_settings = {}
    current_state = 0
    viz_data = json.loads(viz_data)
    #viz_data = request.session["viz_data"]
    array_plot_div = plot_div.split('document.getElementById("')
    split_plot_div = array_plot_div[1].split('"))')
    plot_div_id = split_plot_div[0]
    add_to_plot_div = 'document.getElementById("'+plot_div_id+'").innerHTML = "";'
    plot_div = plot_div.replace('<script type="text/javascript">', '<script type="text/javascript"> '+add_to_plot_div)

    viz_data["visualization_code"] = visualization_code
    viz_data["type_viz"] = type_viz
    viz_data["viz_notes"] = viz_notes
    viz_data["plot_div"] = plot_div
    viz_data["add_dash"] = 1

    if bool(current_project["project_settings"]):
    	project_history = copy.deepcopy(current_project["project_history"])
    	project_settings = copy.deepcopy(current_project["project_settings"])

    if bool(project_settings):
    	previous_settings = copy.deepcopy(project_settings)
    	project_history.append(previous_settings)
    	current_state = len(project_history)

    if "vizs" not in project_settings:
       project_settings["vizs"] = {}

    viz_data["suffix"] = current_state
    visualization_code = viz_data["visualization_code"]
    project_settings["state"] = current_state
    insight = _("Add visualization #{}# to dashboard").format(viz_notes)
    project_settings["insight"] = insight
    project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    viz_data["show_nov"] = True
    viz_data["show_less"] = True
    viz_data["show_adv"] = True
    viz_data["width"] = "m12 l12"
    viz_data["height"] = "400"
    viz_final_title = viz_notes
    if viz_notes:
        viz_final_title = cleanhtml(viz_final_title)
        search = _("shows")
        indice = viz_final_title.index(search)
        if indice > 0:
        	viz_final_title = (viz_final_title[viz_final_title.index(search) + len(search):]).strip()

    viz_data["viz_final_title"] = viz_final_title

    if visualization_code in project_settings["vizs"]:
        viz_data["show_nov"] = project_settings["vizs"][visualization_code]["show_nov"]
        viz_data["show_less"] = project_settings["vizs"][visualization_code]["show_less"]
        viz_data["show_adv"] = project_settings["vizs"][visualization_code]["show_adv"]
        viz_data["width"] = project_settings["vizs"][visualization_code]["width"]
        viz_data["height"] = project_settings["vizs"][visualization_code]["height"]
        viz_data["viz_final_title"] = project_settings["vizs"][visualization_code]["viz_final_title"]

    project_settings["vizs"][visualization_code] = viz_data

    project = Project.objects.get(code__exact=request.session['project_code'])
    project.project_settings = project_settings
    project.project_history = project_history
    project.has_vizs = True
    project.save(update_fields=['project_settings','project_history','has_vizs'])
    #get current project
    request.session["current_project"] = {"id":project.pk, "project_settings":project.project_settings,
                "project_history":project.project_history, "user":(project.user and project.user.username), "title":project.title, "notes":project.notes, "shared":project.shared, "code":project.code, "dash_code":project.dash_code,
                "updated_at": project.updated_at.strftime('%d/%m/%Y'), "project_type": project.project_type, "contact": project.contact, "image": (project.image and project.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": project.static_image,
                "theme": str(project.theme.pk), "link": project.link, "country": project.country, "state": project.state, "status": str(project.status.pk), "list_datasets": project.list_datasets}
    #load_full_project(request, Project, "current_project", 1)

    if "action_traceability" in request.session:
        results = request.session["action_traceability"]
        results.append({"date": project_settings["date"], "state": project_settings["state"], "insight": project_settings["insight"]})
        request.session["action_traceability"] = results

    result = {'success': True, 'plot_div': plot_div}
    return result


#Save the information about the visulization
def embed_viz(request, visualization_code, type_viz, viz_data, viz_notes, plot_div):
    result = {'success': False, 'iframe': ''}
    current_project = request.session["current_project"]

    if not current_project:
        return result

    project_history = []
    project_settings = {}
    current_state = 0
    viz_data = json.loads(viz_data)
    #viz_data = request.session["viz_data"]
    array_plot_div = plot_div.split('document.getElementById("')
    split_plot_div = array_plot_div[1].split('"))')
    plot_div_id = split_plot_div[0]
    add_to_plot_div = 'document.getElementById("'+plot_div_id+'").innerHTML = "";'
    plot_div = plot_div.replace('<script type="text/javascript">', '<script type="text/javascript"> '+add_to_plot_div)

    viz_data["visualization_code"] = visualization_code
    viz_data["type_viz"] = type_viz
    viz_data["viz_notes"] = viz_notes
    viz_data["plot_div"] = plot_div
    viz_data["add_dash"] = 1

    if bool(current_project["project_settings"]):
    	project_history = copy.deepcopy(current_project["project_history"])
    	project_settings = copy.deepcopy(current_project["project_settings"])

    if bool(project_settings):
    	previous_settings = copy.deepcopy(project_settings)
    	project_history.append(previous_settings)
    	current_state = len(project_history)

    if "embed" not in project_settings:
       project_settings["embed"] = {}

    viz_data["suffix"] = current_state
    visualization_code = viz_data["visualization_code"]
    project_settings["state"] = current_state
    insight = _("Add embed visualization #{}#").format(viz_notes)
    project_settings["insight"] = insight
    project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    viz_data["show_nov"] = True
    viz_data["show_less"] = True
    viz_data["show_adv"] = True
    viz_data["width"] = "m12 l12"
    viz_data["height"] = "400"
    viz_final_title = viz_notes
    if viz_notes:
        viz_final_title = cleanhtml(viz_final_title)
        search = _("shows")
        indice = viz_final_title.index(search)
        if indice > 0:
        	viz_final_title = (viz_final_title[viz_final_title.index(search) + len(search):]).strip()

    viz_data["viz_final_title"] = viz_final_title

    if visualization_code in project_settings["embed"]:
        viz_data["show_nov"] = project_settings["embed"][visualization_code]["show_nov"]
        viz_data["show_less"] = project_settings["embed"][visualization_code]["show_less"]
        viz_data["show_adv"] = project_settings["embed"][visualization_code]["show_adv"]
        viz_data["width"] = project_settings["embed"][visualization_code]["width"]
        viz_data["height"] = project_settings["embed"][visualization_code]["height"]
        viz_data["viz_final_title"] = project_settings["embed"][visualization_code]["viz_final_title"]

    project_settings["embed"][visualization_code] = viz_data

    project = Project.objects.get(code__exact=request.session['project_code'])
    project.project_settings = project_settings
    project.project_history = project_history

    project.save(update_fields=['project_settings','project_history'])
    #get current project
    request.session["current_project"] = {"id":project.pk, "project_settings":project.project_settings,
                "project_history":project.project_history, "user":(project.user and project.user.username), "title":project.title, "notes":project.notes, "shared":project.shared, "code":project.code, "dash_code":project.dash_code,
                "updated_at": project.updated_at.strftime('%d/%m/%Y'), "project_type": project.project_type, "contact": project.contact, "image": (project.image and project.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": project.static_image,
                "theme": str(project.theme.pk), "link": project.link, "country": project.country, "state": project.state, "status": str(project.status.pk), "list_datasets": project.list_datasets}
    #load_full_project(request, Project, "current_project", 1)

    if "action_traceability" in request.session:
        results = request.session["action_traceability"]
        results.append({"date": project_settings["date"], "state": project_settings["state"], "insight": project_settings["insight"]})
        request.session["action_traceability"] = results

    url_iframe = settings.URL_IFRAME
    url_iframe = url_iframe.replace('#dash_code#', project.dash_code)
    url_iframe = url_iframe.replace('#viz_code#', visualization_code)
    iframe = '<iframe src="'+url_iframe+'" width="400" height="400" frameborder="0"></iframe>'

    result = {'success': True, 'iframe': iframe}
    return result

#Delete viz from dashboard
def drop_viz(request, visualization_code):
    result = {'success': False, 'div_id': ''}
    current_project = request.session["current_project"]
    if not current_project:
        return result
    project_history = []
    project_settings = {}
    current_state = 0

    if bool(current_project["project_settings"]):
    	project_history = copy.deepcopy(current_project["project_history"])
    	project_settings = copy.deepcopy(current_project["project_settings"])

    if bool(project_settings):
    	previous_settings = copy.deepcopy(project_settings)
    	project_history.append(previous_settings)
    	current_state = len(project_history)

    if "vizs" in project_settings and visualization_code in project_settings["vizs"]:
        project_settings["state"] = current_state
        insight = _("Drop visualization #{}# from dashboard").format(project_settings["vizs"][visualization_code]["viz_notes"])
        project_settings["insight"] = insight
        project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        viz = project_settings["vizs"][visualization_code]
        div_id = visualization_code+str(viz["suffix"])

        project = Project.objects.get(code__exact=request.session['project_code'])

        del project_settings["vizs"][visualization_code]
        project.project_settings = project_settings
        project.project_history = project_history
        project.save(update_fields=['project_settings','project_history'])

        #get current project
        request.session["current_project"] = {"id":project.pk, "project_settings":project.project_settings,
                    "project_history":project.project_history, "user":(project.user and project.user.username), "title":project.title, "notes":project.notes, "shared":project.shared, "code":project.code, "dash_code":project.dash_code,
                    "updated_at": project.updated_at.strftime('%d/%m/%Y'), "project_type": project.project_type, "contact": project.contact, "image": (project.image and project.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": project.static_image,
                    "theme": str(project.theme.pk), "link": project.link, "country": project.country, "state": project.state, "status": str(project.status.pk), "list_datasets": project.list_datasets}
        #load_full_project(request, Project, "current_project", 1)

        if "action_traceability" in request.session:
            results = request.session["action_traceability"]
            results.append({"date": project_settings["date"], "state": project_settings["state"], "insight": project_settings["insight"]})
            request.session["action_traceability"] = results

        result = {'success': True, 'div_id': div_id}
    return result


def save_dash_info(request, dash_parameters):
    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    if not current_project:
        return data

    project_history = []
    project_settings = {}
    current_state = 0

    if bool(current_project["project_settings"]):
    	project_history = copy.deepcopy(current_project["project_history"])
    	project_settings = copy.deepcopy(current_project["project_settings"])

    if bool(project_settings):
    	previous_settings = copy.deepcopy(project_settings)
    	project_history.append(previous_settings)
    	current_state = len(project_history)

    #title = dash_parameters['dash_title'] or ""
    #notes = dash_parameters['dash_notes'] or ""
    shared = False
    if 'shared' in dash_parameters:
        shared = True

    layout = int(dash_parameters['dash_layout'])
    dash_filters = dash_parameters['dash_filters']
    allviz_notes = dash_parameters['allviz_notes']
    find_file = False
    dash_file = ""
    if len(dash_parameters['files_dash']) > 0 :
        file_code = dash_parameters['files_dash'][0]
        if "vizs" in project_settings:
            for viz_code, viz in project_settings["vizs"].items():
                project_settings["vizs"][viz_code]["apply_filter"] = 0
                if file_code == viz["file_code"] and viz["add_dash"] == 1:
                    dash_file = file_code
                    project_settings["vizs"][viz_code]["apply_filter"] = 1
                    find_file = True

        if not find_file:
            if "vizs" in project_settings:
                if bool(project_settings["vizs"]):
                    data["message"] = _('Please set the filters for the fields inside the dashboard')
                else:
                    data["message"] = _('No Visulization inside the dashboard')
            else:
                data["message"] = _('No Visulization inside the dashboard')
            return data

    for viznote in allviz_notes:
        code = viznote["code"]
        viz_notes = cleanhtml(viznote["notes"])
        project_settings["vizs"][code]["viz_notes"] = viz_notes
        project_settings["vizs"][code]["viz_final_title"] = viznote["viz_final_title"]
        project_settings["vizs"][code]["show_nov"] = viznote["show_nov"]
        project_settings["vizs"][code]["show_less"] = viznote["show_less"]
        project_settings["vizs"][code]["show_adv"] = viznote["show_adv"]
        project_settings["vizs"][code]["width"] = viznote["width"]
        project_settings["vizs"][code]["height"] = viznote["height"]

    for setup in settings.SETUP_DASH.keys():
        if setup in dash_parameters:
            project_settings[setup] = True
        else:
            project_settings[setup] = False

    key = 0
    data_where = []
    data_form = ""
    dash_where = ""
    for filt in dash_filters:
        col = filt["name"]
        col_name = col
        where_d = ""
        where_d1 = ""
        where_d2 = ""
        input_form = ""
        add_classdate = ""

        if (filt["realtype"] == "date"):
            where_d = "(TO_CHAR("+col+"::date,'"+settings.DATE_FORMAT[filt["dimmeasopt"]]+"'))::text"
            if filt["dimmeasopt"] == "ymd":
                add_classdate = "datepicker"
        else:
            where_d = col

        if "optionfilt" in filt:
            labelfilt = filt["labelfilt"]
            filter_values = filt["valuefilt"].split("##")
            filter_value1 = "param@@"+str(key)
            filter_value2 = "param@@"+str(key+1)
            inc = 1
            if filt["type"] != "float64" and filt["type"] != "int64" and "contains" not in filt["optionfilt"]:
                filter_value1 = "'"+filter_value1+"'"
                filter_value2 = "'"+filter_value2+"'"

            if filt["optionfilt"] == "contains" and filter_value1 is not None:
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
                where_d1 = where_d + " >= " + filter_value1
                where_d2 = where_d + " <= " + filter_value2
                #where_d = where_d + " >= " + filter_value1 + " and " + where_d + " <= " + filter_value2
                inc = 2
            elif filt["optionfilt"] == "in" and filter_values:
                where_d += " IN ('" + "param@@"+str(key) + "') "
            elif filt["optionfilt"] == "notin" and filter_values:
                where_d += " NOT IN ('" + "param@@"+str(key) + "') "

            if filt["optionfilt"] == "isbetween":
                input_form = '<p class="dh-label">'+labelfilt+'</p><div class="row">'
                input_form += '<div class="sm-mb col s6">'
                input_form += '<input placeholder="Value" name="'+'param'+str(key)+'" type="text" class="validate '+add_classdate+'">'
                input_form += '</div>'
                input_form += '<div class="sm-mb col s6">'
                input_form += '<input placeholder="Value" name="'+'param'+str(key+1)+'" type="text" class="validate '+add_classdate+'">'
                input_form += '</div></div>'
            elif filt["optionfilt"] in ["in", "notin"] and filter_values:
                input_form = '<p class="dh-label">'+labelfilt+'</p><div class="row">'
                for val in filter_values:
                    input_form += '<div class="col m6 s6 truncate"><label><input name="'+'param'+str(key)+'[]" value="'+val+'" class="citem" type="checkbox"/><span title="'+val+'">'+val+'</span></label></div>'
                input_form += '</div>'
            else:
                input_form = '<p class="dh-label">'+labelfilt+'</p><div class="row">'
                input_form += '<div class="sm-mb col s12">'
                input_form += '<input placeholder="Value" name="'+'param'+str(key)+'" type="text" class="validate '+add_classdate+'">'
                input_form += '</div></div>'

            where_d = "("+where_d+")"
            key = key + inc
            if where_d not in data_where and input_form != "":
                if filt["optionfilt"] == "isbetween" and filter_value1 is not None and filter_value2 is not None:
                    data_where.append("("+where_d1+")")
                    data_where.append("("+where_d2+")")
                else:
                    data_where.append(where_d)
                if filt["optionfilt"] in ["in", "notin"]:
                    data_form += '<div class="clear"></div><div>'+input_form+'</div><div class="clear"></div>'
                else:
                    data_form += '<div class="clear"></div><div>'+input_form+'</div><div class="clear"></div>'

    #if len(data_where) > 0:
    #    dash_where += ' AND '.join(data_where)
    if "dashboard" not in project_settings:
        project_settings["dashboard"] = {}

    project_settings["dashboard"] = {"layout": layout, "filters": dash_filters, "where": data_where,
    "form": data_form, "nb_params":key, "dash_file": dash_file, "shared": shared}
    project_settings["state"] = current_state
    insight = _("Change Setup Dashboard")
    project_settings["insight"] = insight
    project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    project = Project.objects.get(code__exact=request.session['project_code'])
    project.project_settings = project_settings
    project.project_history = project_history
    #project.title = title
    #project.notes = notes
    if not project.shared and shared:
        project.published_at = datetime.datetime.now()
        project.shared = shared
        project.save(update_fields=['project_settings','project_history','shared','published_at'])
    else:
        project.shared = shared
        project.save(update_fields=['project_settings','project_history','shared'])
    #get current project
    request.session["current_project"] = {"id":project.pk, "project_settings":project.project_settings,
                "project_history":project.project_history, "user":(project.user and project.user.username), "title":project.title, "notes":project.notes, "shared":project.shared, "code":project.code, "dash_code":project.dash_code,
                "updated_at": project.updated_at.strftime('%d/%m/%Y'), "project_type": project.project_type, "contact": project.contact, "image": (project.image and project.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": project.static_image,
                "theme": str(project.theme.pk), "link": project.link, "country": project.country, "state": project.state, "status": str(project.status.pk), "list_datasets": project.list_datasets}

    #load_full_project(request, Project, "current_project", 1)
    #get select files
    #load_data(request, UploadFile, "list_selectedfiles", 1)

    if "action_traceability" in request.session:
        results = request.session["action_traceability"]
        results.append({"date": project_settings["date"], "state": project_settings["state"], "insight": project_settings["insight"]})
        request.session["action_traceability"] = results
    data = {'success': True}

    return data


#update viz in dashboard
def update_viz(request, graph_parameters, code):
    # get the parameters
    data = {'success': False, 'message': _('Something went wrong')}
    try:
        project = Project.objects.get(code__exact=code)
    except:
        return data
    #mydata += "&viz_code="+viz_code+"&suffix="+suffix+"&file="+file_code;
    embed = False
    if "embed" in graph_parameters:
        embed = True

    visualization_code = graph_parameters['viz_code']
    project_settings = project.project_settings

    if embed:
        project_settings["vizs"] = copy.deepcopy(project_settings["embed"])

    viz_title = project_settings["vizs"][visualization_code]["viz_title"] or ''
    viz_notes = project_settings["vizs"][visualization_code]["viz_notes"] or ''
    viz_orientation = project_settings["vizs"][visualization_code]["viz_orientation"] or ''
    viz_grouping = project_settings["vizs"][visualization_code]["viz_grouping"] or ''
    file_code = graph_parameters['file']
    type_viz = project_settings["vizs"][visualization_code]['type_viz']
    where = project_settings["dashboard"]["where"]
    list_filters = []

    result = None
    plot_div = None

    #initialize variables to be returned
    df_pkl = "df_"+project_settings["vizs"][visualization_code]['df_file_code']
    plot_table = None
    plot_analysis = None
    score_settings = ""
    viztypemarks = ""

    result = project_settings["vizs"][visualization_code]["result"]
    final_graph_parameters = result["final_graph_parameters"]
    final_query = result["final_query"]
    key_column = result["key_column"]

    for key, val in graph_parameters.items():
        if "param" in key and key != "nb_params":
            param_key = re.findall('\d+', key)[0]
            filter = where[int(param_key)]
            if val and val is not None:
                if isinstance(val, list):
                    filter = filter.replace("param@@"+str(param_key), "', '".join(val))
                else:
                    filter = filter.replace("param@@"+str(param_key), val)
                list_filters.append(filter)

    if len(list_filters) > 0:
        add_where = ' AND '.join(list_filters)
        if "WHERE" in final_query:
            final_query = final_query.replace("WHERE ", "WHERE ("+add_where+") AND ")
        else:
            final_query = final_query.replace(df_pkl, df_pkl+" WHERE ("+add_where+") ")

    #print(final_query)

    if "list_selectedfiles" in request.session and file_code in request.session["list_selectedfiles"] and "convert_dict" in request.session and file_code in request.session["convert_dict"][file_code]:
        result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
        request.session["list_selectedfiles"][file_code]["file_link"], request.session["list_selectedfiles"][file_code]["refresh_timeout"],
        project_settings["vizs"][visualization_code]['df_file_code'], 0, request.session["convert_dict"][file_code], final_query)
    else:
        try:
            file = UploadFile.objects.get(code__exact=file_code)
        except:
            return data
        columns = project_settings["files"][file_code]["columns"]
        convert_dict = {}
        load_data(request, DataType, "list_datatypes", 0)
        for keycol, col in columns.items():
            current_datatype = request.session["list_datatypes"][str(col["datatype"])]
            convert_dict[keycol] = current_datatype["pandas_name"]

        result_df = save_read_df(request, file_code, file.file_ext, file.file_link, file.refresh_timeout,
        project_settings["vizs"][visualization_code]['df_file_code'], 0, convert_dict, final_query)

    df = result_df["df"]

    if df is None:
        return data

    df.fillna(0, inplace = True)
    if df.shape[0] == 0:
        data = {'success': True}
        plot_div = '<p class="sm-marg red-text center">'+_("No data to plot")+'</p>'
    else:
        try:
            #Create table
            if type_viz == 27:
                columns = result["columns_dimensions"]+result["columns_measures"]
                df_order = df.loc[:, columns]
                plot_div = create_table(df_order)
            else:
                fig = handle_multi_graph(request, df, type_viz, final_graph_parameters, viz_orientation, viz_grouping, viz_title, key_column)
                plot_div = plot(fig, output_type='div', include_plotlyjs=False)
            data = {'success': True}
        except Exception as e:
            print('Error details: '+ str(e))
            data = {'success': False, 'message': _("Something went wrong")}
            plot_div = '<p class="sm-marg red-text center">'+_("Unable to display the plot")+'</p>'

    data["plot_div"] = plot_div

    return data

#recommend graph based on data
def recommend_graph(request, graph_parameters, add_end=True, limit_nb_viz=9000, option_group=False, convert_temp=False, require_div=True, require_analysis=True):
    # get the parameters
    file_code = graph_parameters['files'][0]

    expert = float(graph_parameters['expert']) or settings.WEIGHT_EXPERT
    intermediate = float(graph_parameters['intermediate']) or settings.WEIGHT_INTERMEDIATE
    nonexpert = float(graph_parameters['non-expert'])  or settings.WEIGHT_NON_EXPERT
    threshold = float(graph_parameters['threshold'])  or settings.MIN_SCORE_THRESHOLD

    obj_data = ""
    if "obj_data" in graph_parameters:
        obj_data = graph_parameters["obj_data"]

    visualization_action = graph_parameters["visualization_action"]
    graph_parameters["limit_nb_viz"] = limit_nb_viz

    result = None
    plot_div = None

    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    if not current_project:
        return data

    try:
    #if True:
        #initialize variables to be returned
        df_pkl = "df_"+current_project["project_settings"]["files"][file_code]["df_file_code"]

        col_lat = None
        col_lon = None
        col_shape = None
        col_point = None
        need_second = False
        need_convert_temp = False
        max_temp_elments = 0

        if visualization_action == "recommend_viz1":
            graph_parameters["attribs"] = []
            graph_parameters["type_viz"] == -1
            for key, value in graph_parameters.items():
                if "vzm" in key and value and value is not None:
                    graph_parameters["attribs"] = graph_parameters["attribs"] + value
            graph_parameters["type_viz"] == -1
            result = generate_query(request, graph_parameters)
            viztypemarks = result["viztypemarks"]
            if len(result["col_temp"]) > 0 and convert_temp:
                result["col_cat"] = result["col_cat"] + result["col_temp"]
                result["col_temp"] = []
        else:
            result = recommend_query(request, graph_parameters)
            viztypemarks = result["viztypemarks"]
            result["columns_measures"] = []
            result["columns_measures_num"] = []
            result["analysis_measures"] = []
            result["columns_dimensions"] = []
            result["first_x"] = ""
            result["analysis_measures"] = []
            columns = current_project["project_settings"]["files"][file_code]["columns"]
            all_stat = current_project["project_settings"]["files"][file_code]["all_stat"]

            if len(result["col_num"]) > 0:
                corr_init = -3
                corr_col = ""
                corr_col2 = ""
                corr_tot = -9
                key_col = 0
                icn = 0
                for num_col in result["col_num_real"]:
                    if num_col != "count" and all_stat["stat"][num_col]["corr"]["nb_corr"] > corr_init:
                        corr_init = all_stat["stat"][num_col]["corr"]["nb_corr"]
                        corr_tot = all_stat["stat"][num_col]["corr"]["tot_corr"]
                        corr_col = num_col
                        key_col = icn
                    elif num_col != "count" and all_stat["stat"][num_col]["corr"]["nb_corr"] == corr_init and all_stat["stat"][num_col]["corr"]["tot_corr"] > corr_tot:
                        corr_init = all_stat["stat"][num_col]["corr"]["nb_corr"]
                        corr_tot = all_stat["stat"][num_col]["corr"]["tot_corr"]
                        corr_col = num_col
                        key_col = icn
                    icn = icn + 1

                if corr_col != "":
                    corr_init = -3
                    corr_col2 = ""
                    key_col2 = 0
                    icn = 0
                    for num_col in result["col_num_real"]:
                        if corr_col != num_col and num_col != "count":
                            if all_stat["stat"][corr_col]["corr"][num_col] > corr_init:
                                corr_init = all_stat["stat"][corr_col]["corr"][num_col]
                                corr_col2 = num_col
                                key_col2 = icn
                        icn = icn + 1

                tot = len(result["col_cat"]) + len(result["col_geo"]) + len(result["col_temp"])

                if len(result["col_num"]) == 2 and (result["need_group_by"] == 0):
                    if (corr_init < settings.GOOD_CORR and option_group == False) or (option_group == True):
                        result["columns_measures"] = result["columns_measures"] + result["col_num"]
                        result["columns_measures_num"] = result["columns_measures_num"] + result["col_num"]
                    else:
                        result["columns_dimensions"] = result["columns_dimensions"] + [result["col_num"][int(key_col2)]]
                        result["columns_measures"] = result["columns_measures"] + [result["col_num"][int(key_col)]]
                        result["columns_measures_num"] = result["columns_measures_num"] + [result["col_num"][int(key_col)]]
                        #if limit_nb_viz != 1:
                        need_second = True

                elif len(result["col_num"]) == 3 and (result["need_group_by"] == 0):
                    if (corr_init < settings.GOOD_CORR and option_group == False) or (option_group == True):
                        result["columns_measures"] = result["columns_measures"] + result["col_num"]
                        result["columns_measures_num"] = result["columns_measures_num"] + result["col_num"]
                    else:
                        key_col3 = 0
                        for l in range(3):
                            if l != int(key_col) and l != int(key_col2):
                                key_col3 = l
                                break
                        result["columns_dimensions"] = result["columns_dimensions"] + [result["col_num"][int(key_col2)]]
                        result["columns_measures"] = result["columns_measures"] + [result["col_num"][int(key_col3)]]
                        result["columns_measures_num"] = result["columns_measures_num"] + [result["col_num"][int(key_col3)]]
                        result["columns_measures"] = result["columns_measures"] + [result["col_num"][int(key_col)]]
                        result["columns_measures_num"] = result["columns_measures_num"] + [result["col_num"][int(key_col)]]
                        #if limit_nb_viz != 1:
                        need_second = True
                elif len(result["col_num"]) > 3 and tot == 0 and (result["need_group_by"] == 0):
                    result["columns_dimensions"] = result["columns_dimensions"] + result["col_num"]
                else:
                    result["columns_measures"] = result["columns_measures"] + result["col_num"]
                    result["columns_measures_num"] = result["columns_measures_num"] + result["col_num"]

            if len(result["col_cat"]) > 0:
                result["columns_dimensions"] = result["columns_dimensions"] + result["col_cat"]
            if len(result["col_geo"]) > 0:
                len_geo = len(result["col_geo"])
                for l in range(len_geo):
                    col = result["col_geo_real"][l]
                    datatype = columns[col]["datatype"]
                    if datatype == settings.LAT_DATATYPE:
                        col_lat = col
                        result["columns_dimensions"] = result["columns_dimensions"] + [result["col_geo"][int(l)]]
                    elif datatype == settings.LON_DATATYPE:
                        col_lon = col
                        result["columns_measures"] = result["columns_measures"] + [result["col_geo"][int(l)]]
                        result["columns_measures_num"] = result["columns_measures_num"] + [result["col_geo"][int(l)]]
                    elif datatype == settings.SHAPE_DATATYPE:
                        col_shape = col
                        result["columns_dimensions"] = result["columns_dimensions"] + [result["col_geo"][int(l)]]
                    elif datatype == settings.POINT_DATATYPE:
                        col_point = col
                        result["columns_dimensions"] = result["columns_dimensions"] + [result["col_geo"][int(l)]]

            if len(result["col_temp"]) > 0:
                result["columns_dimensions"] = result["columns_dimensions"] + result["col_temp"]
                if convert_temp:
                    result["col_cat"] = result["col_cat"] + result["col_temp"]
                    result["col_temp"] = []

            if len(result["columns_dimensions"]) > 0:
                result["first_x"] = result["columns_dimensions"][0]

        #print(result["first_x"])
        full_feature = calculate_features(request, result)

        feature = full_feature["feature"]
        real_feature = full_feature["real_feature"]
        operators = full_feature["operators"]

        score_settings = ""
        for key, val in feature.items():
            if val is False:
                score_settings += str(key)+"_"+settings.OPTION_SCORE_FALSE+"**"
            elif val is True:
                score_settings += str(key)+"_"+settings.OPTION_SCORE_TRUE+"**"
            else:
                if str(key) in operators:
                    score_settings += str(key)+"_"+operators[str(key)]+"_"+str(val)+"**"
                elif str(key) in settings.OPTION_SCORE_NUM:
                    score_settings += str(key)+"_"+settings.OPTION_SCORE_NUM[str(key)]+"_"+str(val)+"**"
                else:
                    score_settings += str(key)+"_"+settings.DEFAULT_OPTION_SCORE_NUM+"_"+str(val)+"**"
        if score_settings:
            score_settings = score_settings[:-2]
        #print(score_settings)

        feature_keys = list(feature.keys())
        vizinputs = VizInput.objects.all()
        all_code = create_formula_features(request, vizinputs, feature_keys)

        list_vizinputs = []

        compiledCodeBlock = compile(all_code, '<string>', 'exec')
        locals = {"feature":real_feature, "list_vizinputs":list_vizinputs}

        exec(compiledCodeBlock, {}, locals)

        list_vizinputs = locals["list_vizinputs"]
        #print(len(list_vizinputs))

        if len(list_vizinputs)> 0:
            str_vizinputs = ",".join(list_vizinputs)
            obj_data = str(obj_data)
            #print(obj_data)
            if obj_data == "" or obj_data == "0" or obj_data == 0:
                query = """select AVG(score) as avg_score, viztype_id, user_type from visualizations_vizoutput
                            join visualizations_viztype on visualizations_viztype.id = visualizations_vizoutput.viztype_id
                            where vizinput_id in (%s) and visualizations_viztype.active=True
                            group by viztype_id, user_type
                            order by viztype_id, user_type
                            """ % str_vizinputs
            else:
                query = """select AVG(score) as avg_score, viztype_id, user_type from visualizations_vizoutput
                            join visualizations_viztype on visualizations_viztype.id = visualizations_vizoutput.viztype_id
                            where vizinput_id in (%s) and visualizations_viztype.active=True and visualizations_viztype.id in (%s)
                            group by viztype_id, user_type
                            order by viztype_id, user_type
                            """ % (str_vizinputs, obj_data)
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            #print(rows)

            recommendations = {}
            avg_scores = {}
            current_viz = -1
            score = {"expert": 0, "intermediate": 0, "non-expert": 0}
            for row in rows:
                if current_viz == -1:
                    current_viz = row[1]
                if row[1] != current_viz:
                    avg_score = (expert * float(score["expert"]) + intermediate * float(score["intermediate"]) + nonexpert * float(score["non-expert"]))/100.0
                    if avg_score >= threshold:
                        recommendations[current_viz] = {"score": score, "avg_score": avg_score}
                        avg_scores[current_viz] = avg_score
                    score = {"expert": 0, "intermediate": 0, "non-expert": 0}
                    current_viz = row[1]
                if row[1] == current_viz:
                    score[row[2]] = float(row[0])

            avg_score = (expert * float(score["expert"]) + intermediate * float(score["intermediate"]) + nonexpert * float(score["non-expert"]))/100.0
            if avg_score >= threshold:
                recommendations[current_viz] = {"score": score, "avg_score": avg_score}
                avg_scores[current_viz] = avg_score

            avg_scores_sorted = {k: v for k, v in sorted(avg_scores.items(), key=lambda item: item[1], reverse=True)}
            all_viztypes = avg_scores_sorted
            #print(avg_scores_sorted)
            list_viztypes = list(avg_scores_sorted.keys())

            #Handle histogram issue with bar & lollipop
            if settings.GRAPH_HISTOGRAM in list_viztypes and settings.GRAPH_BAR in list_viztypes and "order_by_bins" in result and len(result["order_by_bins"]) > 0:
                list_viztypes.remove(settings.GRAPH_BAR)
            if settings.GRAPH_HISTOGRAM in list_viztypes and settings.GRAPH_LOLLIPOP in list_viztypes and  "order_by_bins" in result and len(result["order_by_bins"]) > 0:
                list_viztypes.remove(settings.GRAPH_LOLLIPOP)

            if len(list_viztypes) > limit_nb_viz:
                temp_viztypes = list_viztypes[:limit_nb_viz]
                list_viztypes = copy.deepcopy(temp_viztypes)

            print("listvizs=========================================================")
            print(list_viztypes)

            if len(list_viztypes) > 0:
                count = ""
                for colname in result["columns_dimensions"]:
                    count += " count(distinct "+colname+"),"
                for colname in result["columns_measures"]:
                    count += " count(distinct "+colname+"),"
                if count != "":
                    count = count[:-1]

                sql = "select "+count+" from ("+result["final_query"]+") as q1"
                cursor.execute(sql)
                row = cursor.fetchall()
                len_dim = len(result["columns_dimensions"])
                len_meas = len(result["columns_measures"])
                order_dim = {}
                order_meas = {}

                dim_temp = []
                dist_temp = []

                dim_other = []
                dist_other = []

                if len_dim > 0:
                    if len(result["col_temp"]) > 0:
                        dist = row[0][:len_dim]
                        inj = 0
                        for colname in result["columns_dimensions"]:
                            if colname in result["col_temp"]:
                                dim_temp.append(colname)
                                dist_temp.append(dist[inj])
                            else:
                                dim_other.append(colname)
                                dist_other.append(dist[inj])
                            inj = inj + 1
                        #order temporal
                        array = np.array(dist_temp)
                        temp = array.argsort()
                        ranks = np.empty_like(temp)
                        ranks[temp] = np.arange(len(array))
                        key = 0
                        for colname in dim_temp:
                            if dist_temp[key] > max_temp_elments:
                                max_temp_elments = dist_temp[key]

                            order_dim[colname] = {'order':str(ranks[key]), 'nb':str(dist_temp[key])}
                            viztypemarks = viztypemarks.replace("or-"+colname, str(ranks[key]))
                            viztypemarks = viztypemarks.replace("nb-"+colname, str(dist_temp[key]))
                            key += 1

                        #order other type
                        inc_temp = len(result["col_temp"])
                        array = np.array(dist_other)
                        temp = array.argsort()
                        ranks = np.empty_like(temp)
                        ranks[temp] = np.arange(len(array))
                        key = 0
                        for colname in dim_other:
                            order_dim[colname] = {'order':str(int(ranks[key])+int(inc_temp)), 'nb':str(dist_other[key])}
                            viztypemarks = viztypemarks.replace("or-"+colname, str(int(ranks[key])+int(inc_temp)))
                            viztypemarks = viztypemarks.replace("nb-"+colname, str(dist_other[key]))
                            key += 1
                    else:
                        dist = row[0][:len_dim]
                        array = np.array(dist)
                        temp = array.argsort()
                        ranks = np.empty_like(temp)
                        ranks[temp] = np.arange(len(array))
                        key = 0
                        for colname in result["columns_dimensions"]:
                            order_dim[colname] = {'order':str(ranks[key]), 'nb':str(dist[key])}
                            viztypemarks = viztypemarks.replace("or-"+colname, str(ranks[key]))
                            viztypemarks = viztypemarks.replace("nb-"+colname, str(dist[key]))
                            key += 1

                if len_meas > 0:
                    dist = row[0][-len_meas:]
                    array = np.array(dist)
                    temp = array.argsort()
                    ranks = np.empty_like(temp)
                    ranks[temp] = np.arange(len(array))
                    key = 0
                    for colname in result["columns_measures"]:
                        order_meas[colname] = {'order':str(ranks[key]), 'nb':str(dist[key])}
                        if visualization_action == "recommend_viz1":
                            viztypemarks = viztypemarks.replace("orm-"+colname, str(ranks[key]))
                            viztypemarks = viztypemarks.replace("nbm-"+colname, str(dist[key]))
                        else:
                            viztypemarks = viztypemarks.replace("or-"+colname, str(ranks[key]))
                            viztypemarks = viztypemarks.replace("nb-"+colname, str(dist[key]))
                        key += 1

                if viztypemarks:
                    viztypemarks = viztypemarks[:-2]
                #print("================================")
                #print(order_dim)
                #print("================================")
                #print(order_meas)

                list_viztypes = [str(viz) for viz in list_viztypes]
                str_viztypes = ','.join(list_viztypes)
                #print(str_viztypes)
                mark_settings_str = " 1 = 1 "
                need_marks = 1
                if visualization_action == "recommend_viz1" and "mark_settings_str" in result:
                    need_marks = 0
                    mark_settings_str = result["mark_settings_str"]

                query = """select vo.score, vo.viztype_id, vo.mark_settings, vo.id, vo.vizinput_id from visualizations_vizoutput as vo
                            join (select MAX(score) as score, viztype_id from visualizations_vizoutput as vot
                            where vot.vizinput_id in (%s) and (%s) and vot.viztype_id in (%s) group by vot.viztype_id) as maxi on maxi.score = vo.score
                            and maxi.viztype_id = vo.viztype_id
                            where vo.vizinput_id in (%s) and vo.viztype_id in (%s)
                            """ % (str_vizinputs, mark_settings_str, str_viztypes, str_vizinputs, str_viztypes)
                if limit_nb_viz > 1:
                    cond_score = " vot.score >= "+str(threshold)
                    query = """select vot.score, vot.viztype_id, vot.mark_settings, vot.id, vot.vizinput_id from visualizations_vizoutput as vot
                                where vot.vizinput_id in (%s) and (%s) and vot.viztype_id in (%s) and (%s)
                                """ % (str_vizinputs, mark_settings_str, str_viztypes, cond_score)
                cursor.execute(query)
                rows = cursor.fetchall()

                if len(rows) == 0 and visualization_action == "recommend_viz1" and "mark_settings_str" in result:
                    print("Not taking in account mark_str")
                    need_marks = 1
                    query = """select vo.score, vo.viztype_id, vo.mark_settings, vo.id, vo.vizinput_id from visualizations_vizoutput as vo
                                join (select MAX(score) as score, viztype_id from visualizations_vizoutput as vot
                                where vot.vizinput_id in (%s) and vot.viztype_id in (%s) group by vot.viztype_id) as maxi on maxi.score = vo.score
                                and maxi.viztype_id = vo.viztype_id
                                where vo.vizinput_id in (%s) and vo.viztype_id in (%s)
                                """ % (str_vizinputs, str_viztypes, str_vizinputs, str_viztypes)
                    if limit_nb_viz > 1:
                        cond_score = " vo.score >= "+str(threshold)
                        query = """select vo.score, vo.viztype_id, vo.mark_settings, vo.id, vo.vizinput_id from visualizations_vizoutput as vo
                                    where vo.vizinput_id in (%s) and vo.viztype_id in (%s) order by vo.score desc
                                    """ % (str_vizinputs, str_viztypes, str_viztypes)
                    cursor.execute(query)
                    rows = cursor.fetchall()

                all_data_viztypes = {}
                #all_rows = []
                my_inc = 0
                for row in rows:
                    #if row[1] not in all_rows:
                    #    all_rows.append(row[1])
                    all_data_viztypes[str(my_inc)+"##"+str(row[1])]= {'score': float(all_viztypes[row[1]]), 'mark_settings':row[2], 'type_viz':row[1], 'viz_output':row[3]
                    , 'viz_input':row[4], 'user_score':float(row[0])}
                    my_inc = my_inc + 1
                    if my_inc >= limit_nb_viz:
                        break

                for keycomb, viz in all_data_viztypes.items():
                    #print(viz)
                    key_all = keycomb.split("##")
                    key = key_all[1]
                    need_reload = 0
                    plus = request.session["nb_recommend_graph"] + 1

                    graph_result = copy.deepcopy(result)
                    new_viztypemarks = viztypemarks
                    type_viz = int(key)
                    graph_result["final_graph_parameters"]["type_viz"] = type_viz
                    #new_viztypemarks = new_viztypemarks.replace("viztypeid", str(key))
                    #print(new_viztypemarks)
                    graph_result["previous_viz"] = viz
                    graph_result["final_graph_parameters"]["visualization_code"] += str(plus)
                    graph_result["score_settings"] = score_settings

                    if need_marks == 1:
                        graph_result["analysis_dimensions"] = []
                        graph_result["analysis_measures"] = []
                        graph_result["analysis_size"] = []
                        mark_settings = viz['mark_settings']
                        mark_settings = json.loads(mark_settings)
                        #print(mark_settings)
                        used_meas = []
                        used_dim = []
                        for keymark, valmark in mark_settings.items():
                            graph_result["final_graph_parameters"]["vzm"+str(keymark)] = []
                            for valm in valmark:
                                if type_viz in settings.MAP_VIZ:
                                    for att in graph_result["final_graph_parameters"]["attribs"]:
                                        if "real_datatype" in valm and ((int(valm["real_datatype"]) not in [settings.LAT_DATATYPE,settings.LON_DATATYPE,settings.SHAPE_DATATYPE,settings.POINT_DATATYPE]) or (int(att["dt"]) == int(valm["real_datatype"]) and int(valm["real_datatype"]) in [settings.LAT_DATATYPE,settings.LON_DATATYPE,settings.SHAPE_DATATYPE,settings.POINT_DATATYPE])) and "vzm" not in att["target"]:
                                            att["target"] = "vzm"+str(keymark)
                                            new_viztypemarks = new_viztypemarks.replace("vti-"+att["col_name"], str(keymark))
                                            graph_result["final_graph_parameters"]["vzm"+str(keymark)].append(att)
                                            if str(keymark) == settings.VIZ_Y:
                                                graph_result["analysis_measures"].append(att["analysis"])
                                            elif str(keymark) == settings.VIZ_SIZE:
                                                graph_result["analysis_size"].append(att["analysis"])
                                            else:
                                                graph_result["analysis_dimensions"].append(att["analysis"])
                                            break
                                else:
                                    if str(keymark) == settings.VIZ_ORIENTATION and "orientation" in valm:
                                        graph_result["final_graph_parameters"]["viz_orientation"] = valm["orientation"]
                                    if str(keymark) == settings.VIZ_GROUPING and "grouping" in valm:
                                        graph_result["final_graph_parameters"]["viz_grouping"] = valm["grouping"]
                                    elif str(keymark) in [settings.VIZ_Y, settings.VIZ_SIZE]:
                                        for k, v in order_meas.items():
                                            if k not in used_meas and ("order" in valm) and ("order" in v) and int(v["order"]) == int(valm["order"]):
                                                for att in graph_result["final_graph_parameters"]["attribs"]:
                                                    if att["col_name"] == k:
                                                        used_meas.append(k)
                                                        if att["dimmeasopt"] != valm["option"]:
                                                            if type_viz in settings.NOT_SUPPORTED_AVG and att["dimmeasopt"] == "avg":
                                                                att["dimmeasopt"] = settings.DEFAULT_AGG
                                                                need_reload = 1
                                                            #elif valm["option"] == "valexact":
                                                            #    att["dimmeasopt"] = "valexact"
                                                            #    need_reload = 1
                                                        att["target"] = "vzm"+str(keymark)
                                                        new_viztypemarks = new_viztypemarks.replace("vti-"+k, str(keymark))
                                                        graph_result["final_graph_parameters"]["vzm"+str(keymark)].append(att)
                                                        if str(keymark) == settings.VIZ_Y:
                                                            graph_result["analysis_measures"].append(att["analysis"])
                                                        else:
                                                            graph_result["analysis_size"].append(att["analysis"])
                                                        break
                                                break
                                    else:
                                        for k, v in order_dim.items():
                                            if k not in used_dim and ("order" in valm) and ("order" in v) and int(v["order"]) == int(valm["order"]):
                                                for att in graph_result["final_graph_parameters"]["attribs"]:
                                                    if att["col_name"] == k:
                                                        used_dim.append(k)
                                                        if (att["type"] == "float64" or att["type"] == "int64") and valm["coltype"] == settings.ALL_TYPES[0]:
                                                            #print(att["dimmeasopt"]+"====---------------------==="+valm["option"])
                                                            if att["dimmeasopt"] != valm["option"]:
                                                                if valm["option"] == "bins":
                                                                    att["bins"] = settings.DEFAULT_BINS
                                                                elif att["dimmeasopt"] == "bins":
                                                                    del att["bins"]
                                                                att["dimmeasopt"] = valm["option"]
                                                                need_reload = 1
                                                        att["target"] = "vzm"+str(keymark)
                                                        new_viztypemarks = new_viztypemarks.replace("vti-"+k, str(keymark))
                                                        graph_result["final_graph_parameters"]["vzm"+str(keymark)].append(att)
                                                        graph_result["analysis_dimensions"].append(att["analysis"])
                                                        break
                                                break
                        #print("===============================================")
                        #print(graph_result)
                        if len(used_meas) != len(order_meas.keys()) and type_viz not in settings.MAP_VIZ:
                            include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
                            include_marks = include_marks.split(",")
                            if str(settings.VIZ_Y) in include_marks:
                                for k, v in order_meas.items():
                                    if k not in used_meas:
                                        for att in graph_result["final_graph_parameters"]["attribs"]:
                                            if att["col_name"] == k:
                                                keymark = str(settings.VIZ_Y)
                                                if "option" in valm and att["dimmeasopt"] != valm["option"]:
                                                    if type_viz in settings.NOT_SUPPORTED_AVG and att["dimmeasopt"] == "avg":
                                                        att["dimmeasopt"] = settings.DEFAULT_AGG
                                                        need_reload = 1
                                                    #elif valm["option"] == "valexact":
                                                    #    att["dimmeasopt"] = "valexact"
                                                    #    need_reload = 1
                                                att["target"] = "vzm"+str(keymark)
                                                new_viztypemarks = new_viztypemarks.replace("vti-"+k, str(keymark))
                                                graph_result["final_graph_parameters"]["vzm"+str(keymark)].append(att)
                                                graph_result["analysis_measures"].append(att["analysis"])
                                                break
                            elif str(settings.VIZ_HIERACHY) in include_marks:
                                for k, v in order_dim.items():
                                    if k not in used_dim:
                                        for att in graph_result["final_graph_parameters"]["attribs"]:
                                            if att["col_name"] == k:
                                                keymark = str(settings.VIZ_HIERACHY)
                                                att["target"] = "vzm"+str(keymark)
                                                new_viztypemarks = new_viztypemarks.replace("vti-"+k, str(keymark))
                                                graph_result["final_graph_parameters"]["vzm"+str(keymark)].append(att)
                                                graph_result["analysis_dimensions"].append(att["analysis"])
                                                break

                        if len(used_dim) != len(order_dim.keys()) and type_viz not in settings.MAP_VIZ:
                            include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
                            include_marks = include_marks.split(",")
                            if str(settings.VIZ_HIERACHY) in include_marks:
                                for k, v in order_dim.items():
                                    if k not in used_dim:
                                        for att in graph_result["final_graph_parameters"]["attribs"]:
                                            if att["col_name"] == k:
                                                keymark = str(settings.VIZ_HIERACHY)
                                                att["target"] = "vzm"+str(keymark)
                                                new_viztypemarks = new_viztypemarks.replace("vti-"+k, str(keymark))
                                                graph_result["final_graph_parameters"]["vzm"+str(keymark)].append(att)
                                                graph_result["analysis_dimensions"].append(att["analysis"])
                                                break

                    graph_result["viztypemarks"] = new_viztypemarks
                    visualization_code = graph_result["final_graph_parameters"]["visualization_code"]
                    isin = False

                    list_rec_graph = copy.deepcopy(request.session["recommend_graph"])
                    if "alter_data" in request.session and bool(request.session["alter_data"]):
                        list_rec_graph["alter"] = request.session["alter_data"]

                    for vzcd, vzval in list_rec_graph.items():
                        #print(vzcd+"--"+graph_result["final_graph_parameters"]["visualization_code"])
                        #print(str(vzval["final_graph_parameters"]["type_viz"])+"--"+str(graph_result["final_graph_parameters"]["type_viz"]))
                        if vzval["final_graph_parameters"]["type_viz"] == graph_result["final_graph_parameters"]["type_viz"]:
                            yes = False
                            if vzval["viztypemarks"] == graph_result["viztypemarks"]:
                                yes = True
                            if not yes:
                                arrvzval = vzval["viztypemarks"].split("**")
                                finvzval = []
                                for v in arrvzval:
                                    if v[-2:] != "__":
                                        finvzval.append(v)

                                arrgrh = graph_result["viztypemarks"].split("**")
                                fingrh = []
                                for v in arrgrh:
                                    if v[-2:] != "__":
                                        fingrh.append(v)
                                if (collections.Counter(finvzval) == collections.Counter(fingrh)):
                                    yes = True

                            if yes:
                                vzori = vzval["final_graph_parameters"]["viz_orientation"]
                                if vzori is None or vzori == "":
                                    vzori = "h"
                                grori = graph_result["final_graph_parameters"]["viz_orientation"]
                                if grori is None or grori == "":
                                    grori = "h"
                                vzgrp = vzval["final_graph_parameters"]["viz_grouping"]
                                if vzgrp is None or vzgrp == "":
                                    vzgrp = "group"
                                grgrp = graph_result["final_graph_parameters"]["viz_grouping"]
                                if grgrp is None or grgrp == "":
                                    grgrp = "group"
                                if vzori == grori and vzgrp == grgrp:
                                    isin = True
                                    break
                    if not isin:
                        request.session["nb_recommend_graph"] = plus
                        request.session["recommend_graph"][visualization_code] = graph_result
                        request.session["recommend_graph"][visualization_code]["need_reload"] = need_reload
                    #print("===============================================")
                    #print(visualization_code)
                    #print(graph_result["final_graph_parameters"])
            if need_second and limit_nb_viz > 1 and not isin:
                recommend_graph(request, graph_parameters, add_end, limit_nb_viz, True)
            elif len(result["col_temp"]) > 0 and limit_nb_viz > 1 and not convert_temp and max_temp_elments <= settings.MAX_DISTINCT_CAT_TEMP and not isin:
                recommend_graph(request, graph_parameters, add_end, limit_nb_viz, option_group, True)
            elif add_end:
                request.session["end_recommend_graph"] = 1
        else:
            if need_second:
                recommend_graph(request, graph_parameters, add_end, limit_nb_viz, True)
            elif len(result["col_temp"]) > 0 and not convert_temp:
                recommend_graph(request, graph_parameters, add_end, limit_nb_viz, option_group, True)
            elif add_end:
                request.session["end_recommend_graph"] = 1
        data = {'success': True, 'nb_recommend_graph': request.session["nb_recommend_graph"]}
                #print(all_viztypes)
    except Exception as e:
        if need_second:
            recommend_graph(request, graph_parameters, add_end, limit_nb_viz, True)
        elif len(result["col_temp"]) > 0 and not convert_temp:
            recommend_graph(request, graph_parameters, add_end, limit_nb_viz, option_group, True)
        elif add_end:
            request.session["end_recommend_graph"] = 1
        print('Error details: '+ str(e))
        data = {'success': False, 'message': _("Something went wrong")}
    return data

def create_formula_features(request, vizinputs, feature_keys):
    all_code = ""
    for vizinput in vizinputs:
        list_features = []
        for key, feat in vizinput.feature_settings.items():
            if key in feature_keys:
                list_features.append(feat)
        if len(list_features) > 0:
            formula = "if " + " and ".join(list_features) + " : \n"
            formula += "   list_vizinputs.append('" + str(vizinput.id) + "') \n"
            all_code += str(formula)
    return all_code


#generate query from data
def recommend_query(request, graph_parameters):
    # get the parameters
    data_operator = graph_parameters['data_operator'] or 'and'
    datakeep_operator = graph_parameters['datakeep_operator'] or 'keep'
    file_code = graph_parameters['files'][0]

    data = {"final_query": None, "graph_parameters": None}
    current_project = request.session["current_project"]
    type_viz = graph_parameters['type_viz']

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
    print("final_query=============================")
    print(final_query)
    return data

def init_vizinputs(request):
    load_data(request, VizType, "list_viztypes", 0)
    load_data(request, Feature, "list_features", 0)
    vizinputs = VizInput.objects.all().prefetch_related('vizoutputs')
    for vizinput in vizinputs:
        feature_settings = {}
        viz_score_settings = vizinput.value
        score_settings = viz_score_settings.split("**")
        array_insights = []
        for score_setting in score_settings:
            get_items = score_setting.split("_")
            formula = ""
            apply_onlyto_viz = request.session["list_features"][str(get_items[0])]["apply_onlyto_viz"]
            feat_name = request.session["list_features"][str(get_items[0])]["name"]

            if get_items[1]:
                vals = []
                if len(get_items) == 3:
                    vals = get_items[2].split("#")
                if get_items[1] == "isbetween" and len(vals) == 2 and len(vals[0]) > 0 and len(vals[1]) > 0:
                    ins = feat_name+" >= "+str(vals[0])+" and "+feat_name+" <= "+str(vals[1])
                    array_insights.append(ins)
                elif get_items[1] in ["istrue", "isfalse"]:
                    ins = feat_name+" "+settings.OPERATOR_CORRESPONDANTS[str(get_items[1])]
                    array_insights.append(ins)
                elif len(vals) == 1 and len(vals[0]) > 0:
                    ins = feat_name+" "+settings.OPERATOR_CORRESPONDANTS[str(get_items[1])]+" "+str(vals[0])
                    array_insights.append(ins)

        insight = ""
        input_scores = ""
        if len(array_insights) > 0:
            insight = "\n".join(array_insights)

        vizinput.insight = insight
        for vizoutput in vizinput.vizoutputs.all():
            mark_settings = vizoutput.mark_settings
            mark_settings_str = ""
            for key, val in mark_settings.items():
                for ite in val:
                    if key != settings.VIZ_ORIENTATION and key != settings.VIZ_GROUPING:
                        mark_settings_str = mark_settings_str + str(key)+"__"+str(ite["coltype"])+"__"+str(ite["option"])

            vizoutput.mark_settings_str = mark_settings_str
            vizoutput.save(update_fields=['mark_settings_str'])
            input_scores = input_scores + request.session["list_viztypes"][str(vizoutput.viztype_id)]["name"]+":"+str(vizoutput.score)+"\n"

        vizinput.scores = input_scores
        vizinput.save(update_fields=['insight', 'scores'])

    return True

#generate distribution visualization
def generate_dist_viz(request, graph_parameters, require_div=True, require_analysis=True):
    # get the parameters
    file_code = graph_parameters['files'][0]

    visualization_action = graph_parameters["visualization_action"]

    result = None
    plot_div = None

    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    if not current_project:
        return data
    try:
    #if True:
        all_stat = current_project["project_settings"]["files"][file_code]["all_stat"]
        columns = current_project["project_settings"]["files"][file_code]["columns"]
        len_cat = len(all_stat["col_cat"])
        len_num = len(all_stat["col_num"])
        len_geo = len(all_stat["col_geo"])
        att_cat_sup = []
        all_buble = []
        col_lat = None
        col_lon = None
        col_shape = None
        col_point = None

        if len_geo > 0:
            for i in range(len_geo):
                col = all_stat["col_geo"][str(i)]
                datatype = columns[col]["datatype"]
                if datatype == settings.LAT_DATATYPE:
                    col_lat = col
                elif datatype == settings.LON_DATATYPE:
                    col_lon = col
                elif datatype == settings.SHAPE_DATATYPE:
                    col_shape = col
                elif datatype == settings.POINT_DATATYPE:
                    col_point = col

        #Geographical data
        if col_lat is not None and col_lon is not None:
            i = 0
            special_graph_parameters = {}
            special_graph_parameters = copy.deepcopy(graph_parameters)
            special_graph_parameters["visualization_action"] = "recommend_viz"
            special_graph_parameters["add_marg_score"] = 80 + int(i)
            special_graph_parameters['attribs'] = []
            col = col_lat
            attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
            'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
            special_graph_parameters['attribs'].append(attr_cat)
            col = col_lon
            attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
            'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
            special_graph_parameters['attribs'].append(attr_cat)
            try:
                data = recommend_graph(request, special_graph_parameters, False, 1)
            except Exception as e:
                print('Error details (Recommend Graph): '+ str(e))

        if col_shape is not None:
            i = 0
            special_graph_parameters = {}
            special_graph_parameters = copy.deepcopy(graph_parameters)
            special_graph_parameters["visualization_action"] = "recommend_viz"
            special_graph_parameters["add_marg_score"] = 80 + int(i)
            special_graph_parameters['attribs'] = []
            col = col_shape
            attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
            'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
            special_graph_parameters['attribs'].append(attr_cat)

            try:
                data = recommend_graph(request, special_graph_parameters, False, 1)
            except Exception as e:
                print('Error details (Recommend Graph): '+ str(e))

        if col_point is not None:
            i = 0
            special_graph_parameters = {}
            special_graph_parameters = copy.deepcopy(graph_parameters)
            special_graph_parameters["visualization_action"] = "recommend_viz"
            special_graph_parameters["add_marg_score"] = 80 + int(i)
            special_graph_parameters['attribs'] = []
            col = col_point
            attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
            'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
            special_graph_parameters['attribs'].append(attr_cat)

            try:
                data = recommend_graph(request, special_graph_parameters, False, 1)
            except Exception as e:
                print('Error details (Recommend Graph): '+ str(e))

        for i in range(len_cat):
            col = all_stat["col_cat"][str(i)]
            datatype = columns[col]["datatype"]
            if all_stat["stat"][col]["nb_distinct"] > 1:
                if int(datatype) in settings.GOOD_CAT_DATATYPES and all_stat["stat"][col]["nb_total"] != all_stat["stat"][col]["nb_distinct"]:
                    special_graph_parameters = copy.deepcopy(graph_parameters)
                    special_graph_parameters["visualization_action"] = "recommend_viz"
                    special_graph_parameters["add_marg_score"] = 55 + int(i)
                    special_graph_parameters['attribs'] = []
                    attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                    'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                    special_graph_parameters['attribs'].append(attr_cat)
                    if all_stat["stat"][col]["nb_distinct"] <= settings.MAX_DISTINCT_CAT and all_stat["stat"][col]["nb_distinct"] > 1:
                        att_cat_sup.append(attr_cat)
                    special_graph_parameters['attribs'].append({'fulltext': 'count', 'dimmeasopt': 'valexact', 'file': file_code, 'dt': 0,
                    'realtype': 'auto', 'name': 'count', 'type': 'auto', 'ty': 'meas', 'target': 'attribs'})
                    try:
                        data = recommend_graph(request, special_graph_parameters, False, 1)
                    except Exception as e:
                        print('Error details (Recommend Graph): '+ str(e))

        for i in range(len_num):
            col = all_stat["col_num"][str(len_num-i-1)]
            special_graph_parameters = copy.deepcopy(graph_parameters)
            special_graph_parameters["visualization_action"] = "recommend_viz"
            special_graph_parameters["add_marg_score"] = 50 + int(len_num-i-1)
            special_graph_parameters['attribs'] = []
            special_graph_parameters['attribs'].append({'fulltext': col+"(bins:"+str(settings.DEFAULT_BINS)+")", 'dimmeasopt': 'bins', 'bins':settings.DEFAULT_BINS, 'file': file_code, 'dt': request.session["measures"][file_code][col]["dt_id"],
            'realtype': request.session["measures"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["measures"][file_code][col]["dt_pd"], 'ty': 'meas', 'target': 'attribs'})
            special_graph_parameters['attribs'].append({'fulltext': 'count', 'dimmeasopt': 'valexact', 'file': file_code, 'dt': 0,
            'realtype': 'auto', 'name': 'count', 'type': 'auto', 'ty': 'meas', 'target': 'attribs'})
            try:
                data = recommend_graph(request, special_graph_parameters, False, 1)
            except Exception as e:
                print('Error details (Recommend Graph): '+ str(e))

            if all_stat["stat"][col]["corr"]["nb_corr"] >= 1 and i < (len_num-1):
                for j in range(i+1,len_num):
                    col2 = all_stat["col_num"][str(len_num-j-1)]
                    if all_stat["stat"][col]["corr"][col2] >= settings.GOOD_CORR:
                        special_graph_parameters["visualization_action"] = "recommend_viz"
                        special_graph_parameters["add_marg_score"] = 40 + int(len_num-i-1) + int(len_num-j-1)
                        special_graph_parameters['attribs'] = []
                        special_graph_parameters['attribs'].append({'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["measures"][file_code][col]["dt_id"],
                        'realtype': request.session["measures"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["measures"][file_code][col]["dt_pd"], 'ty': 'meas', 'target': 'attribs'})
                        special_graph_parameters['attribs'].append({'fulltext': col2, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["measures"][file_code][col2]["dt_id"],
                        'realtype': request.session["measures"][file_code][col2]["dt_abbr"], 'name': col2, 'type': request.session["measures"][file_code][col2]["dt_pd"], 'ty': 'meas', 'target': 'attribs'})
                        if len(att_cat_sup) > 0:
                            special_graph_parameters['attribs'].append(att_cat_sup[random.randrange(len(att_cat_sup))])
                        try:
                            data = recommend_graph(request, special_graph_parameters, False, 1)
                        except Exception as e:
                            print('Error details (Recommend Graph): '+ str(e))

                        """for t in range(len_num):
                            if t != i and t != j:
                                bulle = [i, j, t]
                                bulle.sort()
                                str_buble = str(bulle[0])+"#"+str(bulle[1])+"#"+str(bulle[2])
                                if str_buble not in all_buble:
                                    all_buble.append(str_buble)
                                    col3 = all_stat["col_num"][str(len_num-t-1)]
                                    if all_stat["stat"][col]["corr"][col3] < settings.GOOD_CORR or all_stat["stat"][col]["corr"][col3] >= settings.GOOD_CORR:
                                        special_graph_parameters["add_marg_score"] = 30 + int(len_num-i-1) + int(len_num-j-1) + int(t)
                                        special_graph_parameters['attribs'].append({'fulltext': col3, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["measures"][file_code][col3]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col3]["dt_abbr"], 'name': col3, 'type': request.session["measures"][file_code][col3]["dt_pd"], 'ty': 'meas', 'target': 'attribs'})
                                        try:
                                            data = recommend_graph(request, special_graph_parameters, False, 1)
                                        except Exception as e:
                                            print('Error details (Recommend Graph): '+ str(e))"""


        request.session["end_recommend_graph"] = 1
        data = {'success': True, 'nb_recommend_graph': request.session["nb_recommend_graph"]}
    except Exception as e:
        request.session["end_recommend_graph"] = 1
        print('Error details: '+ str(e))
        data = {'success': False, 'message': _("Something went wrong")}
    return data

#generate analysis visualization
def generate_analysis_viz(request, graph_parameters, require_div=True, require_analysis=True):
    # get the parameters
    file_code = graph_parameters['files'][0]

    visualization_action = graph_parameters["visualization_action"]

    result = None
    plot_div = None

    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    if not current_project:
        return data
    try:
    #if True:
        all_stat = current_project["project_settings"]["files"][file_code]["all_stat"]
        columns = current_project["project_settings"]["files"][file_code]["columns"]
        len_cat = len(all_stat["col_cat"])
        len_num = len(all_stat["col_num"])
        len_temp = len(all_stat["col_temp"])
        len_geo = len(all_stat["col_geo"])
        att_cat_sup = []
        all_buble = []
        meas_ord = {}
        list_agg = settings.LIST_AGG
        #list_agg = ["sum", "sum"]
        num_keys = []
        num_vals = []
        col_lat = None
        col_lon = None
        col_shape = None
        col_point = None

        if len_num > 1:
            col_meas = all_stat["col_num"][str(len_num-1)]
            for key, val in all_stat["stat"][col_meas]["corr"].items():
                if key not in ["nb_corr", "tot_corr"]:
                    num_keys.append(key)
                    num_vals.append(val)
            array = np.array(num_vals)
            temp = array.argsort()
            ranks = np.empty_like(temp)
            ranks[temp] = np.arange(len(array))
            key = 0
            for val in num_keys:
                meas_ord[str(ranks[key])] = val
                key += 1

        if len_geo > 0:
            for i in range(len_geo):
                col = all_stat["col_geo"][str(i)]
                datatype = columns[col]["datatype"]
                if datatype == settings.LAT_DATATYPE:
                    col_lat = col
                elif datatype == settings.LON_DATATYPE:
                    col_lon = col
                elif datatype == settings.SHAPE_DATATYPE:
                    col_shape = col
                elif datatype == settings.POINT_DATATYPE:
                    col_point = col

        if len_num > 0 :
            #Geographical data
            if col_lat is not None and col_lon is not None:
                i = 0
                backup_special_graph_parameters = []
                special_graph_parameters = {}
                if True:
                    special_graph_parameters = copy.deepcopy(graph_parameters)
                    special_graph_parameters["visualization_action"] = "recommend_viz"
                    special_graph_parameters["add_marg_score"] = 80 + int(i)
                    special_graph_parameters['attribs'] = []
                    col = col_lat
                    attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                    'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                    special_graph_parameters['attribs'].append(attr_cat)
                    col = col_lon
                    attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                    'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                    special_graph_parameters['attribs'].append(attr_cat)
                    backup_special_graph_parameters = copy.deepcopy(special_graph_parameters)

                    col_meas = all_stat["col_num"][str(len_num-1)]
                    agg = list_agg[random.randrange(len(list_agg))]
                    special_graph_parameters['attribs'].append({'fulltext': col_meas+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col_meas]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col_meas]["dt_abbr"], 'name': col_meas, 'type': request.session["measures"][file_code][col_meas]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                    try:
                        data = recommend_graph(request, special_graph_parameters, False, 1)
                    except Exception as e:
                        print('Error details (Recommend Graph): '+ str(e))

                    if len(num_vals) > 0 and all_stat["stat"][col_meas]["corr"][meas_ord["0"]] <= settings.VERY_GOOD_CORR:
                        special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                        col2 = meas_ord["0"]
                        special_graph_parameters["add_marg_score"] = 60 + int(i)
                        special_graph_parameters['attribs'].append({'fulltext': col2+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col2]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col2]["dt_abbr"], 'name': col2, 'type': request.session["measures"][file_code][col2]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                        try:
                            data = recommend_graph(request, special_graph_parameters, False, 1)
                        except Exception as e:
                            print('Error details (Recommend Graph): '+ str(e))

                        if len(num_vals) > 1 and all_stat["stat"][col_meas]["corr"][meas_ord["1"]] <= settings.VERY_GOOD_CORR:
                            special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                            col3 = meas_ord["1"]
                            special_graph_parameters["add_marg_score"] = 40 + int(i)
                            special_graph_parameters['attribs'].append({'fulltext': col3+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col3]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col3]["dt_abbr"], 'name': col3, 'type': request.session["measures"][file_code][col3]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                            try:
                                data = recommend_graph(request, special_graph_parameters, False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))

                            if len(num_vals) > 2 and all_stat["stat"][col_meas]["corr"][meas_ord["2"]] <= settings.VERY_GOOD_CORR:
                                special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                                col4 = meas_ord["2"]
                                special_graph_parameters["add_marg_score"] = 30 + int(i)
                                special_graph_parameters['attribs'].append({'fulltext': col4+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col4]["dt_id"],
                                                'realtype': request.session["measures"][file_code][col4]["dt_abbr"], 'name': col4, 'type': request.session["measures"][file_code][col4]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                try:
                                    data = recommend_graph(request, special_graph_parameters, False, 1)
                                except Exception as e:
                                    print('Error details (Recommend Graph): '+ str(e))


            """if col_shape is not None:
                i = 0
                backup_special_graph_parameters = []
                special_graph_parameters = {}
                if True:
                    special_graph_parameters = copy.deepcopy(graph_parameters)
                    special_graph_parameters["visualization_action"] = "recommend_viz"
                    special_graph_parameters["add_marg_score"] = 80 + int(i)
                    special_graph_parameters['attribs'] = []
                    col = col_shape
                    attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                    'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                    special_graph_parameters['attribs'].append(attr_cat)
                    backup_special_graph_parameters = copy.deepcopy(special_graph_parameters)

                    col_meas = all_stat["col_num"][str(len_num-1)]
                    agg = list_agg[random.randrange(len(list_agg))]
                    special_graph_parameters['attribs'].append({'fulltext': col_meas+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col_meas]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col_meas]["dt_abbr"], 'name': col_meas, 'type': request.session["measures"][file_code][col_meas]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                    try:
                        data = recommend_graph(request, special_graph_parameters, False, 1)
                    except Exception as e:
                        print('Error details (Recommend Graph): '+ str(e))

                    if len(num_vals) > 0 and all_stat["stat"][col_meas]["corr"][meas_ord["0"]] <= settings.VERY_GOOD_CORR:
                        special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                        col2 = meas_ord["0"]
                        special_graph_parameters["add_marg_score"] = 60 + int(i)
                        special_graph_parameters['attribs'].append({'fulltext': col2+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col2]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col2]["dt_abbr"], 'name': col2, 'type': request.session["measures"][file_code][col2]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                        try:
                            data = recommend_graph(request, special_graph_parameters, False, 1)
                        except Exception as e:
                            print('Error details (Recommend Graph): '+ str(e))

                        if len(num_vals) > 1 and all_stat["stat"][col_meas]["corr"][meas_ord["1"]] <= settings.VERY_GOOD_CORR:
                            special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                            col3 = meas_ord["1"]
                            special_graph_parameters["add_marg_score"] = 50 + int(i)
                            special_graph_parameters['attribs'].append({'fulltext': col3+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col3]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col3]["dt_abbr"], 'name': col3, 'type': request.session["measures"][file_code][col3]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                            try:
                                data = recommend_graph(request, special_graph_parameters, False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))

                            if len(num_vals) > 2 and all_stat["stat"][col_meas]["corr"][meas_ord["2"]] <= settings.VERY_GOOD_CORR:
                                special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                                col4 = meas_ord["2"]
                                special_graph_parameters["add_marg_score"] = 40 + int(i)
                                special_graph_parameters['attribs'].append({'fulltext': col4+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col4]["dt_id"],
                                                'realtype': request.session["measures"][file_code][col4]["dt_abbr"], 'name': col4, 'type': request.session["measures"][file_code][col4]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                try:
                                    data = recommend_graph(request, special_graph_parameters, False, 1)
                                except Exception as e:
                                    print('Error details (Recommend Graph): '+ str(e))"""

            if col_point is not None:
                i = 0
                backup_special_graph_parameters = []
                special_graph_parameters = {}
                if True:
                    special_graph_parameters = copy.deepcopy(graph_parameters)
                    special_graph_parameters["visualization_action"] = "recommend_viz"
                    special_graph_parameters["add_marg_score"] = 80 + int(i)
                    special_graph_parameters['attribs'] = []
                    col = col_point
                    attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                    'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                    special_graph_parameters['attribs'].append(attr_cat)
                    backup_special_graph_parameters = copy.deepcopy(special_graph_parameters)

                    col_meas = all_stat["col_num"][str(len_num-1)]
                    agg = list_agg[random.randrange(len(list_agg))]
                    special_graph_parameters['attribs'].append({'fulltext': col_meas+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col_meas]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col_meas]["dt_abbr"], 'name': col_meas, 'type': request.session["measures"][file_code][col_meas]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                    try:
                        data = recommend_graph(request, special_graph_parameters, False, 1)
                    except Exception as e:
                        print('Error details (Recommend Graph): '+ str(e))

                    if len(num_vals) > 0 and all_stat["stat"][col_meas]["corr"][meas_ord["0"]] <= settings.VERY_GOOD_CORR:
                        special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                        col2 = meas_ord["0"]
                        special_graph_parameters["add_marg_score"] = 60 + int(i)
                        special_graph_parameters['attribs'].append({'fulltext': col2+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col2]["dt_id"],
                                        'realtype': request.session["measures"][file_code][col2]["dt_abbr"], 'name': col2, 'type': request.session["measures"][file_code][col2]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                        try:
                            data = recommend_graph(request, special_graph_parameters, False, 1)
                        except Exception as e:
                            print('Error details (Recommend Graph): '+ str(e))

                        if len(num_vals) > 1 and all_stat["stat"][col_meas]["corr"][meas_ord["1"]] <= settings.VERY_GOOD_CORR:
                            special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                            col3 = meas_ord["1"]
                            special_graph_parameters["add_marg_score"] = 50 + int(i)
                            special_graph_parameters['attribs'].append({'fulltext': col3+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col3]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col3]["dt_abbr"], 'name': col3, 'type': request.session["measures"][file_code][col3]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                            try:
                                data = recommend_graph(request, special_graph_parameters, False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))

                            if len(num_vals) > 2 and all_stat["stat"][col_meas]["corr"][meas_ord["2"]] <= settings.VERY_GOOD_CORR:
                                special_graph_parameters = copy.deepcopy(backup_special_graph_parameters)
                                col4 = meas_ord["2"]
                                special_graph_parameters["add_marg_score"] = 40 + int(i)
                                special_graph_parameters['attribs'].append({'fulltext': col4+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col4]["dt_id"],
                                                'realtype': request.session["measures"][file_code][col4]["dt_abbr"], 'name': col4, 'type': request.session["measures"][file_code][col4]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                try:
                                    data = recommend_graph(request, special_graph_parameters, False, 1)
                                except Exception as e:
                                    print('Error details (Recommend Graph): '+ str(e))
            # Categorical variables
            for i in range(len_cat):
                col = all_stat["col_cat"][str(len_cat-i-1)]
                if all_stat["stat"][col]["nb_distinct"] > 1:
                    datatype = columns[col]["datatype"]
                    special_graph_parameters = {}
                    special_graph_parameters_d2_m1 = {}
                    special_graph_parameters_d3_m1 = {}
                    special_graph_parameters_d4_m1 = {}
                    conserv1 = []
                    conserv2 = []
                    conserv3 = []
                    conserv4 = []
                    if int(datatype) in settings.GOOD_CAT_DATATYPES:
                        special_graph_parameters = copy.deepcopy(graph_parameters)
                        special_graph_parameters["visualization_action"] = "recommend_viz"
                        special_graph_parameters["add_marg_score"] = 70 + int(i)
                        special_graph_parameters['attribs'] = []
                        attr_cat = {'fulltext': col, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                        'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                        special_graph_parameters['attribs'].append(attr_cat)

                        col_meas = all_stat["col_num"][str(len_num-1)]
                        agg = list_agg[random.randrange(len(list_agg))]
                        special_graph_parameters['attribs'].append({'fulltext': col_meas+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col_meas]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col_meas]["dt_abbr"], 'name': col_meas, 'type': request.session["measures"][file_code][col_meas]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                        try:
                            data = recommend_graph(request, special_graph_parameters, False, 1)
                            #conserv1.append(special_graph_parameters)
                        except Exception as e:
                            print('Error details (Recommend Graph): '+ str(e))

                        special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, i, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                        """conserv2.append(special_graph_parameters_d2_m1)
                        conserv3.append(special_graph_parameters_d3_m1)
                        conserv4.append(special_graph_parameters_d4_m1)"""
                        if len(num_vals) > 0 and all_stat["stat"][col_meas]["corr"][meas_ord["0"]] <= settings.VERY_GOOD_CORR:
                            col2 = meas_ord["0"]
                            special_graph_parameters["add_marg_score"] = 60 + int(i)
                            special_graph_parameters['attribs'].append({'fulltext': col2+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col2]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col2]["dt_abbr"], 'name': col2, 'type': request.session["measures"][file_code][col2]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                            try:
                                data = recommend_graph(request, special_graph_parameters, False, 1)
                                #conserv1.append(special_graph_parameters)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                            special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, i, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                            """conserv2.append(special_graph_parameters_d2_m1)
                            conserv3.append(special_graph_parameters_d3_m1)
                            conserv4.append(special_graph_parameters_d4_m1)"""
                            if len(num_vals) > 1 and all_stat["stat"][col_meas]["corr"][meas_ord["1"]] <= settings.VERY_GOOD_CORR:
                                col3 = meas_ord["1"]
                                special_graph_parameters["add_marg_score"] = 50 + int(i)
                                special_graph_parameters['attribs'].append({'fulltext': col3+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col3]["dt_id"],
                                                'realtype': request.session["measures"][file_code][col3]["dt_abbr"], 'name': col3, 'type': request.session["measures"][file_code][col3]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                try:
                                    data = recommend_graph(request, special_graph_parameters, False, 1)
                                    #conserv1.append(special_graph_parameters)
                                except Exception as e:
                                    print('Error details (Recommend Graph): '+ str(e))
                                special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, i, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                                """conserv2.append(special_graph_parameters_d2_m1)
                                conserv3.append(special_graph_parameters_d3_m1)
                                conserv4.append(special_graph_parameters_d4_m1)"""

                                if len(num_vals) > 2 and all_stat["stat"][col_meas]["corr"][meas_ord["2"]] <= settings.VERY_GOOD_CORR:
                                    col4 = meas_ord["2"]
                                    special_graph_parameters["add_marg_score"] = 40 + int(i)
                                    special_graph_parameters['attribs'].append({'fulltext': col4+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col4]["dt_id"],
                                                    'realtype': request.session["measures"][file_code][col4]["dt_abbr"], 'name': col4, 'type': request.session["measures"][file_code][col4]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                    try:
                                        data = recommend_graph(request, special_graph_parameters, False, 1)
                                        #"""conserv1.append(special_graph_parameters)
                                    except Exception as e:
                                        print('Error details (Recommend Graph): '+ str(e))
                                    special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, i, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                                    """conserv2.append(special_graph_parameters_d2_m1)
                                    conserv3.append(special_graph_parameters_d3_m1)
                                    conserv4.append(special_graph_parameters_d4_m1)"""

                    """if len(conserv1) > 0:
                        if bool(conserv1[len(conserv1)-1]):
                            try:
                                data = recommend_graph(request, conserv1[len(conserv1)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                    if len(conserv2) > 0:
                        if conserv2[len(conserv2)-1] != conserv1[len(conserv1)-1] and bool(conserv2[len(conserv2)-1]):
                            try:
                                data = recommend_graph(request, conserv2[len(conserv2)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                    if len(conserv3) > 0:
                        if conserv3[len(conserv3)-1] != conserv2[len(conserv2)-1] and bool(conserv3[len(conserv3)-1]):
                            try:
                                data = recommend_graph(request, conserv3[len(conserv3)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                    if len(conserv4) > 0:
                        if conserv4[len(conserv4)-1] != conserv3[len(conserv3)-1] and bool(conserv4[len(conserv4)-1]):
                            try:
                                data = recommend_graph(request, conserv4[len(conserv4)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))"""

            # Temporal variables
            for i in range(len_temp):
                col = all_stat["col_temp"][str(len_temp-i-1)]
                print(all_stat["stat"][col]["nb_distinct"])
                if all_stat["stat"][col]["nb_distinct"] > 1:
                    datatype = columns[col]["datatype"]
                    special_graph_parameters = {}
                    special_graph_parameters_d2_m1 = {}
                    special_graph_parameters_d3_m1 = {}
                    special_graph_parameters_d4_m1 = {}
                    conserv1 = []
                    conserv2 = []
                    conserv3 = []
                    conserv4 = []
                    if True:
                        special_graph_parameters = copy.deepcopy(graph_parameters)
                        special_graph_parameters["visualization_action"] = "recommend_viz"
                        special_graph_parameters["add_marg_score"] = 70 + int(i)
                        special_graph_parameters['attribs'] = []
                        attr_cat = {'fulltext': col+"("+settings.DEFAULT_DATE_DIM+")", 'dimmeasopt': settings.DEFAULT_DATE_DIM, 'file': file_code, 'dt': request.session["dimensions"][file_code][col]["dt_id"],
                        'realtype': request.session["dimensions"][file_code][col]["dt_abbr"], 'name': col, 'type': request.session["dimensions"][file_code][col]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                        special_graph_parameters['attribs'].append(attr_cat)

                        col_meas = all_stat["col_num"][str(len_num-1)]
                        agg = list_agg[random.randrange(len(list_agg))]
                        special_graph_parameters['attribs'].append({'fulltext': col_meas+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col_meas]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col_meas]["dt_abbr"], 'name': col_meas, 'type': request.session["measures"][file_code][col_meas]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                        try:
                            data = recommend_graph(request, special_graph_parameters, False, 1)
                            #conserv1.append(special_graph_parameters)
                        except Exception as e:
                            print('Error details (Recommend Graph): '+ str(e))

                        special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, -1, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                        """conserv2.append(special_graph_parameters_d2_m1)
                        conserv3.append(special_graph_parameters_d3_m1)
                        conserv4.append(special_graph_parameters_d4_m1)"""
                        if len(num_vals) > 0 and all_stat["stat"][col_meas]["corr"][meas_ord["0"]] <= settings.VERY_GOOD_CORR:
                            col2 = meas_ord["0"]
                            special_graph_parameters["add_marg_score"] = 60 + int(i)
                            special_graph_parameters['attribs'].append({'fulltext': col2+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col2]["dt_id"],
                                            'realtype': request.session["measures"][file_code][col2]["dt_abbr"], 'name': col2, 'type': request.session["measures"][file_code][col2]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                            try:
                                data = recommend_graph(request, special_graph_parameters, False, 1)
                                #conserv1.append(special_graph_parameters)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                            special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, -1, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                            """conserv2.append(special_graph_parameters_d2_m1)
                            conserv3.append(special_graph_parameters_d3_m1)
                            conserv4.append(special_graph_parameters_d4_m1)"""

                            if len(num_vals) > 1 and all_stat["stat"][col_meas]["corr"][meas_ord["1"]] <= settings.VERY_GOOD_CORR:
                                col3 = meas_ord["1"]
                                special_graph_parameters["add_marg_score"] = 50 + int(i)
                                special_graph_parameters['attribs'].append({'fulltext': col3+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col3]["dt_id"],
                                                'realtype': request.session["measures"][file_code][col3]["dt_abbr"], 'name': col3, 'type': request.session["measures"][file_code][col3]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                try:
                                    data = recommend_graph(request, special_graph_parameters, False, 1)
                                    #conserv1.append(special_graph_parameters)
                                except Exception as e:
                                    print('Error details (Recommend Graph): '+ str(e))
                                special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, -1, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                                """conserv2.append(special_graph_parameters_d2_m1)
                                conserv3.append(special_graph_parameters_d3_m1)
                                conserv4.append(special_graph_parameters_d4_m1)"""

                                if len(num_vals) > 2 and all_stat["stat"][col_meas]["corr"][meas_ord["2"]] <= settings.VERY_GOOD_CORR:
                                    col4 = meas_ord["2"]
                                    special_graph_parameters["add_marg_score"] = 40 + int(i)
                                    special_graph_parameters['attribs'].append({'fulltext': col4+"("+agg+")", 'dimmeasopt': agg, 'file': file_code, 'dt': request.session["measures"][file_code][col4]["dt_id"],
                                                    'realtype': request.session["measures"][file_code][col4]["dt_abbr"], 'name': col4, 'type': request.session["measures"][file_code][col4]["dt_pd"], 'ty': 'meas', 'target': 'attribs', 'bins': ''})
                                    try:
                                        data = recommend_graph(request, special_graph_parameters, False, 1)
                                        #conserv1.append(special_graph_parameters)
                                    except Exception as e:
                                        print('Error details (Recommend Graph): '+ str(e))
                                    special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1 = add_more_categorical(request, len_cat, -1, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code)
                                    """conserv2.append(special_graph_parameters_d2_m1)
                                    conserv3.append(special_graph_parameters_d3_m1)
                                    conserv4.append(special_graph_parameters_d4_m1)"""

                    """if len(conserv1) > 0:
                        if bool(conserv1[len(conserv1)-1]):
                            try:
                                data = recommend_graph(request, conserv1[len(conserv1)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                    if len(conserv2) > 0:
                        if conserv2[len(conserv2)-1] != conserv1[len(conserv1)-1] and bool(conserv2[len(conserv2)-1]):
                            try:
                                data = recommend_graph(request, conserv2[len(conserv2)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                    if len(conserv3) > 0:
                        if conserv3[len(conserv3)-1] != conserv2[len(conserv2)-1] and bool(conserv3[len(conserv3)-1]):
                            try:
                                data = recommend_graph(request, conserv3[len(conserv3)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))
                    if len(conserv4) > 0:
                        if conserv4[len(conserv4)-1] != conserv3[len(conserv3)-1] and bool(conserv4[len(conserv4)-1]):
                            try:
                                data = recommend_graph(request, conserv4[len(conserv4)-1], False, 1)
                            except Exception as e:
                                print('Error details (Recommend Graph): '+ str(e))"""


        request.session["end_recommend_graph"] = 1
        data = {'success': True, 'nb_recommend_graph': request.session["nb_recommend_graph"]}
    except Exception as e:
        request.session["end_recommend_graph"] = 1
        print('Error details: '+ str(e))
        data = {'success': False, 'message': _("Something went wrong")}
    return data

#Add more facets to graph
def add_more_categorical(request, len_cat, i, all_stat, special_graph_parameters, special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1, file_code):
    if len_cat >= 1 and 0 < len_cat-i-1 and all_stat["stat"][all_stat["col_cat"]["0"]]["nb_distinct"] <= settings.DINSTICT_CAT_FACET and all_stat["stat"][all_stat["col_cat"]["0"]]["nb_distinct"] > 1:
        special_graph_parameters_d2_m1 = copy.deepcopy(special_graph_parameters)
        special_graph_parameters_d2_m1["add_marg_score"] = special_graph_parameters_d2_m1["add_marg_score"] - 5
        col_add = all_stat["col_cat"]["0"]
        attr_add = {'fulltext': col_add, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col_add]["dt_id"],
        'realtype': request.session["dimensions"][file_code][col_add]["dt_abbr"], 'name': col_add, 'type': request.session["dimensions"][file_code][col_add]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
        special_graph_parameters_d2_m1['attribs'].append(attr_add)
        try:
            data = recommend_graph(request, special_graph_parameters_d2_m1, False, 1)
            #print("None")
        except Exception as e:
            print('Error details (Recommend Graph): '+ str(e))

        if len_cat >= 2 and 1 < len_cat-i-1 and all_stat["stat"][all_stat["col_cat"]["1"]]["nb_distinct"] <= settings.DINSTICT_CAT_FACET and all_stat["stat"][all_stat["col_cat"]["1"]]["nb_distinct"] > 1:
            special_graph_parameters_d3_m1 = copy.deepcopy(special_graph_parameters_d2_m1)
            special_graph_parameters_d3_m1["add_marg_score"] = special_graph_parameters_d3_m1["add_marg_score"] - 5
            col_add = all_stat["col_cat"]["1"]
            attr_add = {'fulltext': col_add, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col_add]["dt_id"],
            'realtype': request.session["dimensions"][file_code][col_add]["dt_abbr"], 'name': col_add, 'type': request.session["dimensions"][file_code][col_add]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
            special_graph_parameters_d3_m1['attribs'].append(attr_add)
            try:
                data = recommend_graph(request, special_graph_parameters_d3_m1, False, 1)
                #print("None")
            except Exception as e:
                print('Error details (Recommend Graph): '+ str(e))

            if len_cat >= 3 and 2 < len_cat-i-1 and all_stat["stat"][all_stat["col_cat"]["2"]]["nb_distinct"] <= settings.DINSTICT_CAT_FACET and all_stat["stat"][all_stat["col_cat"]["2"]]["nb_distinct"] > 1:
                special_graph_parameters_d4_m1 = copy.deepcopy(special_graph_parameters_d3_m1)
                special_graph_parameters_d4_m1["add_marg_score"] = special_graph_parameters_d4_m1["add_marg_score"] - 5
                col_add = all_stat["col_cat"]["2"]
                attr_add = {'fulltext': col_add, 'dimmeasopt': 'valexact', 'file': file_code, 'dt': request.session["dimensions"][file_code][col_add]["dt_id"],
                'realtype': request.session["dimensions"][file_code][col_add]["dt_abbr"], 'name': col_add, 'type': request.session["dimensions"][file_code][col_add]["dt_pd"], 'ty': 'dim', 'target': 'attribs'}
                special_graph_parameters_d4_m1['attribs'].append(attr_add)
                try:
                    data = recommend_graph(request, special_graph_parameters_d4_m1, False, 1)
                    #print("None")
                except Exception as e:
                    print('Error details (Recommend Graph): '+ str(e))
    return special_graph_parameters_d2_m1, special_graph_parameters_d3_m1, special_graph_parameters_d4_m1

#generate tasks visualization
def generate_tasks_viz(request, graph_parameters, require_div=True, require_analysis=True):
    file_code = graph_parameters['files'][0]
    visualization_action = graph_parameters["visualization_action"]
    data = {'success': False, 'message': _('Something went wrong')}
    try:
        current_file = request.session["list_selectedfiles"][file_code]
        if current_file:
            if bool(current_file["init_settings"]) and "tasks" in current_file["init_settings"]:
                ctn = 0
                for task in current_file["init_settings"]["tasks"]:
                    special_graph_parameters = {}
                    special_graph_parameters = copy.deepcopy(graph_parameters)
                    if "titles" in current_file["init_settings"]:
                        if len(current_file["init_settings"]["titles"]) > ctn:
                            special_graph_parameters["title"] = current_file["init_settings"]["titles"][ctn]
                    special_graph_parameters["visualization_action"] = "recommend_viz"
                    special_graph_parameters["add_marg_score"] = 0
                    special_graph_parameters['attribs'] = copy.deepcopy(task)
                    ctn = ctn + 1
                    try:
                        data = recommend_graph(request, special_graph_parameters, False, 999)
                    except Exception as e:
                        print('Error details (Recommend Graph): '+ str(e))
        request.session["end_recommend_graph"] = 1
        data = {'success': True, 'nb_recommend_graph': request.session["nb_recommend_graph"]}
    except Exception as e:
        request.session["end_recommend_graph"] = 1
        print('Error details: '+ str(e))
        data = {'success': False, 'message': _("Something went wrong")}
    return data

#Calculate features values based on visulization marks chosen by the user
def get_fig(request, df, type_viz, fig, px, ff, params, viz_grouping, is_num_x, is_num_y, col_name_shape):
    all_code = ""
    for key, viz in request.session["list_viztypes"].items():
        expr = viz["graph_function"]
        codeBlock = str(expr)
        all_code += codeBlock+ "\n"

    compiledCodeBlock = compile(all_code, '<string>', 'exec')
    loc = {'type_viz': type_viz, 'fig': fig, 'px': px, 'ff': ff, "params":params, "viz_grouping":viz_grouping,
    "is_num_x":is_num_x, "is_num_y":is_num_y, 'df': df, 'col_name_shape': col_name_shape}
    exec(compiledCodeBlock, {}, loc)
    fig = loc["fig"]
    return fig

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def list_files(request, codes, current_project):
    load_data(request, DataPortal, "list_dataportals", 0)
    load_data(request, PlatformPortal, "list_platformportals", 0)
    all_data = UploadFile.objects.select_related('portal').filter(code__in=codes).prefetch_related('related_files', 'related_projects')

    list_data = {}
    for data in all_data:
        has_tasks = 0
        source = ""
        source_link = None
        download_link = None
        last_modified = data.created_at.strftime("%d/%m/%Y %H:%M:%S")
        if bool(data.init_settings) and "tasks" in data.init_settings and len(data.init_settings["tasks"])>0:
            has_tasks = 1
        if data.file_name:
            source = _("File Upload")
        elif data.portal:
            source = data.portal.name
            source_link = data.portal.more_details["link"]
        elif "http" in data.file_link:
            source = _("External Link")

        list_data[data.code] = {"id":data.pk, "code":data.code, "file_link":data.file_link, "title":data.title, "file_ext":data.file_ext
        , "is_demo":data.is_demo, "has_tasks": has_tasks, "refresh_timeout":data.refresh_timeout, "init_settings":data.init_settings,
        "updated_at":data.updated_at, "more_details": data.more_details, "from_query": data.from_query, "created_at":data.created_at.strftime("%d/%m/%Y %H:%M:%S"), "source": source, "source_link": source_link,
        "last_modified": last_modified, "is_requested": data.is_requested, "full_title": data.more_details["title"], "description": data.more_details["description"], "contact": ("contact" in data.more_details and data.more_details["contact"]) or None,
        "country": data.country, "state": data.state, "nb_likes": data.nb_likes, "data_provided": data.data_provided}

        if current_project and bool(current_project["project_settings"]):
            if "files" in current_project["project_settings"]:
                if data.code in current_project["project_settings"]["files"]:
                    df_file_code = current_project["project_settings"]["files"][data.code]["df_file_code"]
                    if df_file_code in data.updated_at:
                        timestamp = float(data.updated_at["df_file_code"])
                        dt_object = datetime.datetime.fromtimestamp(timestamp)
                        last_modified = dt_object.strftime("%d/%m/%Y %H:%M:%S")
                        list_data[data.code]["last_modified"] = last_modified

                    if "data_info" in current_project["project_settings"]["files"][data.code]:
                        list_data[data.code]["data_info"] = current_project["project_settings"]["files"][data.code]["data_info"]
                        list_data[data.code]["full_title"] = current_project["project_settings"]["files"][data.code]["data_info"]["title"]
                        list_data[data.code]["description"] = cleanhtml(current_project["project_settings"]["files"][data.code]["data_info"]["description"])
                    if "quality" in current_project["project_settings"]["files"][data.code]:
                        list_data[data.code]["data_quality"] = current_project["project_settings"]["files"][data.code]["quality"]
                        list_data[data.code]["quality"] = current_project["project_settings"]["files"][data.code]["quality"]["average"]

        list_data[data.code]["related_projects"]={}
        if data.related_projects:
            list_data[data.code]["related_projects"]={}
            for proj in data.related_projects.all():
                list_data[data.code]["related_projects"][proj.code] = {"id":data.pk, "project_settings":proj.project_settings,
                "project_history":proj.project_history, "user":(proj.user and proj.user.username), "title":proj.title, "notes":proj.notes, "shared":proj.shared, "code":proj.code, "dash_code":proj.dash_code,
                "updated_at": proj.updated_at.strftime('%d/%m/%Y'), "project_type": proj.project_type, "contact": proj.contact, "image": (proj.image and proj.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": proj.static_image,
                "theme": str(proj.theme.pk), "link": proj.link, "country": proj.country, "state": proj.state, "status": str(proj.status.pk), "list_datasets": proj.list_datasets}

        list_data[data.code]["related_files"]={}
        if data.related_files:
            for redata in data.related_files.all():
                has_tasks = 0
                if bool(redata.init_settings) and "tasks" in redata.init_settings and len(redata.init_settings["tasks"])>0:
                    has_tasks = 1
                list_data[data.code]["related_files"][redata.code] = {"id":redata.pk, "code":redata.code, "file_link":redata.file_link, "title":redata.title, "file_ext":redata.file_ext
                , "is_demo":redata.is_demo, "has_tasks": has_tasks, "refresh_timeout":redata.refresh_timeout, "init_settings":redata.init_settings,
                "updated_at":redata.updated_at, "more_details": redata.more_details, "from_query": redata.from_query, "created_at":redata.created_at.strftime("%d/%m/%Y"), "is_requested": redata.is_requested}

    return list_data

#delete html tags form string
def cleanhtml(raw_html):
    if not raw_html or raw_html == "":
        return raw_html
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

#Generate form to edit data info
def info_data_form(request, code):
    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    form = """
        <input type="hidden" name="edit_data_code" value="%s" id="edit_data_code">
    """ % code

    title = ""
    if current_project and bool(current_project["project_settings"]):
        if "files" in current_project["project_settings"]:
            if code in current_project["project_settings"]["files"]:
                current_file = current_project["project_settings"]["files"][code]
                # Get general info
                if "data_info" in current_file:
                    title = current_file["data_info"]["title"]
                    form = form + "<div class='col l12 m12 s12'><p>"+_("General Information")+"</p><hr/></div>"
                    form = form + """
                    <div class="col l6 m6 s12"><label>%s</label>
              <input class="browser-default special-input1 validate invalid" id="data_title" name="data_title" type="text" placeholder="%s" value="%s" required>
            </div> """ % (_('Title*'), _('Provide title of the dataset'), current_file["data_info"]["title"])

                    refresh_timeout = ""
                    if code in request.session["list_selectedfiles"]:
                        refresh_timeout = request.session["list_selectedfiles"][code]["refresh_timeout"]
                    form = form + """
                    <div class="col l6 m6 s12"><label for="data_refresh">%s</label>
                    <input class="browser-default special-input1 validate invalid" type="number" name="data_refresh" id="data_refresh" placeholder="%s" value="%s">
                    <small class="helptext">Let empty if you don't need to refresh data</small></div>
                    """ % (_('Refresh Timeout (in seconds)'), _('Provide refresh timeout in seconds'), refresh_timeout or None)

                    form = form + """
                            <div class="col l12 m12 s12"><label>%s</label>
                      <textarea style="min-height: 100px;" class="browser-default validate invalid" id="data_description" name="data_description" placeholder="%s">%s</textarea>
                    </div> """ % (_('Description'), _('Provide description of the dataset'), (current_file["data_info"]["description"] and cleanhtml(current_file["data_info"]["description"])) or "")

                #get column info
                if "columns" in current_file:
                    load_data(request, DataType, "list_datatypes", 0)
                    columns = current_file["columns"]
                    form = form + "<div class='col l12 m12 s12'><p>"+_("Columns Information")+"</p><hr/></div>"
                    form = form + """<div class='col l12 m12 s12'>
                        <table style="overflow:auto;">
                        <thead>
                          <tr>
                              <th>%s</th>
                              <th>%s</th>
                              <th>%s</th>
                              <th>%s</th>
                          </tr>
                        </thead>
                        <tbody>
                    """ % (_('Column'), _('Label'), _('Description'), _('Datatype*'))
                    for key, col in columns.items():
                        form = form + """
                            <tr>
                                <td>%s</td>
                                <td>
                                    <input class="browser-default special-input1 validate invalid colabel" id="%s" name="%s" type="text" value="%s">
                                </td>
                                <td>
                                    <textarea class="browser-default validate invalid coldescript" id="%s" name="%s">%s</textarea>
                                </td>
                        """ % (key, "lb"+col["id"],"lb"+col["id"], col["label"] or "", "de"+col["id"], "de"+col["id"], col["description"] or "")
                        form = form + """<td>
                            <select id="%s" name="%s" class="browser-default coldtype">
                        """ % ("ty"+col["id"],"ty"+col["id"])

                        for k, dtype in request.session["list_datatypes"].items():
                            selected = ""
                            if str(col["datatype"]) == str(dtype["id"]):
                                selected = "selected"
                            form = form + """
                                <option %s value="%s">%s</option>
                            """ % (selected, dtype["id"], dtype["name"])

                        form = form + """
                            </select></td></tr>
                        """
                    form = form + """
                        </tbody></table></div>
                    """

            data = {'success': True, 'form': form, 'title': title}
    return data

def save_data_info(request, code):
    data = {'success': False, 'message': _('Something went wrong')}
    current_project = request.session["current_project"]
    update_cols = 0
    update_file = 0
    update_title = 0
    update_lade = 0
    project_history = []
    project_settings = {}
    nb_dfs = 0
    json_columns = {}
    current_state = 0
    new_df_file_code = ""
    file_code = code
    convert_dict = {}
    quality = {"complete_data":0, "column_labels":0,"column_descriptions":0,"data_info":0, "average": 0}

    if code and code in request.session["list_selectedfiles"]:
        refresh_timeout = request.session["list_selectedfiles"][code]["refresh_timeout"] or None
        data_refresh = request.POST.get('data_refresh') or None
        if data_refresh != refresh_timeout:
            update_file = 1

        if current_project and bool(current_project["project_settings"]):
            if "files" in current_project["project_settings"]:
                if code in current_project["project_settings"]["files"]:
                    current_file = current_project["project_settings"]["files"][code]
                    my_cf = request.session["list_selectedfiles"][file_code]
                    convert_dict = copy.deepcopy(request.session["convert_dict"][file_code])
                    project_history = copy.deepcopy(current_project["project_history"])
                    project_settings = copy.deepcopy(current_project["project_settings"])


                    # Get general info
                    title = current_file["data_info"]["title"] or None
                    data_title = request.POST.get('data_title') or my_cf["title"]
                    if data_title != title:
                        update_title = 1

                    if data_title and data_title != "":
                        quality["data_info"] = quality["data_info"] + 1

                    description = current_file["data_info"]["description"] or None
                    data_description = request.POST.get('data_description') or None
                    if data_description != description:
                        update_title = 1

                    if data_description and data_description != "":
                        quality["data_info"] = quality["data_info"] + 1

                    if my_cf["more_details"]["modified"] and my_cf["more_details"]["modified"] != "":
                        quality["data_info"] = quality["data_info"] + 1

                    if "columns" in current_file:
                        nb_dfs = project_settings["nb_dfs"]
                        new_df_file_code = request.session["project_code"]+"d"+str(nb_dfs+1)

                        load_data(request, DataType, "list_datatypes", 0)
                        columns = current_file["columns"]
                        for key, col in columns.items():
                            column_data = key
                            lb = "lb"+col["id"]
                            de = "de"+col["id"]
                            ty = "ty"+col["id"]
                            type_data = request.POST[ty] or None
                            lb_data = request.POST[lb] or key
                            de_data = request.POST[de] or None
                            if lb_data != col["label"]:
                                update_lade = 1
                                project_settings["files"][file_code]["columns"][column_data]["label"] = lb_data
                            if de_data != col["description"]:
                                update_lade = 1
                                project_settings["files"][file_code]["columns"][column_data]["description"] = de_data

                            if de_data and de_data != "":
                                quality["column_descriptions"] = quality["column_descriptions"] + 1
                            if lb_data and lb_data != "" and lb_data != key:
                                quality["column_labels"] = quality["column_labels"] + 1

                            #print(str(col["datatype"])+"========"+str(type_data))
                            if str(col["datatype"]) != str(type_data):
                                update_cols = 1
                                old_datatype_name = request.session["list_selectedfiles"][file_code]["init_settings"]["init_columns"][column_data]
                                new_datatype = DataType.objects.get(pk=int(type_data))
                                request.session["convert_dict"][file_code][column_data] = request.session["list_datatypes"][str(type_data)]["pandas_name"]
                                project_settings["files"][file_code]["columns"][column_data]["datatype"] = int(type_data)

                                #Create new datatype rule
                                new_datatype_rule = DataTypeRule()
                                new_datatype_rule.user_type = request.session["current_user_type"]
                                new_datatype_rule.datatype = new_datatype
                                rule = settings.NEW_DATATYPE_RULE
                                rule = rule.replace("datatype_name", old_datatype_name)
                                rule = rule.replace("column_name", column_data)
                                new_datatype_rule.rule = rule
                                num_results = DataTypeRule.objects.filter(rule = rule).count()
                                new_datatype_rule.address_ip = visitor_ip_address(request)
                                if request.user and request.user.id:
                                    new_datatype_rule.user_id = request.user.id

                                if num_results == 0:
                                    new_datatype_rule.save()

        if update_file == 1:
            request.session["list_selectedfiles"][code]["refresh_timeout"] = data_refresh
            my_file = UploadFile.objects.get(code__exact=code)
            my_file.refresh_timeout = data_refresh
            my_file.save(update_fields=['refresh_timeout'])

        if update_title == 1:
            request.session["current_project"]["project_settings"]["files"][code]["data_info"]["title"] = data_title
            request.session["current_project"]["project_settings"]["files"][code]["data_info"]["description"] = data_description
            project_settings["files"][code]["data_info"]["title"] = data_title
            project_settings["files"][code]["data_info"]["description"] = data_description

        if update_cols == 1:
            if bool(project_settings):
                previous_settings = copy.deepcopy(project_settings)
                project_history.append(previous_settings)
                current_state = len(project_history)
                result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
                request.session["list_selectedfiles"][file_code]["file_link"], refresh_timeout,
                current_project["project_settings"]["files"][file_code]["df_file_code"], 0, convert_dict)
                old_df = result_df["df"]
                if old_df is None:
                    return data
                df = update_column_from_df(request, old_df, new_df_file_code, request.session["convert_dict"][file_code])
                if df is None:
                    return data

            project_settings["files"][file_code]["df_file_code"] = new_df_file_code
            project_settings["nb_dfs"] = nb_dfs + 1
            project_settings["state"] = current_state
            project_settings["insight"] = _("Change datatype of some columns")
            project_settings["date"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            all_stat = get_stat_df(request, df, project_settings["files"][file_code]["columns"], 0)
            inc = 1
            nb_tot_values = 0
            columns = current_project["project_settings"]["files"][code]["columns"]
            for col, valcol in columns.items():
                if "stat" in all_stat and col in all_stat["stat"]:
                    nb_tot_values = nb_tot_values + all_stat["stat"][col]["nb_total"]
                    quality["complete_data"] = quality["complete_data"] + (int(all_stat["stat"][col]["nb_total"]) - int(all_stat["stat"][col]["mis_val"]))
                inc += 1
            quality["column_descriptions"] = round(float(quality["column_descriptions"])*100.0/float(inc-1), 2)
            quality["column_labels"] = round(float(quality["column_labels"])*100.0/float(inc-1), 2)
            quality["complete_data"] = round(float(quality["complete_data"])*100.0/float(nb_tot_values), 2)
        else:
            quality["column_descriptions"] = current_project["project_settings"]["files"][file_code]["quality"]["column_descriptions"]
            quality["column_labels"] = current_project["project_settings"]["files"][file_code]["quality"]["column_labels"]
            quality["complete_data"] = current_project["project_settings"]["files"][file_code]["quality"]["complete_data"]

        if update_cols == 1 or update_lade == 1 or update_title == 1:
            quality["data_info"] = round(float(quality["data_info"])*100.0/3.0, 2)
            quality["average"] = round((settings.WEIGHT_DATA_INFO * float(quality["data_info"]) + settings.WEIGHT_COLUMN_DESCRIPTIONS * float(quality["column_descriptions"]) + settings.WEIGHT_COLUMN_LABELS * float(quality["column_labels"]) + settings.WEIGHT_COMPLETE_DATA * float(quality["complete_data"]))/float(settings.WEIGHT_COMPLETE_DATA + settings.WEIGHT_COLUMN_LABELS + settings.WEIGHT_COLUMN_DESCRIPTIONS + settings.WEIGHT_DATA_INFO), 2)
            project_settings["files"][file_code]["quality"] = quality
            project = Project.objects.get(code__exact=request.session['project_code'])
            project.project_settings = project_settings
            project.project_history = project_history
            project.save(update_fields=['project_settings','project_history'])
            #get current project
            if update_cols == 1:
                load_full_project(request, Project, "current_project", 1)
            else:
                load_data(request, Project, "current_project", 1)
            #get select files
            load_data(request, UploadFile, "list_selectedfiles", 1)

        data = {'success': True, 'message': _('Update successful'), 'title': request.session["current_project"]["project_settings"]["files"][code]["data_info"]["title"]
        , 'quality': request.session["current_project"]["project_settings"]["files"][code]["quality"]["average"], 'code': code}

    return data

def init_columns_datatable(request, project, file, query):
    query +=" LIMIT 2"
    data = {}
    file_code = file['code']
    project_settings = project["project_settings"]
    columns = project_settings["files"][file_code]["columns"]
    convert_dict = {}
    mycolumns = []
    load_data(request, DataType, "list_datatypes", 0)
    for keycol, col in columns.items():
        current_datatype = request.session["list_datatypes"][str(col["datatype"])]
        convert_dict[keycol] = current_datatype["pandas_name"]

    print(convert_dict)

    result_df = save_read_df(request, file_code, file["file_ext"], file["file_link"], file["refresh_timeout"],
    project_settings["files"][file_code]["df_file_code"], 0, convert_dict, query)

    df = result_df["df"]

    if df is None:
    	return data
    else:
        #nb_rows = int(df.shape[0])

        for col, val in convert_dict.items():
            try:
                if "date" in val:
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
            except:
                print("error")

        df_split = df.to_json(orient="split")
        data["columns"] = [{"title": columns[str(col)]["label"] or str(col)} for col in json.loads(df_split)["columns"]]
        data["dropdown_columns"] = [{"col": str(col), "title": columns[str(col)]["label"] or str(col)} for col in json.loads(df_split)["columns"]]
        #data["recordsTotal"] = nb_rows
    return data

def create_datatable(request, project_code, file_code, query):
    data = {'fail': True, 'message': _('Something went wrong')}
    project = None
    file_ext = None
    file_link = None
    refresh_timeout = None
    project_settings = None

    try:
        if "list_explore_projects" in request.session and project_code in request.session["list_explore_projects"]:
            project = request.session["list_explore_projects"][project_code]
            project_settings = project["project_settings"]
        else:
            project = Project.objects.get(code__exact=project_code)
            project_settings = project.project_settings
    except:
        project = None

    if project is None:
        return data

    try:
        if "list_explore_files" in request.session and file_code in request.session["list_explore_files"]:
            file = request.session["list_explore_files"][file_code]
            file_ext = file["file_ext"]
            file_link = file["file_link"]
            refresh_timeout = file["refresh_timeout"]
        else:
            file = UploadFile.objects.get(code__exact=file_code)
            file_ext = file.file_ext
            file_link = file.file_link
            refresh_timeout = file.refresh_timeout
    except:
    	file = None

    if file is None:
        return data

    #print(project_settings["files"].keys())
    columns = project_settings["files"][file_code]["columns"]
    convert_dict = {}
    load_data(request, DataType, "list_datatypes", 0)
    for keycol, col in columns.items():
        current_datatype = request.session["list_datatypes"][str(col["datatype"])]
        convert_dict[keycol] = current_datatype["pandas_name"]

    requestData = request.GET

    result_df = save_read_df(request, file_code, file_ext, file_link, refresh_timeout,
    project_settings["files"][file_code]["df_file_code"], 0, convert_dict, query)

    df = result_df["df"]


    if df is None:
    	return data
    else:
        data = {}
        nb_rows = int(df.shape[0])
        #
        #print(int(requestData['length']))
        if int(requestData['length']) != -1:
            df_sm = df.iloc[int(requestData['start']):(int(requestData['length'])+int(requestData['start']))]
        else:
            df_sm = df

        for col, val in convert_dict.items():
            try:
                if "date" in val:
                    df_sm[col] = df_sm[col].dt.strftime('%Y-%m-%d')
            except:
                print("error")

        df_split = df_sm.to_json(orient="split",date_format='iso')

        data["data"] = json.loads(df_split)["data"]

        #data["draw"] = request.POST.get('draw')
        data["recordsTotal"] = nb_rows
        data["recordsFiltered"] = nb_rows

    return data

def datatable_script(id, final_url, init_columns):
    script = """
    <script type="text/javascript" language="javascript">
                document.addEventListener("DOMContentLoaded", function(event) {
                    $('#%s').DataTable({
                        "pagingType": "full_numbers",
                        "ordering": false,
                        "searching": false,
                        "columns":%s,
                        lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                        //"bLengthChange": false,
                        pageLength: 10,
                        "processing": true,
                        "serverSide": true,
                        "ajax": {
                            url: "%s",
                            type: "GET"
                        },
                        /*fixedHeader: {
                            header: true,
                            headerOffset: 50
                        },*/
                        columnDefs: [
                            {
                                targets: ['_all'],
                                className: 'mdc-data-table__cell cell-truncate'
                            }
                        ],
                        createdRow: function(row){
                           $(row).find(".cell-truncate").each(function(){
                              $(this).attr("title", this.innerText);
                           });
                        },
                        "buttons": [
            				'colvis',
                            'csvHtml5',
            			],
                        "dom": '<"mdc-layout-grid"<"mdc-layout-grid__inner"<"mdc-cell mdc-layout-grid__cell--span-6"B><"mdc-cell mdc-layout-grid__cell--span-6"l>>><"mdc-layout-grid dt-table"<"mdc-layout-grid__inner"<"mdc-cell mdc-layout-grid__cell--span-12"t>>><"mdc-layout-grid"<"mdc-layout-grid__inner"<"mdc-cell mdc-layout-grid__cell--span-6"i><"mdc-cell mdc-layout-grid__cell--span-6"p>>>',
                    });
                });
                </script>
                """ % (id, json.dumps(init_columns['columns']), final_url)
    script = "<div class='table-responsive'><table id='"+id+"' class='mdl-data-table' style='width:100%'></table></div>" + script
    return script

def generate_explore_column(request, project_code, file_code, query, current_col):
    data = {'success': False, 'message': _('Something went wrong')}
    project = None
    file_ext = None
    file_link = None
    refresh_timeout = None
    project_settings = None
    datatype_name = ""
    description = ""
    label = ""
    missed_values = ""
    corr = ""
    graph_content = ""
    div_content = ""

    try:
        if "list_explore_projects" in request.session and project_code in request.session["list_explore_projects"]:
            project = request.session["list_explore_projects"][project_code]
            project_settings = project["project_settings"]
        else:
            project = Project.objects.get(code__exact=project_code)
            project_settings = project.project_settings
    except:
        project = None

    if project is None:
        return data

    try:
        if "list_explore_files" in request.session and file_code in request.session["list_explore_files"]:
            file = request.session["list_explore_files"][file_code]
            file_ext = file["file_ext"]
            file_link = file["file_link"]
            refresh_timeout = file["refresh_timeout"]
        else:
            file = UploadFile.objects.get(code__exact=file_code)
            file_ext = file.file_ext
            file_link = file.file_link
            refresh_timeout = file.refresh_timeout

    except:
    	file = None

    if file is None:
        return data

    columns = project_settings["files"][file_code]["columns"]
    convert_dict = {}
    load_data(request, DataType, "list_datatypes", 0)

    col = columns[current_col]
    current_datatype = request.session["list_datatypes"][str(columns[current_col]["datatype"])]
    datatype_name = current_datatype["name"]
    description = columns[current_col]["description"]
    label = columns[current_col]["label"]
    nb_total = project_settings["files"][file_code]["all_stat"]["stat"][current_col]["nb_total"]
    missed_values = 0.0

    if nb_total > 0:
        missed_values = (float(project_settings["files"][file_code]["all_stat"]["stat"][current_col]["mis_val"]) * 100.0)/float(nb_total)
        missed_values = round(missed_values, 2)
    if "corr" in project_settings["files"][file_code]["all_stat"]["stat"][current_col]:
        mycol = project_settings["files"][file_code]["all_stat"]["stat"][current_col]["corr"]
        if int(mycol["nb_corr"]) == 0:
            corr = "There is no correlation/relation between this column and other numeric columns"
        else:
            corr = "There is correlation/relation between this column and following columns: "
            for key,value in mycol.items():
                if key not in ["nb_corr", "tot_corr"]:
                    if value > settings.GOOD_CORR:
                        corr +=  columns[key]["label"]+", "
        corr = corr[:-2]

    if int(columns[current_col]["datatype"]) in settings.EXPLORE_COLUMN_DATATYPES:
        graph_columns = []
        current_datatype = request.session["list_datatypes"][str(columns[current_col]["datatype"])]
        filt = {"name": current_col, "realtype": current_datatype["abbreviation"], "type": current_datatype["pandas_name"]}
        if int(columns[current_col]["datatype"]) in settings.GOOD_CAT_DATATYPES: #bool or nominal
            filt["dimmeasopt"] = ""
            filt["bins"] = None
        else:
            filt["dimmeasopt"] = "bins"
            filt["bins"] = settings.DEFAULT_BINS
        graph_columns.append(filt)
        filt = {"name": "count", "realtype": "auto", "type": "auto"}
        filt["dimmeasopt"] = ""
        filt["bins"] = None
        graph_columns.append(filt)
        df_file_code = project_settings["files"][file_code]["df_file_code"]
        df_pkl = "df_" + df_file_code
        query = generate_query_explore_col(request, df_pkl, graph_columns)
        #print(query)

        result_df = save_read_df(request, file_code, file_ext, file_link, refresh_timeout,
        project_settings["files"][file_code]["df_file_code"], 0, convert_dict, query)

        df = result_df["df"]

        if df is None:
        	return data
        params = {}
        params["df"] = df
        params["id"] = "gp_"+current_col
        if int(columns[current_col]["datatype"]) in settings.GOOD_CAT_DATATYPES:
            params["x"] = current_col
            params["y"] = "count"
            graph_content = wordcloud_highcharts(request, params)
        else:
            init_columns  = df.columns.tolist()
            params["x"] = init_columns[1]
            params["y"] = init_columns[2]
            params["labely"] = _("Occurrences")
            graph_content = "<br/>"+histogram_highcharts(request, params)
            #print(init_columns)

        #data["data"] = json.loads(df_split)["data"]

    data = {'success': True}

    if label != "":
        div_content += """<br/><b class="labelcol">%s</b>""" % label

    if description != "":
        div_content += """<br/><b>%s </b>%s""" % (_("Description: "), description)

    if datatype_name != "":
        div_content += """<br/><b>%s </b>%s""" % (_("Datatype: "), datatype_name)

    div_content += """<br/><b>%s </b>%s""" % (_("Missed Values: "), str(missed_values)+"%")

    if corr != "":
        div_content += """<br/><b>%s </b>%s""" % (_("Correlation: "), corr)
    if graph_content != "":
        div_content += """<br/>%s""" % (graph_content)
    else:
        div_content += """<br/>%s""" % (_("No data distribution because this column is of type ")+datatype_name)

    data["div_content"] = div_content

    return data

#Generate data quality graph using gauge
def gauge_highcharts(request, params):
    script = """
    <script type="text/javascript" language="javascript">
                document.addEventListener("DOMContentLoaded", function(event) {
                        var gaugeOptions = {
                        chart: {
                            type: 'solidgauge',
                            height: '100%',
                        },
                        title: null,
                        exporting: {
                            enabled: false
                        },
                        pane: {
                            startAngle: 0,
                            endAngle: 360,
                            background: {
                                backgroundColor:
                                    Highcharts.defaultOptions.legend.backgroundColor || '#EEE',
                                innerRadius: '60%',
                                outerRadius: '100%',
                                shape: 'arc'
                            }
                        },
                        // the value axis
                        yAxis: {
                            stops: [
                                [0.1, '#DF5353'], // red
                                [0.5, '#DDDF0D'], // yellow
                                [0.9, '#55BF3B'] // green
                            ],
                            lineWidth: 0,
                            tickWidth: 0,
                            minorTickInterval: null,
                            tickAmount: 2,
                            title: {
                                y: 50
                            }
                        },
                        plotOptions: {
                            solidgauge: {
                                dataLabels: {
                                    borderWidth: 0,
                                    useHTML: true
                                }
                            }
                        }
                    };

                    //Gauge
                    var __id__ = Highcharts.chart('__id__', Highcharts.merge(gaugeOptions, {
                        yAxis: {
                            min: __min__,
                            max: __max__,
                            title: {
                                text: '__title__'
                            }
                        },
                        credits: {
                            enabled: true
                        },
                        series: [{
                            name: '__title__',
                            data: [__value__],
                            dataLabels: {
                                format:
                                    '<div style="text-align:center">' +
                                    '<span style="font-size:1.1rem">{y}</span>' +
                                    '<span style="font-size:1rem;opacity:0.4">__unit__</span>' +
                                    '</div>'
                            },
                            tooltip: {
                                valueSuffix: '__unit__'
                            }
                        }]

                    }));
                });
                </script>
                """
    for k, v in params.items():
        script = script.replace("__"+k+"__", str(v))

    #% (params["variable"], params["id"], params["min"], params["max"], params["title"], params["title"], params["value"], params["unit"], params["unit"])
    script = "<figure class='highcharts-figure'><div id='"+params["id"]+"' class='chart-container' style='width:100%'></div></figure>" + script
    return script

#generate query from explore data column
def generate_query_explore_col(request, df_pkl, columns):
    #initialize variables to be returned
    data_select = []
    data_where = []
    data_groupby = []
    # to manage bin columns
    before_select = ""
    after_from = ""
    list_bins = []
    order_by = []
    order_by_bins = []
    order_by_proposed = []

    select_d = ""
    where_d = ""
    groupby_d = ""

    need_group_by = 1

    for filt in columns:
        col = filt["name"]
        col_name = col

        if (filt["dimmeasopt"] and filt["dimmeasopt"] == "bins" and int(filt["bins"])>0):
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
        elif (filt["realtype"] == "auto"):
            where_d = "count(*)"
            select_d = "COALESCE(" + where_d + ", 0)" + " as " + col_name
            having_d = 1
        else:
            where_d = col
            col_name = col
            select_d = where_d
            groupby_d = col
            order_by_proposed.append(col_name+" asc")

        if groupby_d and groupby_d not in data_groupby:
            data_groupby.append(groupby_d)

        if select_d not in data_select:
            data_select.append(select_d)

    #Create final query
    final_query = ""
    if len(data_select) == 0:
        return final_query
    else:
        if before_select != "":
            final_query += " "+ before_select
        final_query +=" SELECT " + ', '.join(data_select)
        final_query += " FROM "+ df_pkl+after_from
    final_query +=" WHERE 1 = 1 "
    if len(data_groupby) > 0 and need_group_by == 1:
        final_query +=" GROUP BY " + ', '.join(data_groupby)
    if len(order_by_bins) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by_bins)
    elif len(order_by_proposed) > 0:
        final_query +=" ORDER BY " + ', '.join(order_by_proposed)

    return final_query

def wordcloud_highcharts(request, params):
    df = params["df"]
    df.rename(columns = {params["x"]: 'name', params["y"]: 'weight'}, inplace = True)
    df = df.dropna(subset=['name'])

    if int(df.shape[0]) > settings.MAX_WORDCLOUD_ITEMS:
        df.sort_values(by=['weight'], ascending=False, inplace=True)
        #df.reset_index(inplace = True)
        df = df.head(settings.MAX_WORDCLOUD_ITEMS)
    df_split = df.to_json(orient="records")

    params["graphtitle"] = "null"
    params["pre"] = ""
    params["suf"] = ""
    if "title" in params and params["title"]:
        params["graphtitle"] = """{text: '__title__'}"""
        params["graphtitle"] = params["graphtitle"].replace("__title__", params["title"])
    if "addready" in params:
        params["pre"] = 'document.addEventListener("DOMContentLoaded", function(event) {'
        params["suf"] = '});'


    params["data"] = json.loads(df_split)

    script = """
    <script type="text/javascript" language="javascript">
                    __pre__
                    var __id__ = Highcharts.chart('__id__', {
                        accessibility: {
                            screenReaderSection: {
                                beforeChartFormat: '<h5>{chartTitle}</h5>' +
                                    '<div>{chartSubtitle}</div>' +
                                    '<div>{chartLongdesc}</div>' +
                                    '<div>{viewTableButton}</div>'
                            }
                        },
                        series: [{
                            type: 'wordcloud',
                            data: __data__,
                            name: 'Occurrences'
                        }],
                        title: __graphtitle__
                    });
                __suf__
                </script>
                """
    for k, v in params.items():
        script = script.replace("__"+k+"__", str(v))

    #% (params["variable"], params["id"], params["min"], params["max"], params["title"], params["title"], params["value"], params["unit"], params["unit"])
    script = "<figure class='highcharts-figure'><div id='"+params["id"]+"' class='chart-container' style='width:100%; height: 260px;'></div></figure>" + script
    return script


def histogram_highcharts(request, params):
    df = params["df"]

    params["graphtitle"] = "null"
    params["pre"] = ""
    params["suf"] = ""
    if "title" in params and params["title"]:
        params["graphtitle"] = """{text: '__title__'}"""
        params["graphtitle"] = params["graphtitle"].replace("__title__", params["title"])
    if "addready" in params:
        params["pre"] = 'document.addEventListener("DOMContentLoaded", function(event) {'
        params["suf"] = '});'

    params["categories"] = df[params['x']].tolist()
    params["data"] = df[params['y']].tolist()

    script = """
    <script type="text/javascript" language="javascript">
                    __pre__
                    var __id__ = Highcharts.chart('__id__', {
                          chart: {
                            type: 'column'
                          },
                          title: __graphtitle__,
                          xAxis: {
                            categories: __categories__,
                            crosshair: true
                          },
                          yAxis: {
                            min: 0,
                            title: null
                          },
                          tooltip: {
                            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                              '<td style="padding:0"><b>{point.y:.0f}</b></td></tr>',
                            footerFormat: '</table>',
                            shared: true,
                            useHTML: true
                          },
                          plotOptions: {
                            column: {
                              pointPadding: 0,
                              borderWidth: 0,
                              groupPadding: 0,
                              shadow: false
                            }
                          },
                          series: [{
                            name: '__labely__',
                            data: __data__
                          }]
                        });
                __suf__
                </script>
                """
    for k, v in params.items():
        script = script.replace("__"+k+"__", str(v))

    #% (params["variable"], params["id"], params["min"], params["max"], params["title"], params["title"], params["value"], params["unit"], params["unit"])
    script = "<figure class='highcharts-figure'><div id='"+params["id"]+"' class='chart-container' style='width:100%; height: 200px;'></div></figure>" + script
    return script


def timeago(mydate):
    now = timezone.now()
    diff= now - mydate
    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        seconds= diff.seconds
        if seconds == 1:
            return str(seconds) +  _(" second ago")
        else:
            return str(seconds) + _(" seconds ago")

    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        minutes= math.floor(diff.seconds/60)
        if minutes == 1:
            return str(minutes) + _(" minute ago")
        else:
            return str(minutes) + _(" minutes ago")

    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        hours= math.floor(diff.seconds/3600)
        if hours == 1:
            return str(hours) + _(" hour ago")
        else:
            return str(hours) + _(" hours ago")

    # 1 day to 30 days
    if diff.days >= 1 and diff.days < 30:
        days= diff.days
        if days == 1:
            return str(days) + _(" day ago")
        else:
            return str(days) + _(" days ago")

    if diff.days >= 30 and diff.days < 365:
        months= math.floor(diff.days/30)
        if months == 1:
            return str(months) + _(" month ago")
        else:
            return str(months) + _(" months ago")

    if diff.days >= 365:
        years= math.floor(diff.days/365)
        if years == 1:
            return str(years) + _(" year ago")
        else:
            return str(years) + _(" years ago")

#Get list of used countries
def get_countries(request):
    cursor = connection.cursor()
    countries = []
    try:
        sql = """select distinct country from (
        	(select distinct country from visualizations_uploadfile where country is not NULL)
        	UNION
        	(select distinct country from visualizations_project where country is not NULL)
        ) as subq"""
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            countries.append(row[0])
        countries = sorted(countries)
        request.session["used_countries"] = countries
    except Exception as e:
        print('Error details: '+ str(e))
    return countries

#Get list of used countries
def get_transcountries(request):
    cursor = connection.cursor()
    countries = []
    try:
        sql = """select distinct country from visualizations_transproject where country is not NULL"""
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            countries.append(row[0])
        countries = sorted(countries)
        request.session["used_transcountries"] = countries
    except Exception as e:
        print('Error details: '+ str(e))
    return countries

#Get list of states based on country
def get_states_by_country(request, country=None):
    cursor = connection.cursor()
    states = []
    data = {'states': states, "success": False}
    try:
        if country is None or country == "" or not country:
            sql = """select distinct state from (
            	(select distinct state from visualizations_uploadfile where state is not NULL)
            	UNION
            	(select distinct state from visualizations_project where state is not NULL)
            ) as subq"""
        else:
            sql = """select distinct state from (
            	(select distinct state from visualizations_uploadfile where state is not NULL and country='"""+country+"""')
            	UNION
            	(select distinct state from visualizations_project where state is not NULL and country='"""+country+"""')
            ) as subq"""
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            states.append(row[0])
        data = {'states': states, "success": True}
    except Exception as e:
        print('Error details: '+ str(e))
    return data


#Get list of states based on transcountry
def get_states_by_transcountry(request, country=None):
    cursor = connection.cursor()
    states = []
    data = {'states': states, "success": False}
    try:
        if country is None or country == "" or not country:
            sql = """select distinct state from visualizations_transproject where state is not NULL"""
        else:
            sql = """select distinct state from visualizations_transproject where state is not NULL and country='"""+country+"""'"""
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            states.append(row[0])
        data = {'states': states, "success": True}
    except Exception as e:
        print('Error details: '+ str(e))
    return data


def check_like(request, like_type, obj_id, action_type="like", return_obj=False):
    result = False
    user_id = 0
    if request.user and request.user.id:
        user_id = request.user.id
    all_data = None
    if like_type == "project":
        all_data = Like.objects.filter((Q(project__id=obj_id) & Q(action_type__exact=action_type)) & (Q(user__id=user_id) | Q(address_ip__exact=visitor_ip_address(request))))
    if like_type == "file":
        all_data = Like.objects.filter((Q(file__id=obj_id) & Q(action_type__exact=action_type)) & (Q(user__id=user_id) | Q(address_ip__exact=visitor_ip_address(request))))
    if all_data and len(all_data) > 0:
        result = True
        if return_obj == True:
            result = all_data[0]

    return result

#List down all the projects based on keyword
def autocomplete_project(request):
    data = {'datas': [], "success": False}
    list_data = []
    if request.method == 'POST':
        search = request.POST.get('search', "")
        reqfilter = (Q(shared__exact=True) & Q(title__icontains=search))
        datas = Project.objects.filter(reqfilter).order_by('-updated_at')
        if len(datas) > 0:
            for dt in datas:
                list_data.append(dt.title)
            data = {'datas': list_data, "success": True}
    return data

#List down all the files based on keyword
def autocomplete_dataset(request):
    data = {'datas': [], "success": False}
    list_data = []
    if request.method == 'POST':
        search = request.POST.get('search', "")
        reqfilter = (Q(active__exact=True) & Q(more_details__title__icontains=search))
        datas = UploadFile.objects.filter(reqfilter).order_by('-created_at')
        if len(datas) > 0:
            for dt in datas:
                list_data.append(dt.more_details["title"])
            data = {'datas': list_data, "success": True}
    return data

def get_project_statuses(request, reload=0):
    #for update status
    statuses_fus = []
    #for suggested project
    statuses_fsp = []
    #for OGD reuse
    statuses_fep = []
    list_statuses = []

    if "statuses" not in request.session or reload == 1:
        statuses = ProjectStatus.objects.all().order_by('sequence')
        for dt in statuses:
            list_statuses.append({"id": dt.pk, "name": dt.name, "abbreviation": dt.abbreviation, "for_update_status": dt.for_update_status
            , "for_suggested_project": dt.for_suggested_project, "for_existing_project": dt.for_existing_project, "icon": dt.icon, "color": dt.color})
            if dt.for_update_status:
                statuses_fus.append(dt.pk)
            if dt.for_suggested_project:
                statuses_fsp.append(dt.pk)
            if dt.for_existing_project:
                statuses_fep.append(dt.pk)
        request.session["statuses"] = list_statuses
        request.session["statuses_fus"] = statuses_fus
        request.session["statuses_fsp"] = statuses_fsp
        request.session["statuses_fep"] = statuses_fep

#Check if the website is running on mobile or not
def mobile(request):
    """Return True if the request comes from a mobile device."""
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch|ipad|android)",re.IGNORECASE)
    #print(request.META['HTTP_USER_AGENT'])
    #print(request.META.get('HTTP_X_REQUESTED_WITH'))

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']) or (request.META.get('HTTP_X_REQUESTED_WITH') and "com.ogd.citizenapps" in request.META.get('HTTP_X_REQUESTED_WITH')):
        return True
    else:
        return False


#get project favorites ids
def get_favorites(request):
    cursor = connection.cursor()
    favorites = [0]
    try:
        sql = """select distinct project_id from visualizations_like
        where user_id = %s and action_type = 'favorite'""" % request.user.id
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            favorites.append(row[0])
    except Exception as e:
        print('Error details: '+ str(e))
    return favorites

#get country, city, etc from ip
def get_ip_details(ip_address=None):
	ipinfo_token = getattr(settings, "IPINFO_TOKEN", None)
	ipinfo_settings = getattr(settings, "IPINFO_SETTINGS", {})
	ip_data = ipinfo.getHandler(ipinfo_token, **ipinfo_settings)
	ip_data = ip_data.getDetails(ip_address)
	return ip_data

#Generate french country names
def countries_fr(request):
    with open(settings.COUNTRY_JSON, encoding='utf-8') as f:
        data_en = json.load(f)
    with open(settings.COUNTRY_INIT_FR_JSON, encoding='utf-8') as f:
        data_fr = json.load(f)
    data = {}
    for key, value in data_en.items():
        if key in data_fr.keys():
            data[value] =  data_fr[key]
        else:
            data[value] =  ""

    with open(settings.COUNTRY_FR_JSON, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent = 4, sort_keys=True, ensure_ascii=False)
    #json.dumps(data, indent = 4, sort_keys=True)
    return True

def reuses_fr(request,import_type=None,nb_imports=None):
    separator = ";"
    file_link = settings.REUSES_FR
    df = pd.read_csv(file_link, sep=separator, encoding='utf8')
    if df is not None:
        list_columns = ['title', 'description', 'type', 'remote_url', 'organization', 'image', 'featured', 'last_modified', 'tags', 'datasets', 'metric.followers']
        query_filter = (df['type'] == "visualization") | (df['type'] == "application")
        df = df.loc[query_filter][list_columns]

        if import_type is not None and import_type == 1:
            df.sort_values(by=['metric.followers'], inplace=True, ascending=False)
        if import_type is not None and import_type == 0:
            df.sort_values(by=['last_modified'], inplace=True, ascending=False)

        count = 0
        for index, row in df.iterrows():
            count = count + 1
            data = Project()
            type = row["type"]
            if row["description"] and row["description"] != "":
                project_notes = row["description"]
            if type == "visualization":
                project_notes = project_notes+"\nType : Visualisation"
            else:
                project_notes = project_notes+"\nType : Application"
            if row["tags"] and row["tags"] != "" and str(row["tags"]) != "nan":
                project_notes = project_notes +"\nTags : "+str(row["tags"])

            data.address_ip = visitor_ip_address(request)
            data.title = row["title"]
            data.notes = project_notes
            data.published_at = row["last_modified"] or datetime.datetime.now()
            data.shared = True
            data.theme_id = int(settings.THEME_REUSES_FR)
            data.status_id = int(settings.STATUS_REUSES_FR)
            data.project_type = "external"
            row["organization"] = str(row["organization"])
            data.contact = row["organization"] if (row["organization"] is not None and row["organization"] != "" and row["organization"] != "nan") else "N/A"
            data.country = "France"
            data.show_in_mobile_apps = True
            #data.state = project_state
            datasets = str(row["datasets"])
            list_datasets = ""
            if datasets != "" and str(row["datasets"]) != "nan":
                all_datasets = datasets.split(",")
                for dt in all_datasets:
                    list_datasets = settings.DATASET_LINK_FR+dt+"/ \n,"
                list_datasets = list_datasets[:-1]
            data.list_datasets = list_datasets
            if str(row["image"]) != "nan":
                data.static_image = row["image"]
            data.link = row["remote_url"] or None
            data.is_popular = True if int(row["featured"]) == 1 else False
            data.nb_favorites = int(row["metric.followers"])
            try:
            	data.save()
                #print("++"+str(datasets)+"++")
            except Exception as e:
            	print('Error details: '+ str(e))
            if nb_imports is not None and count >= nb_imports:
                break
    return True

def get_overview_data(request, code, current_file, project):
    #list_data = list_files(request, [code], project)
    #request.session["explore_file"] = list_data
    #current_file = list_data[code]
    final_query = None
    final_url = "/generate-datatable/"
    final_url += project["code"]+"/"
    final_url += code+"/"

    script = ""
    gauge_quality = ""
    corr = ""
    init_columns = {"dropdown_columns":[], "columns": []}

    project_code = project["code"]

    if "quality" in project["project_settings"]["files"][code]:
        current_file["data_quality"] = project["project_settings"]["files"][code]["quality"]
        current_file["quality"] = project["project_settings"]["files"][code]["quality"]["average"]

    if not current_file["is_requested"] and project:
       if code in project["project_settings"]["files"]:
           df_file_code = project["project_settings"]["files"][code]["df_file_code"]

       final_query = "select * from " + "df_" + df_file_code + " WHERE 1 = 1 "
       final_url += final_query+"/"
       init_columns = init_columns_datatable(request, project, current_file, final_query)
       script = datatable_script("table-content",final_url, init_columns)
       params = {}
       params["title"] = _("Data Quality")
       params["id"] = "dqfile"
       params["variable"] = "dqfile"
       params["min"] = 0
       params["max"] = 100
       params["value"] = current_file["data_quality"]["average"]
       params["unit"] = "%"
       gauge_quality = gauge_highcharts(request, params)
       corr = get_corr_data(request, code)

    return {"final_url": final_url, "final_query": final_query, "script": script, "project_code":project_code,
           "file_code": code, "dropdown_columns": init_columns["dropdown_columns"],
           "gauge_quality": gauge_quality, "current_file": current_file, "corr": corr}

#Get correlation table
def get_corr_data(request, file_code):
    current_project = request.session["current_project"]
    result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
    request.session["list_selectedfiles"][file_code]["file_link"], request.session["list_selectedfiles"][file_code]["refresh_timeout"],
    current_project["project_settings"]["files"][file_code]["df_file_code"], 0, request.session["convert_dict"][file_code])

    df = result_df["df"]

    if df is None:
        return JsonResponse(data)

    keys_num = list(request.session["measures"][file_code].keys())
    keys_num = keys_num[:-1]
    df_num = df[keys_num]
    plot_corr = ""
    if len(keys_num) > 1:
        df_corr = df_num.corr()
        project_settings = current_project["project_settings"]
        columns = project_settings["files"][file_code]["columns"]

        column_names = {}
        for col in df_corr.columns:
            column_names[col] = columns[str(col)]["label"]
        df_corr.rename(columns = column_names, inplace = True)

        plot_corr = create_corr(df_corr, False, None, None, 1)
    else:
        plot_corr = "<p class='sm-marg center'><b>"+_("Correlation")+"</b></p><br/>"+_("No numerical columns to generate the correlation.")

    full_result =  "<div id='corr' class='center'>"+plot_corr+"</div>"
    return full_result
