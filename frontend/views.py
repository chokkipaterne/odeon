from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.messages import get_messages
from django.utils.translation import ugettext as _
from django.utils.translation import activate, LANGUAGE_SESSION_KEY
from .forms import UploadFileForm, NewUserForm, ExternalLinkForm
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.urls import reverse
import numpy as np
import pandas as pd
import os, time
import json
import math
import decimal
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
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
from utils.viz import *
from utils.data_portal import *
from django.db.models import Q
import plotly
from urllib.parse import urlparse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from random import seed
from random import randint
from django.utils.text import slugify

#set language
def set_language(request):
    if request.method == 'POST':
        if request.POST.get('locale'):
            user_language = request.POST.get('locale')
            activate(user_language)
            request.session[LANGUAGE_SESSION_KEY] = user_language
            load_data(request, Theme, "list_themes", 1)
            load_data(request, Theme, "list_themes_mobile", 1)
            get_project_statuses(request, 1)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            return redirect("frontend:home_page")
    return redirect("frontend:home_page")

#home page
def home_page(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    load_data(request, Theme, "list_themes", 0)
    request.session["active_service"] = "ODEON"
    if "countries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["countries"] = countries

    now = datetime.datetime.now()
    now_str = now.strftime("%d/%m/%y")

    reload = False
    if "reload_time" not in request.session:
        reload = True
    else:
        prev = request.session["reload_time"]
        prev = datetime.datetime.strptime(prev, "%d/%m/%y")
        diff = (now-prev).days
        if diff >= settings.RELOAD_TIMEOUT:
            reload = True

    if reload:
        load_data(request, Theme, "list_themes", 1)
        get_countries(request)
        request.session["reload_time"] = now_str
    else:
        load_data(request, Theme, "list_themes", 0)
        #get_countries(request)
        if "used_countries" not in request.session:
            get_countries(request)

    #handle feedback form
    if request.method == 'POST':
        if request.POST.get('wremail'):
            if not request.POST.get('wremail') or not request.POST.get('wrcountry') or not request.POST.get('wrstate'):
                messages.error(request, _("All fields are required"))
            else:
                email = cleanhtml(request.POST.get('wremail'))
                country = request.POST.get('wrcountry')
                state = cleanhtml(request.POST.get('wrstate'))

                try:
                    subscribe, created = SubscribeDataArea.objects.get_or_create(country=country, email=email, state=state, defaults={'country': country, 'email': email, 'state': state})
                    messages.success(request, _("Subscription saved successfully"))
                except Exception as e:
                    print('Error details: '+ str(e))
                    messages.error(request, _("Something went wrong"))

        elif request.POST.get('message') and request.POST.get('full_name') and request.POST.get('email'):
            message = "Content of the feedback: "
            if request.POST.get('full_name'):
                message += "\nFull Name: "+request.POST.get('full_name')
            if request.POST.get('email'):
                message += "\nEmail: "+request.POST.get('email')
            message += "\nMessage: "+request.POST.get('message')
            send_mail(
                    settings.EMAIL_SUBJECT,
                    message,
                    settings.EMAIL_FROM,
                    settings.EMAIL_RECEIVERS,
                    fail_silently=False,
                )
            messages.success(request, _("Feedback sent successfully"))
        else:
            messages.error(request, _("Please fill message"))

    return render(request = request, template_name='frontend/index.html', context = {})

#About page
def about(request):
    request.session["active_service"] = "ODEON"
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

    return render(request = request, template_name='frontend/about.html', context = {})

#About page
def about_apps(request):
    request.session["active_service"] = "ODEON"
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

    return render(request = request, template_name='frontend/about_apps.html', context = {})

#How It works page
def how_works(request):
    request.session["active_service"] = "ODE"
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

    return render(request = request, template_name='frontend/how_works.html', context = {})

#Privacy page
def privacy(request):
    request.session["active_service"] = "ODEON"
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)

    return render(request = request, template_name='frontend/privacy.html', context = {})

#home page
def home_proto(request):
    #activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    activate("en")
    request.session["active_service"] = "ODE"
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    load_data(request, Theme, "list_themes", 0)
    if "countries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["countries"] = countries
    if "used_countries" not in request.session:
        get_countries(request)

    #handle feedback form
    if request.method == 'POST':
        if request.POST.get('message') and request.POST.get('full_name') and request.POST.get('email'):
            message = "Content of the feedback: "
            if request.POST.get('full_name'):
                message += "\nFull Name: "+request.POST.get('full_name')
            if request.POST.get('email'):
                message += "\nEmail: "+request.POST.get('email')
            message += "\nMessage: "+request.POST.get('message')
            send_mail(
                    settings.EMAIL_SUBJECT_PROTO,
                    message,
                    settings.EMAIL_FROM,
                    settings.EMAIL_RECEIVERS,
                    fail_silently=False,
                )
            messages.success(request, _("Feedback sent successfully"))
        else:
            messages.error(request, _("Please fill message"))

    return render(request = request, template_name='frontend/home_proto.html', context = {})

#Share project to friend by mail
def share_project(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    emails = []
    message = ""
    if request.method == 'POST' and request.POST.get('body') and request.POST.get('emails'):
        if request.POST.get('emails'):
            emails = (request.POST.get('emails')).split(",")
        if request.POST.get('body'):
            message = request.POST.get('body')

        try:
            send_mail(
                    settings.SUBJECT_SHARE,
                    message,
                    settings.EMAIL_FROM,
                    emails,
                    fail_silently=False,
                )
        except Exception as e:
            print('Error details: '+ str(e))

        data = {'success': True, 'message': _('Message sent successfully')}
    return JsonResponse(data)

#register new account page
def register_page(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _("New account created:")+" "+username)
            login(request, user)
            return redirect("frontend:home_page")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            password1 = form.data['password1']
            password2 = form.data['password2']
            email = form.data['email']
            for msg in form.errors.as_data():
                if msg == 'email':
                    messages.error(request, f"Declared {email} is not valid")
                if msg == 'password2' and password1 == password2:
                    messages.error(request, f"Selected password: {password1} is not strong enough")
                elif msg == 'password2' and password1 != password2:
                    messages.error(request, f"Password: '{password1}' and Confirmation Password: '{password2}' do not match")
    else:
        form = NewUserForm()
    return render(request = request,
                  template_name = "frontend/register.html",
                  context={"form":form})

#login page
def login_page(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session["current_user_type"] = user.user_type
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect("frontend:home_page")
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            messages.error(request, _("Invalid username or password."))
    else:
        form = AuthenticationForm()
    return render(request = request,
                      template_name = "frontend/login.html",
                      context={"form":form})

#logout
def logout_page(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    current_lang = (LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE
    if request.method == 'POST':
        messages.info(request, _("Logged out successfully!"))
        logout(request)
        request.session["current_user_type"] = settings.NON_EXPERT
        request.session[LANGUAGE_SESSION_KEY] = current_lang
        return redirect("frontend:home_page")

def switch_display(request):
    next = request.GET.get('next', "")
    if ("current_user_type" not in request.session):
        if request.user and request.user.id:
            request.session["current_user_type"] = request.user.user_type
        else:
            request.session["current_user_type"] = settings.NON_EXPERT
    else:
        if request.session["current_user_type"] == settings.NON_EXPERT:
            request.session["current_user_type"] = settings.EXPERT
        else:
            request.session["current_user_type"] = settings.NON_EXPERT
    if request.session["current_user_type"] == settings.NON_EXPERT:
        messages.success(request, _("Switch to Beginner display"))
    else:
        messages.success(request, _("Switch to Expert display"))
    response = redirect(next)
    return response

#upload data/ get started
def get_started(request, code = ''):
    #print(timezone.now)
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    get_project_statuses(request)
    project_type = ""
    project_theme = ""
    project_title = ""
    project_notes = ""
    project_contact = ""
    project_link = ""
    project_state = ""
    status = ""
    list_datasets = ""
    user_request_type = request.GET.get('user_type', "")
    explore_file_code = request.GET.get('explore_file', "")
    view_type = request.GET.get('view_type', "")
    #print(explore_file_code)
    goto = False

    storage = get_messages(request)
    for message in storage:
        comp = _("Project saved successfully")
        if str(comp) in str(message):
            goto = "adddts"

    if user_request_type != "":
        request.session["user_request_type"] = user_request_type
    if user_request_type  == "" and "user_request_type" in request.session:
        user_request_type = request.session["user_request_type"]
    if view_type != "":
        request.session["current_user_type"] = view_type

    shared = True
    image = None
    p_code = ""
    add_data = False
    img = None
    country = settings.DEFAULT_COUNTRY
    if "countries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["countries"] = countries

    if request.user and request.user.id:
        project_contact = request.user.username+"|"+request.user.email

    if request.method == 'POST' or view_type == settings.NON_EXPERT:
        if request.method == 'POST':
            project_type = request.POST.get("project_type")
            status  = request.POST.get("status")
            project_theme = request.POST.get("project_theme")
            country = request.POST.get("country")
            project_state = request.POST.get("project_state")
            p_code = request.POST.get("p_code")
            if project_theme:
                project_theme = str(project_theme)
            project_title = request.POST.get("project_title")
            project_notes = request.POST.get("project_notes")
            project_contact = request.POST.get("project_contact")
            shared = request.POST.get("shared")
            user_request_type = request.POST.get("user_request_type")
            if shared:
                shared = True
            else:
                shared = False
            if project_type == 'external':
                project_link = request.POST.get("project_link")
            if project_type != 'internal':
                list_datasets = request.POST.get("list_datasets")
        else:
            request.session["current_user_type"] = view_type
            project_type = 'internal'
            country = "Global"
            project_state = "Global"
            p_code = ""
            project_theme = settings.DEFAULT_THEME_ID
            project_title = "Not defined (please update it)"
            project_notes = "Not defined (please update it)"
            project_contact = "Not defined (please update it)"
            user_request_type = view_type
            shared = False

            #Laod existent project in case there is no vizs yet
            all_data = Project.objects.filter(address_ip__exact=visitor_ip_address(request)).order_by('-updated_at', '-created_at')
            all_data = all_data.exclude(project_settings__has_key='vizs')
            if len(all_data) > 0:
                data = all_data[0]
                request.session['project_code'] = data.code
                request.session['dash_code'] = data.dash_code
                messages.success(request, _("Project loaded successfully"))
                for variable in ["current_project", "file_codes", "list_selectedfiles", "used_countries"]:
                    if variable in request.session:
                        del request.session[variable]
                return redirect("frontend:get_started")

        verif = 0
        if project_type and country and project_state and project_theme and project_notes and project_title and project_contact:
            if project_type == 'external' and project_link:
                verif = 1
            elif project_type != 'external':
                verif = 1

        if verif == 1:
            if request.FILES and 'image' in request.FILES:
                img = request.FILES['image']
            if img:
                img_extension = os.path.splitext(img.name)[1]
                img_name = os.path.splitext(img.name)[0]
                image = 'projects/'+str(randint(1000, 9999))+"_"+img_name+img_extension
                path = default_storage.save(image, ContentFile(img.read()))

            if p_code != "":
                try:
                    data = Project.objects.get(code__exact=p_code)
                    project_code = data.code
                except Exception as e:
                    data = Project()
            else:
                data = Project()
                data.address_ip = visitor_ip_address(request)

            data.title = project_title
            data.notes = project_notes
            if not data.shared and shared:
                data.published_at = datetime.datetime.now()
            data.shared = shared
            data.theme_id = int(project_theme)
            #Set status to complete
            if project_type == 'internal':
                data.status_id = 3
            else:
                data.status_id = int(status)

            data.project_type = project_type
            data.contact = project_contact
            data.country = country
            data.state = project_state
            if project_type != 'internal':
                data.list_datasets = list_datasets

            if project_type == 'proposed' and p_code == "" and user_request_type:
                data.user_request_type = user_request_type

            if image:
                data.image = image
            data.link = project_link
            try:
                data.save()
                request.session['project_code'] = data.code
                request.session['dash_code'] = data.dash_code
                messages.success(request, _("Project saved successfully"))

                for variable in ["current_project", "file_codes", "list_selectedfiles", "used_countries"]:
                    if variable in request.session:
                        del request.session[variable]
                if project_type != 'internal':
                    return redirect("frontend:get_started_type", code="update")
                else:
                    return redirect("frontend:get_started")
            except Exception as e:
                print('Error details: '+ str(e))
                default_storage.delete(image)
                image = None
        else:
            messages.error(request, _("Fields * are required"))
    elif code and code in ["internal", "external", "proposed", "create"]:
        if code == "internal":
            shared = False
        for variable in ["current_project", "file_codes", "list_selectedfiles", "project_code", "dash_code"]:
            if variable in request.session:
                del request.session[variable]

        if code != 'create':
            project_type = code


    if ("current_user_type" not in request.session):
        request.session["current_user_type"] = settings.NON_EXPERT

    #get demo files
    load_data(request, Theme, "list_themes", 0)

    load_data(request, UploadFile, "list_demofiles", 1)
    #get datatypes
    load_data(request, DataType, "list_datatypes", 0)
    #get current project
    load_full_project(request, Project, "current_project", 0)
    #get select files
    load_data(request, UploadFile, "list_selectedfiles", 0)
    #print(request.session["convert_dict"])
    #get open data portals
    load_data(request, DataPortal, "list_dataportals", 1)
    load_data(request, PlatformPortal, "list_platformportals", 1)

    nbfiles = len(request.session["file_codes"])
    externalForm = ExternalLinkForm()
    current_project = request.session["current_project"]
    if current_project:
        project_type = current_project["project_type"]
        project_link = current_project["link"] or ""
        project_title = current_project["title"]
        project_notes = current_project["notes"]
        project_contact = current_project["contact"]
        project_theme = current_project["theme"]
        status = int(current_project["status"])
        country = current_project["country"]
        project_state = current_project["state"]
        shared = current_project["shared"]
        image = current_project["image"]
        p_code = current_project["code"]
        list_datasets = current_project["list_datasets"]

        if code == "":
            add_data = True
        if goto == "adddts" and project_type == "internal":
            add_data = True
            goto = False

    load_data(request, Project, "my_projects", 1, project_type)


    title_platform = _('ODEON')
    if project_type == "internal":
        project_types = [
            ('internal', _('Create a quick prototype of your project idea'))
        ]
        current_template = "proto_layout.html"
        title_platform = _('ODE')
        request.session["active_service"] = "ODE"
    else:
        project_types = [
            #('internal', _('Create a quick prototype of your project idea')),
            ('external', _('Register an OGD reuse')),
            ('proposed', _('Suggest a project'))
        ]
        current_template = "frontend_layout.html"
        title_platform = _('ODEON')
        request.session["active_service"] = "ODEON"

    context = {"nbfiles": nbfiles, "externalForm": externalForm, "project_types": project_types,
    "project_type": project_type, "project_title": project_title, "project_notes": project_notes
    ,"project_contact": project_contact, "shared": shared, "image": image, "project_theme": project_theme, "status": status,
    "project_link": project_link, "p_code": p_code, "add_data": add_data, "country": country, "project_state": project_state,
    "user_request_type": user_request_type, "current_template":  current_template, "title_platform": title_platform,
    "goto":goto, "list_datasets":list_datasets, "current_file": False, "file_code": ""}

    if add_data == True:
        if request.session["list_selectedfiles"].keys() and len(request.session["list_selectedfiles"].keys()) > 0 and explore_file_code == "":
            explore_file_code = list(request.session["list_selectedfiles"].keys())[0]

        if explore_file_code != "" and explore_file_code in request.session["list_selectedfiles"]:
            current_file = request.session["list_selectedfiles"][explore_file_code]
            overview_data = get_overview_data(request, explore_file_code, current_file, request.session["current_project"])
            for key, value in overview_data.items():
                context[key] = value

    return render(request = request,
                  template_name='frontend/get_started.html',
                  context = context)

#File upload
def select_file(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'is_valid': False, 'message': _('Something went wrong')}
    if request.method == 'POST' and request.POST.get('file_selected'):
        file_code = request.POST.get('file_selected')
        if file_code in request.session["list_selectedfiles"]:
            data = {'is_valid': False, 'message': _('File already exists')}
            return JsonResponse(data)
        if file_code not in request.session["list_demofiles"]:
            return JsonResponse(data)
        current_file = request.session["list_demofiles"][file_code]
        insight = _("Add online resource #{}# to project").format(request.session["list_demofiles"][file_code]["title"])
        data = add_file(request, current_file, insight)
        return JsonResponse(data)

#Load existant project
def load_project(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        if request.POST.get('project_code'):
            project_code = request.POST.get('project_code').strip().lower()
            project_code = project_code.replace(" ", "")
            if project_code:
                project_code = project_code.split("(")[0]
            try:
                data = Project.objects.get(code__exact=project_code)
            except:
                data = None
            if data is not None:
                request.session['project_code'] = data.code
                request.session['dash_code'] = data.dash_code
                for variable in ["current_project", "file_codes", "list_selectedfiles"]:
                    if variable in request.session:
                        del request.session[variable]
                messages.success(request, _("Project loaded successfully"))
                return redirect("frontend:get_started")
                #if bool(data.project_settings):
                #    return redirect("frontend:visualization")
            else:
                messages.error(request, _("Project code invalid"))
        else:
            messages.error(request, _("Please fill code"))
    return redirect("frontend:get_started_type", code="update")

#File upload
def file_upload(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            data = None
            try:
                file = request.FILES['file_name']
                file_name = file.name
                file_ext = file_name.split(".")[-1]
                if file_ext in settings.LIST_EXTENSIONS:
                    data = form.save()
                    now = datetime.datetime.now()
                    format_iso_now = now.isoformat()

                    language = settings.LANGUAGE_CODE
                    if LANGUAGE_SESSION_KEY in request.session:
                        language = request.session[LANGUAGE_SESSION_KEY]

                    more_details = {"title": data.title, "dataset_id": "",
                     "description": "", "modified": format_iso_now,
                     "language": [language], "fields": {}}

                    current_file = {"id":data.pk, "code":data.code, "file_link":data.file_link, "title":data.title, "file_ext":data.file_ext
                    , "is_demo":data.is_demo, "refresh_timeout":data.refresh_timeout, "init_settings":data.init_settings, "updated_at":data.updated_at,
                     "more_details": more_details}
                    insight = _("Add new file #{}# to project").format(current_file["title"])
                    data = add_file(request, current_file, insight)
                else:
                    data = {'is_valid': False, 'message': _('Format file invalid')}
            except Exception as e:
                print('Error details: '+ str(e))
                if data is not None:
                    file_link = settings.MEDIA_ROOT+settings.UPLOAD_FILES+data.code+data.file_ext
                    if os.path.isfile(file_link):
                        os.remove(file_link)
                    data.delete()
                data = {'is_valid': False, 'message': _('File invalid')}
        else:
            data = {'is_valid': False, 'message': _('Something went wrong')}
        return JsonResponse(data)

#External link
def external_link(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        form = ExternalLinkForm(request.POST)
        if form.is_valid():
            data = None
            try:
                data = form.save()
                now = datetime.datetime.now()
                format_iso_now = now.isoformat()

                language = settings.LANGUAGE_CODE
                if LANGUAGE_SESSION_KEY in request.session:
                    language = request.session[LANGUAGE_SESSION_KEY]

                more_details = {"title": data.title, "dataset_id": "",
                 "description": data.more_details["description"] or "", "modified": format_iso_now,
                 "language": [language], "fields": {}}

                current_file = {"id":data.pk, "code":data.code, "file_link":data.file_link, "title":data.title, "file_ext":data.file_ext
                , "is_demo":data.is_demo, "refresh_timeout":data.refresh_timeout, "init_settings":data.init_settings, "updated_at":data.updated_at,
                 "more_details": more_details}
                insight = _("Add new external link #{}# to project").format(current_file["title"])
                data = add_file(request, current_file, insight)
            except:
                if data is not None:
                    file_link = settings.MEDIA_ROOT+settings.UPLOAD_FILES+data.code+data.file_ext
                    if os.path.isfile(file_link):
                        os.remove(file_link)
                    data.delete()
                data = {'is_valid': False, 'message': _('File invalid')}
        else:
            if form.errors:
                message = ""
                for field, items in form.errors.items():
                    for item in items:
                        if message != "":
                            message +="<br/>"
                        if field == "__all__":
                            message +='{}'.format(item)
                        else:
                            message +='{}: {}'.format(field, item)
                data = {'is_valid': False, 'message': message}
            else:
                data = {'is_valid': False, 'message': _('Please check your inputs')}
        return JsonResponse(data)

#Requested data
def requested_data(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        if request.POST.get('requested_title') and request.POST.get('requested_description') and request.POST.get('requested_contact') \
        and request.POST.get('requested_country') and request.POST.get('requested_state'):
            title = request.POST.get('requested_title')
            description = request.POST.get('requested_description')
            pcode = request.POST.get('requested_data_pcode').strip()
            contact = request.POST.get('requested_contact').strip()
            country = request.POST.get('requested_country').strip()
            state = request.POST.get('requested_state').strip()
            #theme = request.POST.get('requested_theme')

            data = UploadFile()
            data.title = title
            data.file_link = "#"
            #data.description = description
            #data.theme = theme
            data.country = country
            data.state = state
            data.is_requested = True
            data.data_provided = False

            now = datetime.datetime.now()
            format_iso_now = now.isoformat()

            language = settings.LANGUAGE_CODE
            if LANGUAGE_SESSION_KEY in request.session:
                language = request.session[LANGUAGE_SESSION_KEY]

            more_details = {"title": title, "dataset_id": "",
             "description": description or "", "modified": format_iso_now,
             "language": [language], "fields": {}, "contact":contact}
            data.more_details = more_details
            data.save()
            if pcode and 'project_code' in request.session and pcode == request.session['project_code']:
                current_file = {"id":data.id, "code":data.code, "file_link":data.file_link, "title":data.title, "file_ext":data.file_ext
                , "is_demo":data.is_demo, "refresh_timeout":data.refresh_timeout, "init_settings":data.init_settings, "updated_at":data.updated_at,
                 "more_details": more_details, "is_requested": data.is_requested}
                insight = _("Add new requested data #{}# to project").format(current_file["title"])
                data = add_file(request, current_file, insight)
            else:
                data = {'is_valid': True, 'message': _('Successful data request')}
        else:
            data = {'is_valid': False, 'message': _('Please check your inputs')}
        return JsonResponse(data)

#Delete File from project
def delete_file(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        if request.POST.get('file_code'):
            file_code = request.POST.get('file_code')
            insight = _("Delete file #{}# from project").format(request.session["list_selectedfiles"][file_code]["title"])
            data = remove_file(request, file_code, insight)
        else:
            data = {'deleted': False, 'message': _('Something went wrong')}
        return JsonResponse(data)

#View File
def view_file(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('file_code') and request.POST.get('file_code') in request.session["list_selectedfiles"]:
            file_code = request.POST.get('file_code')
            current_project = request.session["current_project"]
            if not current_project:
                return JsonResponse(data)
            result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
            request.session["list_selectedfiles"][file_code]["file_link"], request.session["list_selectedfiles"][file_code]["refresh_timeout"],
            current_project["project_settings"]["files"][file_code]["df_file_code"], 0, request.session["convert_dict"][file_code])
            df = result_df["df"]

            if df is None:
                return JsonResponse(data)

            action_type = request.POST.get('action_type')
            message =""

            #update dattype column
            if action_type == "transform":
                if request.POST.get('column_data') and request.POST.get('type_data'):
                    column_data = request.POST.get('column_data')
                    type_data = request.POST.get('type_data')
                    #update datatype column
                    try:
                        insight = _("Change datatype of column #{}# from #{}# to #{}#").format(column_data,
                        request.session["real_convert_dict"][file_code][column_data],
                        request.session["list_datatypes"][str(type_data)]["name"])

                        df = update_column(request, df, file_code, column_data, type_data, insight)
                        message = _("Update successful")
                    except:
                        data = {'success': False, 'message': _('Something went wrong')}
                        return JsonResponse(data)

                    if df is None:
                        return JsonResponse(data)

            #end update datatype column
            keys = list(request.session["real_convert_dict"][file_code].keys())
            values = list(request.session["real_convert_dict"][file_code].values())
            columns = request.session["id_convert_dict"][file_code]
            mz_table = missing_values_table(df, keys, values)
            #print(keys)
            #print(values)
            plot_table = create_table(df, True)
            cols = list(mz_table.columns)
            #reorder attributes
            plot_mz = create_table(mz_table, False, None, None, 0)
            keys_num = list(request.session["measures"][file_code].keys())
            keys_num = keys_num[:-1]
            df_num = df[keys_num]
            plot_corr = ""
            if len(keys_num) > 1:
                df_corr = df_num.corr()
                #df_corr.insert(0, " ",keys_num, True)
                #plot_corr = create_table(df_corr, False, None, None, 1)
                plot_corr = create_corr(df_corr, False, None, None, 1)

            full_result =  "<div id='datatypes'>"+plot_mz+"<div id=corr>"+plot_corr+"</div></div>" + plot_table
            data = {'success': True, 'plot_table':full_result, 'keys': keys, 'columns': columns, 'message': message, 'title': request.session["list_selectedfiles"][file_code]["title"]}
        else:
            data = {'success': False, 'message': _('Something went wrong')}
        return JsonResponse(data)

#get unique values of column
def get_unique_values(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('un_column') and request.POST.get('un_file'):
            file_code = request.POST.get('un_file')
            column = request.POST.get('un_column')
            unique_values = retrieve_unique_values(request,file_code, column)
            data = {'success': True, 'unique_values': unique_values}
    return JsonResponse(data)

#Visualization
def visualization(request, code=""):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    #get current project
    load_full_project(request, Project, "current_project", 0)

    #get select files
    load_data(request, UploadFile, "list_selectedfiles", 0)

    files = check_files(request)
    if len(files) <= 0 or "show_vizmenu" not in request.session or not request.session["show_vizmenu"]:
         return redirect("frontend:get_started")

    files = []
    vizs = []
    load_data(request, VizMark, "list_vizmarks", 0)
    load_data(request, VizType, "list_viztypes", 1)
    load_data(request, Feature, "list_features", 0)
    #get list vizgoals
    load_data(request, VizGoal, "list_vizgoals", 1)
    request.session["current_project"]["list_vizmarks"] = request.session["list_vizmarks"]
    request.session["current_project"]["list_viztypes"] = request.session["list_viztypes"]


    class_viz = ""
    class_dash = "hide"
    if code and code == "dash":
        class_dash = ""
        class_viz = "hide"

    #if "current_user_type" in request.session and request.session["current_user_type"] != settings.NON_EXPERT:
    #    return render(request = request,
    #                template_name='frontend/visualization.html',
    #                context = {"files": files, "plot_div": "", "vizs": vizs,
    #                "class_viz": class_viz, "class_dash": class_dash, "code_viz_init":code})
    #else:
    nbfiles = len(request.session["file_codes"])

    return render(request = request,
                template_name='frontend/visualization_guide.html',
                context = {"files": files, "plot_div": "", "vizs": vizs,
                "class_viz": class_viz, "class_dash": class_dash, "code_viz_init":code, "nbfiles": nbfiles})


#get list of actions history
def action_traceability(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        results = retrieve_action_traceability(request)
        data = {'success': True, 'results': results[::-1]}
    return JsonResponse(data)

#create visualisation based on attributes
def create_visualization(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        graph_parameters = {}
        if request.POST.get('files') and len(json.loads(request.POST.get('files')))==1:
            for key, value in request.POST.items():
                if key == "search_viztype" or key == "csrfmiddlewaretoken" :
                    continue
                else:
                    try:
                        variable = json.loads(value)
                        graph_parameters[key] = variable
                    except:
                        variable = value
                        graph_parameters[key] = variable
            #print(graph_parameters)
            if "recommend_viz" in graph_parameters["visualization_action"]:
                if graph_parameters["alter_data"] != "" and bool(graph_parameters["alter_data"]) and graph_parameters["visualization_action"] == "recommend_viz":
                    request.session["alter_data"] = copy.deepcopy(graph_parameters["alter_data"]["result"])
                else:
                    request.session["alter_data"] = {}

                if "recommend_graph" in request.session and "previous_rec" in request.session  and request.session["previous_rec"] != "recommend_viz":
                    request.session["backup_recommend_graph"] = copy.deepcopy(request.session["recommend_graph"])
                    request.session["backup_nb_recommend_graph"] = request.session["nb_recommend_graph"]
                    request.session["backup_end_recommend_graph"] = request.session["end_recommend_graph"]
                    request.session["backup_vzcode_recommend_graph"] = request.session["vzcode_recommend_graph"]

                request.session["previous_rec"] = graph_parameters["visualization_action"]

                request.session["recommend_graph"] = {}
                request.session["nb_recommend_graph"] = 0
                request.session["end_recommend_graph"] = 0
                request.session["vzcode_recommend_graph"] = graph_parameters["visualization_code"]
                if graph_parameters["visualization_action"] == "recommend_viz":
                    has_num = 0
                    for v in graph_parameters['attribs']:
                        if (v["realtype"] in ["int", "float", "auto"] and v["dimmeasopt"] != 'bins') or (v["realtype"] in ['lat', 'lon', 'point', 'shape']):
                            has_num = 1
                            break
                    if has_num == 0:
                        graph_parameters['attribs'].append({'fulltext': 'count', 'dimmeasopt': 'valexact', 'file': graph_parameters['files'][0], 'dt': 0,
                        'realtype': 'auto', 'name': 'count', 'type': 'auto', 'ty': 'meas', 'target': 'attribs'})
                elif graph_parameters["visualization_action"] == "recommend_viz1":
                    del graph_parameters["attribs"]
                    vzmy = "vzm"+settings.VIZ_Y
                    vzmx = "vzm"+settings.VIZ_X
                    has_num = 0
                    for v in graph_parameters[vzmx]:
                        if (v["realtype"] in ['point', 'shape']):
                            has_num = 1
                            break
                    if has_num == 0 and len(graph_parameters[vzmy]) == 0 and len(graph_parameters["vzm"+settings.VIZ_HIERACHY]) == 0:
                        graph_parameters[vzmy].append({'fulltext': 'count', 'dimmeasopt': 'valexact', 'file': graph_parameters['files'][0], 'dt': 0,
                        'realtype': 'auto', 'name': 'count', 'type': 'auto', 'ty': 'meas', 'target': 'vm2'})
                elif graph_parameters["visualization_action"] == "dist_recommend_viz":
                    data = generate_dist_viz(request, graph_parameters)
                elif graph_parameters["visualization_action"] == "empty_recommend_viz":
                    if graph_parameters["is_task"] == 0:
                        data = generate_analysis_viz(request, graph_parameters)
                    else:
                        data = generate_tasks_viz(request, graph_parameters)

                if graph_parameters["visualization_action"] == "recommend_viz" or graph_parameters["visualization_action"] == "recommend_viz1":
                    data = recommend_graph(request, graph_parameters)
                data["nb_recommend_graph"] = request.session["nb_recommend_graph"]
            else:
                for val in ["attribs", "expert", "intermediate", "non-expert", "threshold"]:
                    del graph_parameters[val]
                vzmy = "vzm"+settings.VIZ_Y
                vzmx = "vzm"+settings.VIZ_X
                has_num = 0
                for v in graph_parameters[vzmx]:
                    if (v["realtype"] in ['point', 'shape']):
                        has_num = 1
                        break
                type_viz = graph_parameters["type_viz"]
                include_marks = request.session["list_viztypes"][str(type_viz)]["include_marks"]
                include_marks = include_marks.split(",")
                if has_num == 0 and len(graph_parameters[vzmy]) == 0 and len(graph_parameters['files']) > 0 and (str(settings.VIZ_Y) in include_marks):
                    graph_parameters[vzmy].append({'fulltext': 'count', 'dimmeasopt': 'valexact', 'file': graph_parameters['files'][0], 'dt': 0,
                    'realtype': 'auto', 'name': 'count', 'type': 'auto', 'ty': 'meas', 'target': 'vm2'})
                if int(request.POST.get('submit_full_data')) == 1 or (int(request.POST.get('submit_full_data')) == 0 and not bool(request.session["previous_data"])):
                    request.session["previous_data"] = {}
                    request.session["features"] = ""
                    request.session["score_settings"] = ""
                    data = generate_graph(request, graph_parameters)
                else:
                    data = generate_graph(request, graph_parameters,True)
        else:
            data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)

#Save scores
def save_score(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        variables = {}
        if request.POST.get('viz_scores'):
            for key, value in request.POST.items():
                if key == "csrfmiddlewaretoken" :
                    continue
                else:
                    try:
                        variable = json.loads(value)
                        variables[key] = variable
                    except:
                        variable = value
                        variables[key] = variable
            #print(variables)
            data = record_scores(request, variables)
        else:
            data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)

#Add viz to dashboard
def addto_dash(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('add_code'):
            rep = add_viz(request, request.POST.get('add_code'), request.POST.get('add_type_viz'), request.POST.get('add_viz_data'), request.POST.get('add_viz_notes'), request.POST.get('add_plot_div'))
            data = {'success': rep['success'], 'plot_div': rep['plot_div']}
        else:
            data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)

#Add viz to embed
def addto_embed(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('embed_code'):
            rep = embed_viz(request, request.POST.get('embed_code'), request.POST.get('embed_type_viz'), request.POST.get('embed_viz_data'), request.POST.get('embed_viz_notes'), request.POST.get('embed_plot_div'))
            data = {'success': rep['success'], 'iframe': rep['iframe']}
        else:
            data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)

#Save settings dashboard
def save_dashboard(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        dash_parameters = {}
        if request.POST.get('files_dash') and len(json.loads(request.POST.get('files_dash')))<=1:
            for key, value in request.POST.items():
                if key == "csrfmiddlewaretoken" :
                    continue
                else:
                    try:
                        variable = json.loads(value)
                        dash_parameters[key] = variable
                    except:
                        variable = value
                        dash_parameters[key] = variable
            #print(dash_parameters)
            data = save_dash_info(request, dash_parameters)
        else:
            data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)

#Show Dashboard
def dashboard(request, code, theme='', trans_code=''):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    try:
        data = Project.objects.get(dash_code__exact=code)
    except:
        data = None

    embed_link = ""

    if data:
        code = data.code
        embed_link = settings.URL_DASH_IFRAME
        embed_link = embed_link.replace('#dash_code#', data.dash_code)

        project = {"id":data.pk, "project_settings":data.project_settings,
        "project_history":data.project_history, "user":(data.user and data.user.username), "title":data.title, "notes":data.notes, "shared":data.shared, "code":data.code, "dash_code":data.dash_code,
        "updated_at": data.updated_at.strftime("%d/%m/%Y")}

        project_settings = data.project_settings
        if "files" in project_settings:
            dashfile_codes = []
            for keyfile, file in project_settings["files"].items():
                dashfile_codes.append(keyfile)
            list_data = list_files(request, dashfile_codes, project)
            project["dash_files"] = list_data
        load_data(request, VizMark, "list_vizmarks", 0)
        load_data(request, VizType, "list_viztypes", 0)
        project["list_vizmarks"] = request.session["list_vizmarks"]
        project["list_viztypes"] = request.session["list_viztypes"]
    else:
        messages.error(request, _("Code invalid"))
        return redirect("frontend:home_page")

    display = request.GET.get('display', "nov")
    showhide_display = "showhide#"+display
    vzshde_display = "vzshde#"+display
    is_mobile = mobile(request)

    context = {"project": project, "code": code, "display": display, "showhide_display": showhide_display,
    "vzshde_display": vzshde_display, "is_mobile": is_mobile, "embed_link": embed_link}

    context["trans_code"] = trans_code
    context["current_theme"] = theme

    if trans_code != "" and theme != "":
        view_trans = True
        arr = theme.split("-")
        theme_id = arr[-1]
        theme_id = str(theme_id)
        context["theme_id"] = theme_id
        mytheme = Theme.objects.get(pk=theme_id)
        context["mytheme"] = mytheme
        context["trans_code"] = trans_code


    return render(request = request,
                template_name='frontend/dashboard.html',
                context = context)

#Show embed
def embed(request, project_code, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    try:
        data = Project.objects.get(dash_code__exact=project_code)
    except:
        data = None

    viz = ""

    if data:
        project_code = data.code
        project = {"id":data.pk, "project_settings":data.project_settings,
        "project_history":data.project_history, "user":(data.user and data.user.username), "title":data.title, "notes":data.notes, "shared":data.shared, "code":data.code, "dash_code":data.dash_code,
        "updated_at": data.updated_at.strftime("%d/%m/%Y")}

        project_settings = data.project_settings
        if "embed" in project_settings:
            if code in project_settings["embed"]:
                viz = project_settings["embed"][code]
    else:
        messages.error(request, _("Code invalid"))
        project = False

    return render(request = request,
                template_name='frontend/embed.html',
                context = {"project": project, "code": project_code, "viz": viz, "viz_code": code})


#Upodate the dashboard based on filters
def update_dashboard(request, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        #print(request.POST)
        dash_parameters = {}
        for key, value in request.POST.items():
            if key == "csrfmiddlewaretoken" :
                continue
            else:
                if '[]' in key:
                    key_final = key.replace('[]', '')
                    dash_parameters[key_final] =  request.POST.getlist(key)
                else:
                    dash_parameters[key] = request.POST.get(key)
        #print(dash_parameters)
        data = update_viz(request, dash_parameters, code)
    return JsonResponse(data)

#Delete vis from dashbaord
def drop_visualization(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('drop_code'):
            rep = drop_viz(request, request.POST.get('drop_code'))
            data = {'success': rep['success'], 'div_id': rep['div_id']}
        else:
            data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)

def nb_recommend(request, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': True, 'nb_recommend_graph': 0, 'end_recommend_graph': 0}
    if "nb_recommend_graph" in request.session and "vzcode_recommend_graph" in request.session and request.session["vzcode_recommend_graph"] == code:
        data = {'success': True, 'nb_recommend_graph': request.session["nb_recommend_graph"], 'end_recommend_graph': request.session["end_recommend_graph"]}
    elif "backup_nb_recommend_graph" in request.session and "backup_vzcode_recommend_graph" in request.session and request.session["backup_vzcode_recommend_graph"] == code:
        request.session["recommend_graph"] = copy.deepcopy(request.session["backup_recommend_graph"])
        request.session["nb_recommend_graph"] = request.session["backup_nb_recommend_graph"]
        request.session["end_recommend_graph"] = request.session["backup_end_recommend_graph"]
        request.session["vzcode_recommend_graph"] = request.session["backup_vzcode_recommend_graph"]

    if "nb_recommend_graph" in request.session and "vzcode_recommend_graph" in request.session and request.session["vzcode_recommend_graph"] == code:
        data = {'success': True, 'nb_recommend_graph': request.session["nb_recommend_graph"], 'end_recommend_graph': request.session["end_recommend_graph"]}

    return JsonResponse(data)

def get_recommend(request, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if "recommend_graph" in request.session and code in request.session["recommend_graph"]:
        #print(code)
        #print(request.session["recommend_graph"][code])
        data = generate_graph(request, {}, False, code)
    return JsonResponse(data)

#Show data content
def data_content(request, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    file_code = code
    if file_code and file_code in request.session["list_selectedfiles"]:
        current_project = request.session["current_project"]
        if not current_project:
            return JsonResponse(data)
        result_df = save_read_df(request, file_code, request.session["list_selectedfiles"][file_code]["file_ext"],
        request.session["list_selectedfiles"][file_code]["file_link"], request.session["list_selectedfiles"][file_code]["refresh_timeout"],
        current_project["project_settings"]["files"][file_code]["df_file_code"], 0, request.session["convert_dict"][file_code])
        df = result_df["df"]

        if df is None:
            return JsonResponse(data)

        plot_table = create_table(df, True)
        data = {'success': True, 'plot_table':plot_table, 'title': request.session["list_selectedfiles"][file_code]["title"]}
    else:
        data = {'success': False, 'message': _('Something went wrong')}
    return JsonResponse(data)


#view visualization
def view_visualization(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST' and request.POST.get('code'):
        code = request.POST.get('code')
        data = {'success': False, 'message': _('Something went wrong')}
        list_viz = request.session['list_viz']
        list_viz = [x for x in list_viz if (code == x['code'])]
        if len(list_viz) == 1:
            graph_parameters = list_viz[0]
            data = generate_graph(request, graph_parameters)
            data["info"] = graph_parameters
    return JsonResponse(data)


#Load datasets from open data portal
def load_opdaset(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    request.session["current_portal"] = None
    request.session["current_portal_link"] = None
    request.session["current_platform"] = None
    request.session["current_dataset"] = None
    request.session["search_dataset"] = None
    request.session["all_datasets"] = []
    request.session["start"] = 0
    if request.method == 'POST':
        if request.POST.get('portal') and request.POST.get('dataset'):
            portal = request.POST.get('portal')
            dataset = request.POST.get('dataset')
            request.session["search_dataset"] = dataset
            portal_link = portal
            if "http" not in portal_link and int(portal) > 0 and str(portal) in request.session["list_dataportals"]:
                portal_link = request.session["list_dataportals"][str(portal)]["more_details"]["link"]
                request.session["current_portal"] = str(portal)
                request.session["current_platform"] = request.session["list_dataportals"][str(portal)]["platform"]

            if "http" in portal_link:
                parsed_uri = urlparse(portal_link)
                portal_link = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                request.session["current_portal_link"] = portal_link
                data = search_dataset(request, portal_link, dataset)
        else:
            data = {'success': False, 'message': _('Please fill all fileds')}
    return JsonResponse(data)

#Load more datasets from open data portal
def load_more_opdaset(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('link_next') and "current_portal_link" in request.session and "current_platform" in request.session:
            link = request.POST.get('link_next')
            response = requests.get(link)
            if response and int(response.status_code) == 200:
                myresults = response.json()
                sportal = str(request.session["current_platform"])
                portal_link = request.session["current_portal_link"]
                more_details = request.session["list_platformportals"][sportal]["more_details"]
                explore_link = portal_link + more_details["explore_dt"]
                if sportal == "1": #ODS
                    data = {'success': True, 'data': myresults, 'current_platform': sportal, 'explore_link':explore_link}
                    request.session["all_datasets"] += myresults["datasets"]
                elif sportal == "2": #CKAN
                    if not myresults["success"]:
                        data = {'success': False, 'message': _('Impossible to retrieve data.')}
                    elif "result" in myresults and "count" in myresults["result"] and  myresults["result"]["count"] == 0:
                        data = {'success': False, 'message': _('No datasets match your request.')}
                    elif "result" in myresults and "results" in myresults["result"]:
                        request.session["start"] = request.session["start"] + 1
                        dataset = request.session["search_dataset"]
                        final_results = convert_ckan_to_ods_format(request, portal_link, dataset, sportal, myresults)
                        explore_link = portal_link + more_details["explore_dt"]
                        data = {'success': True, 'data': final_results, 'current_platform': sportal, 'explore_link': explore_link}
                        request.session["all_datasets"] += final_results["datasets"]
    return JsonResponse(data)

#Get dataset from portal
def get_whole_dataset(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'is_valid': False, 'message': _('Unable to retrieve dataset')}
    if request.method == 'POST':
        if request.POST.get('dataset_id') and request.POST.get('dataset_inc') and "current_portal_link" in request.session and "current_platform" in request.session:
            dataset_id = request.POST.get('dataset_id')
            dataset_inc = request.POST.get('dataset_inc')
            data = add_opd(request, dataset_id,dataset_inc)
    return JsonResponse(data)

#get all selected files in project
def get_all_datasets(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('No dataset available'), 'data': []}
    if "list_selectedfiles" in request.session:
        keys = list(request.session["list_selectedfiles"].keys())
        data = {'success': True, 'data': request.session["list_selectedfiles"], 'keys': keys}
    return JsonResponse(data)

#Return columns of specific dataset
def get_dataset_columns(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Unable to retrieve data'), 'data': []}
    if request.method == 'POST':
        if request.POST.get('data_code'):
            file_code = request.POST.get('data_code')
            col_code = request.POST.get('col_code')
            fulldata = {}
            if "agg" in col_code:
                keys = list(request.session["all_agg_dict"][file_code].keys())
                fulldata = request.session["all_agg_dict"][file_code]
            else:
                keys = list(request.session["all_col_dict"][file_code].keys())
                fulldata = request.session["all_col_dict"][file_code]
            data = {'success': True, 'keys': keys, 'fulldata': fulldata}
    return JsonResponse(data)

#Drop Columns from dataset
def dropcol(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('dropcol_dt') and request.POST.get('dropcol_col'):
            data = dropcol_dataset(request)
        else:
            data = {'is_valid': False, 'message': _('Please fill all fileds')}
    return JsonResponse(data)

#Search and replace values in dataset
def repval(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('repval_dt') and request.POST.get('repval_col') and request.POST.get('repval_rep'):
            data = se_rep_dataset(request)
        else:
            data = {'is_valid': False, 'message': _('Please fill all fileds')}
    return JsonResponse(data)

#Combine datasets
def combata(request):
    data = {'is_valid': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('combdata_dt1') and request.POST.get('combdata_col1') and request.POST.get('combdata_rel') and request.POST.get('combdata_dt2') and request.POST.get('combdata_col2') and request.POST.get('combdata_dtname'):
            data = combine_datasets(request)
        else:
            data = {'is_valid': False, 'message': _('Please fill all fileds')}

    return JsonResponse(data)

#Aggregate data
def aggdata(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('aggdata_dt') and request.POST.get('aggdata_col'):
            data = agg_dataset(request)
        else:
            data = {'is_valid': False, 'message': _('Please fill all fileds')}
    return JsonResponse(data)

#Duplicate existent dashboard
def customize_dashboard(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST':
        if request.POST.get('dash_code'):
            code = request.POST.get('dash_code')
            try:
                data = Project.objects.get(dash_code__exact=code)
                if data:
                    new_project = Project()
                    new_project.address_ip = visitor_ip_address(request)
                    new_project.has_vizs = data.has_vizs
                    project_settings = data.project_settings
                    if data.title:
                        new_project.title = data.title+_(" (copy)")
                        #project_settings["dashboard"]["title"] = new_project.title
                    if data.notes:
                        new_project.notes = data.notes
                        #project_settings["dashboard"]["notes"] = new_project.notes
                    if request.user and request.user.id:
                        new_project.user_id = request.user.id

                    new_project.project_settings = project_settings
                    new_project.theme_id = data.theme.pk
                    new_project.project_type = data.project_type
                    if request.user and request.user.id:
                        new_project.contact = request.user.username+"|"+request.user.email
                    else:
                        new_project.contact = "N/A"
                    new_project.link = data.link
                    #Set project status to complete
                    new_project.status_id = 3

                    new_project.save()

                    request.session['project_code'] = new_project.code
                    request.session['dash_code'] = new_project.dash_code

                    if "files" in project_settings:
                    	for keyfile, file in project_settings["files"].items():
                            my_file = UploadFile.objects.get(code__exact=keyfile)
                            my_file.related_projects.add(new_project.pk)

                    for variable in ["current_project", "file_codes", "list_selectedfiles"]:
                        if variable in request.session:
                            del request.session[variable]

                    messages.success(request, _("Dashboard duplicated successfully"))
                    return redirect("frontend:special_visualization", code="dash")
            except:
                messages.error(request, _("Something went wrong"))
                return redirect("frontend:home_proto")
        else:
            messages.error(request, _("Something went wrong"))
            return redirect("frontend:home_proto")
    else:
        messages.error(request, _("Something went wrong"))
        return redirect("frontend:home_proto")

#return edit data form
def edit_dataform(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('edit_file_code'):
            code = request.POST.get('edit_file_code')
            data = info_data_form(request, code)
    return JsonResponse(data)

#save changes for edit data from
def edit_datainfo(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('edit_data_code'):
            code = request.POST.get('edit_data_code')
            data = save_data_info(request, code)
    return JsonResponse(data)

#Explore data
def explore_data(request, project_code, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    current_file = None
    project = None
    final_query = None
    final_url = "/generate-datatable/"
    script = ""
    gauge_quality = ""
    init_columns = {"dropdown_columns":[], "columns": []}
    #Handle comments
    comment = ""
    name = (request.user and request.user.username) or ""
    attach = None
    att = None
    checklike = False

    user_types = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    init_user_type = 'expert'

    issue_types = settings.ISSUE_TYPES

    #impacted records - identifier [if existing], data range, complete dataset..., description, suggestion for correction, etc

    if project_code and code:
        try:
            if project_code.startswith('n'):
                data = None
                dash_code = "none"
            elif project_code.startswith('d'): # for dash code
                data = Project.objects.get(dash_code__exact=project_code)
            else: # for project code
                data = Project.objects.get(code__exact=project_code)

            if data:
                project_code = data.code
                dash_code = data.dash_code
                project = {"id":data.pk, "project_settings":data.project_settings,
                "project_history":data.project_history, "user":(data.user and data.user.username), "title":data.title, "notes":data.notes, "shared":data.shared, "code":data.code, "dash_code":data.dash_code,
                "updated_at": data.updated_at.strftime("%d/%m/%Y"), "published_at": data.published_at.strftime("%d/%m/%Y"), "country": data.country, "state": data.state}
                final_url += data.code+"/"
            else:
                project = None

            list_data = list_files(request, [code], project)
            request.session["explore_file"] = list_data
            current_file = list_data[code]
            checklike = check_like(request, "file", current_file["id"])

            final_url += code+"/"
            if "list_explore_files" not in request.session:
                request.session["list_explore_files"] = {}
            if "list_explore_projects" not in request.session:
                request.session["list_explore_projects"] = {}

            request.session["list_explore_files"][code] = current_file
            request.session["list_explore_projects"][project_code] = project

            if request.method == 'POST':
                if request.POST.get('comment') and request.POST.get('name'):
                    feedback = Feedback()
                    if project:
                        feedback.project_id = project["id"]
                    feedback.file_id = current_file["id"]
                    feedback.comment = cleanhtml(request.POST.get('comment'))
                    if request.POST.get('user_type'):
                        feedback.user_type = request.POST.get('user_type')
                    data_provided = request.POST.get("data_provided")
                    if data_provided:
                        data_provided = True
                    else:
                        data_provided = False

                    if data_provided:
                        feedback.comment = "#Data Provided#\n"+feedback.comment

                    if not request.POST.get('parent_feedback') or request.POST.get('parent_feedback') == "":
                        impacted_records = request.POST.get("impacted_records")
                        if impacted_records:
                            feedback.comment = "#IMPREC#"+impacted_records+"\n"+feedback.comment

                        issue_type = request.POST.get("issue_type")
                        if issue_type:
                            feedback.comment = "#"+issue_type+"#\n"+feedback.comment

                        suggestion = request.POST.get("suggestion")
                        if suggestion:
                            feedback.comment = feedback.comment+ "\n#SUGG#"+suggestion

                    feedback.username = cleanhtml(request.POST.get('name'))
                    feedback.feedback_type = cleanhtml(request.POST.get('feedback_type'))
                    if request.POST.get('parent_feedback') and request.POST.get('parent_feedback') != "":
                        feedback.parent_feedback_id = int(request.POST.get('parent_feedback'))
                    if request.FILES and 'attach' in request.FILES:
                        att = request.FILES['attach']
                    if att:
                        att_extension = os.path.splitext(att.name)[1]
                        att_name = os.path.splitext(att.name)[0]
                        attach = 'feedbacks/'+str(randint(1000, 9999))+"_"+att_name+att_extension
                        path = default_storage.save(attach, ContentFile(att.read()))
                    if attach:
                        feedback.attach = attach
                    try:
                        feedback.save()
                        file = UploadFile.objects.get(pk=current_file["id"])
                        file.has_new_comment = True
                        file.nb_comments = file.nb_comments + 1
                        file.last_comment = feedback.comment
                        if data_provided and file.is_requested:
                            file.data_provided = True
                            file.save(update_fields=['has_new_comment', 'last_comment', 'nb_comments', 'data_provided'])
                        else:
                            file.save(update_fields=['has_new_comment', 'last_comment', 'nb_comments'])

                        messages.success(request, _("Feedback saved successfully"))
                    except Exception as e:
                        print('Error details: '+ str(e))
                        default_storage.delete(attach)
                        messages.error(request, _("Something went wrong"))
                else:
                    messages.error(request, _("Fields * are required"))

            #End Handle comments
            current_file["feedbacks"] = {}

            #feedbacks = Feedback.objects.filter(Q(parent_feedback__isnull=True) & (Q(project__id=project["id"]) & Q(file__id=current_file["id"]))).prefetch_related('feedbacks').order_by('-created_at')
            feedbacks = Feedback.objects.filter(Q(parent_feedback__isnull=True) & Q(file__id=current_file["id"])).prefetch_related('feedbacks').order_by('-created_at')
            if feedbacks:
                for feed in feedbacks:
                    current_file["feedbacks"][feed.pk] = {"id":feed.pk, "reply": feed.pk, "username":feed.username, "comment":feed.comment, "created_at":timeago(feed.created_at),
                    "feedback_type_div": feed.feedback_type, "feedback_type": settings.FEEDBACK_TYPES[feed.feedback_type], "attach": (feed.attach and feed.attach.url) or None,
                    "user_type": _(settings.USER_TYPES[feed.user_type])}
                    current_file["feedbacks"][feed.pk]["subfeedbacks"] = {}
                    for subfeed in feed.feedbacks.all():
                        current_file["feedbacks"][feed.pk]["subfeedbacks"][subfeed.pk] = {"id":subfeed.pk, "reply": feed.pk, "username":subfeed.username, "comment":subfeed.comment, "created_at":timeago(subfeed.created_at),
                        "feedback_type_div": feed.feedback_type, "feedback_type": settings.FEEDBACK_TYPES[feed.feedback_type], "attach": (subfeed.attach and subfeed.attach.url) or None,
                        "user_type": _(settings.USER_TYPES[subfeed.user_type])}

            feedback_types = [
                #('general', _('General Comment')),
                ('data', _('Report Data Issue'))
            ]
            feedback_filter_types = [
                #('general', _('General')),
                ('data', _('Data Issue'))
            ]
            if current_file["is_requested"]:
                feedback_types = [
                    ('general', _('General Comment'))
                ]
                feedback_filter_types = [
                    ('general', _('General'))
                ]

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
            #data = get_info_data(request, project_code, code)

        except Exception as e:
            print('Error details: '+ str(e))
            messages.error(request, _("Unable to retrieve data"))
            return redirect("frontend:home_page")

    return render(request = request,
                  template_name = "frontend/explore_data.html",
                  context={"checklike": checklike, "project":project, "current_file":current_file, "dash_code": dash_code,
                  "final_url": final_url, "final_query": final_query, "script": script, "project_code":project_code,
                  "file_code": code, "dropdown_columns": init_columns["dropdown_columns"],
                  "gauge_quality": gauge_quality, "comment": comment, "name": name, "feedback_types": feedback_types, "feedback_filter_types": feedback_filter_types,
                  "user_types": user_types, "init_user_type": init_user_type, "issue_types": issue_types})

#Generate datatable
def generate_datatable(request, project_code, file_code, query):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'GET':
        data = create_datatable(request, project_code, file_code, query)
        if "fail" not in data:
            return JsonResponse(data)
    return JsonResponse({'status': _('Something went wrong')}, status=404)

#Explore column dataset
def explore_column(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'success': False, 'message': _('Something went wrong')}
    if request.method == 'POST':
        if request.POST.get('col'):
            project_code = request.POST.get('project_code')
            file_code = request.POST.get('file_code')
            final_query = request.POST.get('final_query')
            col = request.POST.get('col')
            data = generate_explore_column(request, project_code, file_code, final_query, col)
    return JsonResponse(data)

#List all projects based on search option
def projects(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    load_data(request, Theme, "list_themes", 0)
    get_project_statuses(request)
    search = request.GET.get('search', "")
    topic = request.GET.get('topic', "")
    type = request.GET.get('type', "")
    sort = request.GET.get('sort', "")
    status = request.GET.get('status', "")
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")

    if status:
        status = int(status)
    if type and status and type == 'external' and status not in request.session["statuses_fep"]:
        status = ""
    if type and status and type == 'proposed' and status not in request.session["statuses_fsp"]:
        status = ""
    if type and type == 'external' and sort == "nblikes":
        sort = "modified"
    if type and type == 'proposed' and (sort == "" or sort == "nbfavorites"):
        sort = "nblikes"

    filter = Q(shared__exact=True)

    country = request.GET.get('country', "")
    state = request.GET.get('state', "")
    if "countries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["countries"] = countries
    if "used_countries" not in request.session:
        get_countries(request)

    order_by = ["-updated_at"]
    #order_by = *order_by
    if sort == "nblikes":
        order_by = ['-nb_likes', '-published_at']
    elif sort == "nbfavorites":
        order_by = ['-nb_favorites', '-published_at']
    elif sort == "modified":
        order_by = ["-published_at"]
    elif sort == "nameasc":
        order_by = ["title"]
    elif sort == "namedesc":
        order_by = ["-title"]

    if(topic != ""):
        topic = topic.lower()
        filter = filter & (Q(theme__name__icontains=topic))
    if(search != ""):
        search = search.lower()
        filter = filter & (Q(title__icontains=search) | Q(notes__icontains=search) | Q(dash_code__exact=search) | Q(code__exact=search))
    if(type != ""):
        type = type.lower()
        if type == 'proposed':
            filter = filter & (Q(project_type__exact=type))
        else:
            filter = filter & (Q(project_type__exact='external') | (Q(project_type__exact='internal') & Q(shared__exact=True)))
    if(country != ""):
        filter = filter & (Q(country__exact=country))
    if(state != ""):
        filter = filter & (Q(state__icontains=state.lower()))
    if(status != ""):
        filter = filter & (Q(status__id=status))
    if(datefrom != ""):
        filter = filter & (Q(published_at__gte=datefrom+ " 00:00:00"))
    if(dateto != ""):
        filter = filter & (Q(published_at__lte=dateto+ " 23:59:59"))

    projects = Project.objects.select_related('theme', 'status').filter(filter).order_by(*order_by)
    nbprojects = len(projects)

    page = request.GET.get('page', 1)
    paginator = Paginator(projects, settings.MAX_PROJECTS_PAGE)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    num_pages = paginator.num_pages
    page_no = int(page)

    if num_pages <= 11 or page_no <= 6:  # case 1 and 2
        pages = [x for x in range(1, min(num_pages + 1, 12))]
    elif page_no > num_pages - 6:  # case 4
        pages = [x for x in range(num_pages - 10, num_pages + 1)]
    else:  # case 3
        pages = [x for x in range(page_no - 5, page_no + 6)]

    return render(request = request,
                  template_name = "frontend/projects.html",
                  context={"status": status, "search": search, "type": type, "sort": sort, "country": country, "state": state,
                  "projects": projects, "topic": request.GET.get('topic', ""), "nbprojects": nbprojects,
                  "datefrom": datefrom, "dateto": dateto, "pages": pages})

#Detail project
def detail_project(request, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    try:
        data = Project.objects.select_related('theme', 'status').get(dash_code__exact=code)
    except:
        data = None

    #Handle comments
    comment = ""
    name = (request.user and request.user.username) or ""
    attach = None
    att = None
    checklike = False
    checkfavorite = False
    get_project_statuses(request)

    if request.method == 'POST' and data:
        if request.POST.get('sdpemail') and request.POST.get('sdpid'):
            email = cleanhtml(request.POST.get('sdpemail'))

            try:
                subscribe, created = SubscribeDataProject.objects.get_or_create(project_id=int(data.pk), email=email, defaults={'project_id': int(data.pk), 'email': email})
                messages.success(request, _("Subscription saved successfully"))
            except Exception as e:
                print('Error details: '+ str(e))
                messages.error(request, _("Something went wrong"))

        elif request.POST.get('comment') and request.POST.get('name'):
            feedback = Feedback()
            feedback.project_id = data.pk
            feedback.comment = cleanhtml(request.POST.get('comment'))
            feedback.username = cleanhtml(request.POST.get('name'))
            feedback.feedback_type = cleanhtml(request.POST.get('feedback_type'))
            if request.POST.get('user_type'):
                feedback.user_type = request.POST.get('user_type')
            if request.POST.get('fdstatus'):
                sts= request.POST.get('fdstatus').split("_")
                feedback.comment = "#"+cleanhtml(sts[0])+"# " +feedback.comment
                if data.project_type == "proposed":
                    data.status_id = int(sts[1])
            if request.POST.get('rate') and int(request.POST.get('rate'))>0:
                feedback.comment = "#"+str(request.POST.get('rate'))+"#" +feedback.comment

            if request.POST.get('parent_feedback') and request.POST.get('parent_feedback') != "":
                feedback.parent_feedback_id = int(request.POST.get('parent_feedback'))
            if request.FILES and 'attach' in request.FILES:
                att = request.FILES['attach']
            if att:
                att_extension = os.path.splitext(att.name)[1]
                att_name = os.path.splitext(att.name)[0]
                attach = 'feedbacks/'+str(randint(1000, 9999))+"_"+att_name+att_extension
                path = default_storage.save(attach, ContentFile(att.read()))
            if attach:
                feedback.attach = attach
            try:
                feedback.save()
                data.has_new_comment = True
                data.nb_comments = data.nb_comments + 1

                if feedback.feedback_type != 'general':
                    data.last_comment = feedback.comment
                    if request.POST.get('fdstatus') and data.project_type == "proposed":
                        data.save(update_fields=['has_new_comment', 'last_comment', 'nb_comments', 'status'])
                    else:
                        data.save(update_fields=['has_new_comment', 'last_comment', 'nb_comments'])
                else:
                    data.last_general_comment = feedback.comment
                    data.save(update_fields=['has_new_comment', 'last_general_comment', 'nb_comments'])

                messages.success(request, _("Feedback saved successfully"))
            except Exception as e:
                print('Error details: '+ str(e))
                default_storage.delete(attach)
                messages.error(request, _("Something went wrong"))
        else:
            messages.error(request, _("Fields * are required"))
    #End Handle comments

    if data:
        code = data.code
        project = {"id":data.pk, "project_settings":data.project_settings,
        "project_history":data.project_history, "user":(data.user and data.user.username), "title":data.title, "notes":data.notes, "shared":data.shared, "code":data.code, "dash_code":data.dash_code,
        "updated_at": data.updated_at.strftime('%d/%m/%Y'), "published_at": data.published_at.strftime('%d/%m/%Y'), "project_type": data.project_type, "contact": data.contact, "image": (data.image and data.image.url) or None, "static_image": data.static_image,
        "theme": str(data.theme.name), "link": data.link, "country": data.country, "state": data.state, "nb_likes": data.nb_likes, "user_request_type": data.user_request_type,
        "status": data.status.id, "status_name": data.status.name, "data_status": data.status, "nb_favorites": data.nb_favorites, "list_datasets": data.list_datasets}

        project["feedbacks"]={}
        project["feedbacks_req"]={}
        project["feedbacks_sta"]={}
        checklike = check_like(request, "project", project["id"], "like")
        checkfavorite = check_like(request, "project", project["id"], "favorite")


        project_settings = data.project_settings
        if "files" in project_settings:
            file_codes = []
            for keyfile, file in project_settings["files"].items():
                file_codes.append(keyfile)
            list_data = list_files(request, file_codes, project)
            project["list_files"] = list_data

        feedbacks = Feedback.objects.filter(Q(project__id=data.pk) & (Q(parent_feedback__isnull=True) & Q(file__isnull=True))).prefetch_related('feedbacks').order_by('-created_at')
        if feedbacks:
            for feed in feedbacks:
                varfeedname = "feedbacks"
                if feed.feedback_type == "status":
                    varfeedname = "feedbacks_sta"
                elif feed.feedback_type == "requirement":
                    varfeedname = "feedbacks_req"
                project[varfeedname][feed.pk] = {"id":feed.pk, "reply": feed.pk, "username":feed.username, "comment":feed.comment, "created_at":timeago(feed.created_at),
                "feedback_type_div": feed.feedback_type,"feedback_type": settings.FEEDBACK_TYPES[feed.feedback_type], "attach": (feed.attach and feed.attach.url) or None,
                "user_type": _(settings.USER_TYPES[feed.user_type])}
                project[varfeedname][feed.pk]["subfeedbacks"] = {}
                for subfeed in feed.feedbacks.all():
                    project[varfeedname][feed.pk]["subfeedbacks"][subfeed.pk] = {"id":subfeed.pk, "reply": feed.pk, "username":subfeed.username, "comment":subfeed.comment, "created_at":timeago(subfeed.created_at),
                    "feedback_type_div": feed.feedback_type, "feedback_type": settings.FEEDBACK_TYPES[feed.feedback_type], "attach": (subfeed.attach and subfeed.attach.url) or None,
                    "user_type": _(settings.USER_TYPES[subfeed.user_type])}
    else:
        messages.error(request, _("Code invalid"))
        return redirect("frontend:home_page")

        PROJECT_TYPES = [
            #('internal', _('Internal')),
            ('external', _('External')),
            ('proposed', _('Proposed'))
        ]
    """feedback_types = [
        ('general', _('General Comment'))
    ]
    feedback_filter_types = [
        ('general', _('General')),
    ]"""
    user_types = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    #if data.project_type and data.project_type == "proposed":
    feedback_types = [
        ('general', _('General Comment')),
        ('status', _('Update Project Status')),
        ('requirement', _('Requirement Clarification'))
        #('data', _('Data Issue'))
    ]
    feedback_filter_types = [
        ('general', _('General')),
        ('status', _('Project Status')),
        ('requirement', _('Requirement Clarification'))
        #('data', _('Data Issue'))
    ]

    return render(request = request,
                  template_name = "frontend/detail_project.html",
                  context={"checklike": checklike, "project": project, "comment": comment, "name": name, "feedback_types": feedback_types, "feedback_filter_types": feedback_filter_types,
                  "user_types": user_types, "checkfavorite": checkfavorite})

#Get all states based oon country
def get_states(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'states': [], "success": False}
    if request.method == 'POST':
        data = get_states_by_country(request, request.POST.get('sch_country') or None)
    return JsonResponse(data)

#Get all states based oon country
def get_transstates(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {'states': [], "success": False}
    if request.method == 'POST':
        data = get_states_by_transcountry(request, request.POST.get('sch_country') or None)
    return JsonResponse(data)

#Save when user clicks on like button on file or project
def save_like(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    data = {"success": False}
    if request.method == 'POST':
        like_type = request.POST.get('like_type')
        obj_id = request.POST.get('obj_id')
        action_type = request.POST.get('action_type')

        result = check_like(request, like_type, obj_id, action_type, True)
        if not result:
            like = Like()
            like.action_type = action_type
            if like_type == "project":
                like.project_id = int(obj_id)
                obj = Project.objects.get(pk=obj_id)
            elif like_type == "file":
                like.file_id = int(obj_id)
                obj = UploadFile.objects.get(pk=obj_id)
            if request.user and request.user.id:
                like.user_id = request.user.id
            like.address_ip = visitor_ip_address(request)
            like.save()
            if action_type == "like":
                obj.nb_likes = obj.nb_likes + 1
                obj.save(update_fields=['nb_likes'])
            else:
                obj.nb_favorites = obj.nb_favorites + 1
                obj.save(update_fields=['nb_favorites'])
            data = {"success": True}
        elif result and action_type != "like":
            result.delete()
            obj = Project.objects.get(pk=obj_id)
            obj.nb_favorites = obj.nb_favorites - 1
            obj.save(update_fields=['nb_favorites'])
            data = {"success": False}

    return JsonResponse(data)

#Aurocomplete title project or file
def autocomplete_title(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    if request.method == 'POST' and request.POST.get('auto_type') == "project":
        data = autocomplete_project(request)
    else:
        data = autocomplete_dataset(request)
    #print(data)
    return JsonResponse(data)

#List all datasets based on search option
def datasets(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    search = request.GET.get('search', "")
    type = request.GET.get('type', "")
    sort = request.GET.get('sort', "")
    provided = request.GET.get('provided', "")
    country = request.GET.get('country', "")
    state = request.GET.get('state', "")
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")


    filter = Q(is_demo__exact=False) & Q(active__exact=True) & Q(related_projects__isnull=False) & Q(related_projects__shared__exact=True)

    if "countries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["countries"] = countries
    if "used_countries" not in request.session:
        get_countries(request)

    if type and type == 'available' and sort == "nblikes":
        sort = "created"
    if type and type == 'requested' and sort == "":
        sort = "nblikes"

    order_by = ["-created_at"]
    if sort == "nblikes":
        order_by = ['-nb_likes', '-created_at']
    elif sort == "created":
        order_by = ["-created_at"]

    if search != "":
    	lsearch = search.lower()
    	filter = filter & (Q(more_details__title__icontains=lsearch) | Q(more_details__description__icontains=lsearch) | Q(more_details__contact__icontains=lsearch))
    if country != "":
    	lcountry = country.lower()
    	filter = filter & Q(related_projects__country__icontains=lcountry)
    if state != "":
    	lstate = state.lower()
    	filter = filter & Q(related_projects__state__icontains=lstate)
    if type != "" and type == 'available':
        filter = filter & Q(is_requested__exact=False)
    if type != "" and type == 'requested':
        filter = filter & Q(is_requested__exact=True)
        if provided != "" and provided == "yes":
            filter = filter & Q(data_provided__exact=True)
        if provided != "" and provided == "no":
            filter = filter & Q(data_provided__exact=False)
    if(datefrom != ""):
        filter = filter & (Q(created_at__gte=datefrom+ " 00:00:00"))
    if(dateto != ""):
        filter = filter & (Q(created_at__lte=dateto+ " 23:59:59"))

    #.exclude(related_projects=None)
    datasets = UploadFile.objects.prefetch_related('related_projects').filter(filter).order_by(*order_by)
    print("datasets Query====================================================================")
    print(datasets.query)
    print("datasets Query====================================================================")
    nbdatasets = len(datasets)

    page = request.GET.get('page', 1)
    paginator = Paginator(datasets, settings.MAX_DATA_PAGE)
    try:
        datasets = paginator.page(page)
    except PageNotAnInteger:
        datasets = paginator.page(1)
    except EmptyPage:
        datasets = paginator.page(paginator.num_pages)

    num_pages = paginator.num_pages
    page_no = int(page)

    if num_pages <= 11 or page_no <= 6:  # case 1 and 2
        pages = [x for x in range(1, min(num_pages + 1, 12))]
    elif page_no > num_pages - 6:  # case 4
        pages = [x for x in range(num_pages - 10, num_pages + 1)]
    else:  # case 3
        pages = [x for x in range(page_no - 5, page_no + 6)]

    return render(request = request,
                  template_name = "frontend/datasets.html",
                  context={"provided": provided, "search": search, "type": type, "sort": sort, "country": country, "state": state, "datasets": datasets, "nbdatasets": nbdatasets
                  ,"datefrom": datefrom, "dateto": dateto, "pages": pages})

#List all data issues based on search option
def issues(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    search = request.GET.get('search', "")
    country = request.GET.get('country', "")
    state = request.GET.get('state', "")
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")

    filter = Q(feedback_type__exact="data") & Q(parent_feedback__isnull=True) & Q(project__isnull=False)

    if "countries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["countries"] = countries
    if "used_countries" not in request.session:
        get_countries(request)

    if search != "":
        lsearch = search.lower()
        filter = filter & (Q(comment__icontains=lsearch) | Q(username__icontains=lsearch) | Q(file__more_details__title__icontains=lsearch) | Q(file__more_details__description__icontains=lsearch))

    if country != "":
        lcountry = country.lower()
        filter = filter & (Q(project__country__icontains=lcountry))

    if state != "":
        lstate = state.lower()
        filter = filter & (Q(project__state__icontains=lstate))

    if(datefrom != ""):
        filter = filter & (Q(created_at__gte=datefrom+ " 00:00:00"))
    if(dateto != ""):
        filter = filter & (Q(created_at__lte=dateto+ " 23:59:59"))

    order_by = "-created_at"
    issues = Feedback.objects.select_related('project', 'file').filter(filter).order_by(order_by)
    nbissues = len(issues)

    page = request.GET.get('page', 1)
    paginator = Paginator(issues, settings.MAX_DATA_PAGE)
    try:
        issues = paginator.page(page)
    except PageNotAnInteger:
        issues = paginator.page(1)
    except EmptyPage:
        issues = paginator.page(paginator.num_pages)

    num_pages = paginator.num_pages
    page_no = int(page)

    if num_pages <= 11 or page_no <= 6:  # case 1 and 2
        pages = [x for x in range(1, min(num_pages + 1, 12))]
    elif page_no > num_pages - 6:  # case 4
        pages = [x for x in range(num_pages - 10, num_pages + 1)]
    else:  # case 3
        pages = [x for x in range(page_no - 5, page_no + 6)]

    return render(request = request,
                  template_name = "frontend/issues.html",
                  context={"pages": pages,"search": search, "country": country, "state": state, "issues": issues, "nbissues": nbissues, "datefrom": datefrom, "dateto": dateto})

def summary(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']
    host = settings.DATABASES['default']['HOST']
    port = settings.DATABASES['default']['PORT']
    country = request.GET.get('country', "")
    state = request.GET.get('state', "")
    datefrom = request.GET.get('datefrom', "")
    dateto = request.GET.get('dateto', "")

    tot_proj = 0
    tot_issues = 0
    tot_data_requested = 0
    tot_proj_suggested = 0
    cursor = connection.cursor()
    cond_proj = " AND 1 = 1 "

    if country != "":
        lcountry = country.lower()
        cond_proj = cond_proj + " AND LOWER(vp.country) = '"+lcountry+"'"

    if state != "":
        lstate = state.lower()
        cond_proj = cond_proj + " AND LOWER(vp.state) = '"+lstate+"'"

    cond_file = cond_proj
    cond_iss = cond_proj

    if(datefrom != ""):
        cond_proj = cond_proj + " AND vp.published_at >= '"+datefrom+ " 00:00:00'"
        cond_file = cond_file + " AND vu.created_at >= '"+datefrom+ " 00:00:00'"
        cond_iss = cond_iss + " AND vf.created_at >= '"+datefrom+ " 00:00:00'"
    if(dateto != ""):
        cond_proj = cond_proj + " AND vp.published_at <= '"+dateto+ " 23:59:59'"
        cond_file = cond_file + " AND vu.created_at <= '"+dateto+ " 23:59:59'"
        cond_iss = cond_iss + " AND vf.created_at <= '"+dateto+ " 23:59:59'"

    sql_theme_projects = """
        select *,
        (select count(vp.id) from visualizations_project as vp
         where vp.theme_id = vt.id and vp.shared=True %s) as tot_proj,
         (select count(vp.id) from visualizations_project as vp
         where vp.theme_id = vt.id and vp.shared=True and vp.project_type='proposed' %s) as tot_proj_suggested,
         (select count(vp.id) from visualizations_project as vp
         where vp.theme_id = vt.id and vp.shared=True and vp.project_type='external' %s) as tot_proj_existing
        from visualizations_theme as vt
    """ % (cond_proj, cond_proj, cond_proj)

    sql_stat_projects = """
        select *,
        (select count(vp.id) from visualizations_project as vp
         where vp.status_id = vps.id and vp.shared=True %s) as tot_proj,
         (select count(vp.id) from visualizations_project as vp
         where vp.status_id = vps.id and vp.shared=True and vp.project_type='proposed' %s) as tot_proj_suggested,
         (select count(vp.id) from visualizations_project as vp
         where vp.status_id = vps.id and vp.shared=True and vp.project_type='external' %s) as tot_proj_existing
        from visualizations_projectstatus as vps
    """ % (cond_proj, cond_proj, cond_proj)

    sql_dt_requested = """
        select *,
        (SELECT count(distinct(vu.id)) FROM visualizations_uploadfile as vu
        INNER JOIN visualizations_uploadfile_related_projects vurp ON (vu.id = vurp.uploadfile_id)
        INNER JOIN visualizations_project vp ON (vp.id = vurp.project_id)
        WHERE (vu.is_demo = False AND vu.active = True AND vurp.project_id IS NOT NULL AND vp.theme_id = vt.id and vp.shared=True
        and vu.is_requested=True %s)) as tot_data_requested
        from visualizations_theme as vt
    """ % cond_file

    sql_issues = """
        select count(vf.id) as tot_issues
        from visualizations_feedback as vf
        INNER JOIN visualizations_project vp ON (vp.id = vf.project_id)
        WHERE vf.parent_feedback_id is NULL AND feedback_type='data' %s
    """ % cond_iss

    database_uri  = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}'.format(
        user=user,
        password=password,
        database_name=database_name,
        host=host,
        port=port,
    )
    engine = sqlalchemy.create_engine(database_uri, echo=False)
    df_theme_proj = pd.read_sql(sqlalchemy.text(sql_theme_projects), con=engine)

    tot_proj = df_theme_proj['tot_proj'].sum()
    tot_proj_suggested = df_theme_proj['tot_proj_suggested'].sum()

    df_stat_proj = pd.read_sql(sqlalchemy.text(sql_stat_projects), con=engine)

    df_dt_requested = pd.read_sql(sqlalchemy.text(sql_dt_requested), con=engine)
    tot_data_requested = df_dt_requested['tot_data_requested'].sum()

    df_issues = pd.read_sql(sqlalchemy.text(sql_issues), con=engine)
    tot_issues = df_issues['tot_issues'].sum()

    varx = "name_"+settings.MODELTRANSLATION_DEFAULT_LANGUAGE

    if LANGUAGE_SESSION_KEY in request.session:
        varx = "name_"+request.session[LANGUAGE_SESSION_KEY]

    layout = go.Layout(
        template='plotly_white'
    )
    fig_theme_proj = go.Figure(data=[
        go.Bar(name=_("Total Projects"), x=df_theme_proj[varx], y=df_theme_proj["tot_proj"]),
        go.Bar(name=_("Total Suggested Projects"), x=df_theme_proj[varx], y=df_theme_proj["tot_proj_suggested"])
    ], layout=layout)
    fig_theme_proj.update_layout(barmode='group')
    fig_theme_proj.update_layout(margin=dict(
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
            font=dict(size=13)
        ), font=dict(size=11)
    )
    plot_theme_proj = plot(fig_theme_proj, output_type='div', include_plotlyjs=False)


    fig_stat_proj = go.Figure(data=[
        go.Bar(name=_("Total Projects"), x=df_stat_proj[varx], y=df_stat_proj["tot_proj"]),
        go.Bar(name=_("Total Suggested Projects"), x=df_stat_proj[varx], y=df_stat_proj["tot_proj_suggested"])
    ], layout=layout)
    fig_stat_proj.update_layout(barmode='group')
    fig_stat_proj.update_layout(margin=dict(
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
            font=dict(size=13)
        ), font=dict(size=11)
    )
    plot_stat_proj = plot(fig_stat_proj, output_type='div', include_plotlyjs=False)

    df_dt_requested = df_dt_requested[df_dt_requested.tot_data_requested != 0]
    if df_dt_requested.shape[0] > 0:

        fig_dt_req = go.Figure(data=[go.Pie(labels=df_dt_requested[varx], values=df_dt_requested["tot_data_requested"])])
        fig_dt_req.update_layout(margin=dict(
                l=0,
                r=10,
                b=5,
                t=15,
                pad=4
            ),legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="left",
                x=0,
                tracegroupgap=5,
                font=dict(size=13)
            ), font=dict(size=11)
        )
        fig_dt_req.update_traces(textinfo='value+percent', textfont_size=15)
        plot_dt_req = plot(fig_dt_req, output_type='div', include_plotlyjs=False)
    else:
        plot_dt_req = '<p class="sm-marg red-text center">'+_("There is no requested data.")+'</p>'

    return render(request = request,
                  template_name = "frontend/summary.html",
                  context={"country": country, "state": state, "datefrom": datefrom, "dateto": dateto,
                  "tot_proj": tot_proj, "tot_issues": tot_issues, "tot_data_requested": tot_data_requested,
                  "tot_proj_suggested": tot_proj_suggested, "plot_theme_proj":plot_theme_proj, "plot_stat_proj": plot_stat_proj,
                  "plot_dt_req": plot_dt_req})

#All functions for mobile app
#Mobile Home page
def home_mobile(request):
    active_lang = (LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    themes_popular = Theme.objects.filter(Q(is_popular__exact=True) & Q(active__exact=True)).order_by('sequence_mobile', 'name')[:settings.LIMIT_HOME_MOBILE_THEMES:1]

    now = datetime.datetime.now()
    now_str = now.strftime("%d/%m/%y")

    reload = False
    if "reload_time" not in request.session:
        reload = True
    else:
        prev = request.session["reload_time"]
        prev = datetime.datetime.strptime(prev, "%d/%m/%y")
        diff = (now-prev).days
        if diff >= settings.RELOAD_TIMEOUT:
            reload = True

    if reload:
        load_data(request, Theme, "list_themes_mobile", 1)
        get_countries(request)
        request.session["reload_time"] = now_str
    else:
        load_data(request, Theme, "list_themes_mobile", 0)
        #get_countries(request)
        if "used_countries" not in request.session:
            get_countries(request)

    #filter = Q(shared__exact=True) & Q(show_in_mobile_apps__exact=True)
    #Detect location of user
    home_country = request.GET.get('home_country', "")
    if home_country == "" or home_country is None:
        if ("country" in request.session and request.session["country"]):
            home_country = request.session["country"]

        if home_country not in request.session["used_countries"]:
            address_ip = visitor_ip_address(request)
            ip_data = get_ip_details(address_ip)
            detected_country = ip_data.country_name or request.ipinfo.country_name
            home_country = detected_country
            if home_country not in request.session["used_countries"]:
                home_country = settings.DEFAULT_COUNTRY
                messages.success(request, translate_value(settings.DEFAULT_COUNTRY, active_lang)+ _(" was used by default because there are no recorded OGD reuses for ")+" "+translate_value(detected_country, active_lang))

    request.session["country"] = home_country

    filter_pop = (Q(project_type__exact='external') | (Q(project_type__exact='internal') & Q(shared__exact=True))) & (Q(shared__exact=True) & Q(country__exact=home_country)) & (Q(is_popular__exact=True))
    order_pop = ['-is_popular', '-nb_favorites', 'title']
    filter_new = (Q(project_type__exact='external') | (Q(project_type__exact='internal') & Q(shared__exact=True))) & (Q(shared__exact=True) & Q(country__exact=home_country))
    order_new = ['-published_at', 'title']

    if settings.CHECK_SHOW_IN_APPS:
        filter_pop = filter_pop & Q(show_in_mobile_apps__exact=True)
        filter_new = filter_pop & Q(show_in_mobile_apps__exact=True)

    projects_popular = Project.objects.select_related('theme', 'status').filter(filter_pop).order_by(*order_pop)[:settings.LIMIT_HOME_MOBILE_POP:1]
    projects_new = Project.objects.select_related('theme', 'status').filter(filter_new).order_by(*order_new)[:settings.LIMIT_HOME_MOBILE_NEW:1]
    is_mobile = mobile(request)

    return render(request = request,
                  template_name = "frontend/home_mobile.html",
                  context={"country": home_country, "home_country": home_country, "themes_popular": themes_popular, "projects_popular": projects_popular, "projects_new": projects_new, "is_mobile": is_mobile})

#Mobile Favorites page
def favorites_mobile(request):
    country = ("country" in request.session and request.session["country"]) or settings.DEFAULT_COUNTRY
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    if request.user and request.user.id:
        favids = get_favorites(request)
        filter = (Q(project_type__exact='external') | (Q(project_type__exact='internal') & Q(shared__exact=True))) & (Q(pk__in=favids))
        order_by = ['-nb_favorites', '-is_popular', 'title']
        if settings.CHECK_SHOW_IN_APPS:
            filter = filter & Q(show_in_mobile_apps__exact=True)
        favorites = Project.objects.select_related('theme', 'status').filter(filter).order_by(*order_by)[:settings.LIMIT_HOME_MOBILE_POP:1]
        is_mobile = mobile(request)
        nbfavorites = len(favorites)

        return render(request = request,
                      template_name = "frontend/favorites_mobile.html",
                      context={"favorites": favorites,  "is_mobile": is_mobile, "nbfavorites": nbfavorites, "country":country})
    else:
        response = redirect("frontend:login_mobile")
        response['Location'] += '?next=/favorites-mobile'
        return response

#Mobile Topics page
def topics_mobile(request):
    country = ("country" in request.session and request.session["country"]) or settings.DEFAULT_COUNTRY
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    load_data(request, Theme, "list_themes_mobile", 0)
    return render(request = request,
                  template_name = "frontend/topics_mobile.html",
                  context={"country": country})


#register new account mobile
def register_mobile(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    country = ("country" in request.session and request.session["country"]) or settings.DEFAULT_COUNTRY
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _("New account created:")+" "+username)
            login(request, user)
            return redirect("frontend:home_mobile")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            password1 = form.data['password1']
            password2 = form.data['password2']
            email = form.data['email']
            for msg in form.errors.as_data():
                if msg == 'email':
                    messages.error(request, f"Declared {email} is not valid")
                if msg == 'password2' and password1 == password2:
                    messages.error(request, f"Selected password: {password1} is not strong enough")
                elif msg == 'password2' and password1 != password2:
                    messages.error(request, f"Password: '{password1}' and Confirmation Password: '{password2}' do not match")
    else:
        form = NewUserForm()

    is_mobile = mobile(request)

    return render(request = request,
                  template_name = "frontend/register_mobile.html",
                  context={"form":form, "is_mobile": is_mobile, "country": country})

#login mobile
def login_mobile(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    country = ("country" in request.session and request.session["country"]) or settings.DEFAULT_COUNTRY
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                request.session["current_user_type"] = user.user_type
                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                return redirect("frontend:home_mobile")
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            messages.error(request, _("Invalid username or password."))
    else:
        form = AuthenticationForm()

    is_mobile = mobile(request)

    return render(request = request,
                      template_name = "frontend/login_mobile.html",
                      context={"form":form, "is_mobile": is_mobile, "country": country})

#logout mobile
def logout_mobile(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    current_lang = settings.MOBILE_APP_LANG
    if request.method == 'POST':
        messages.info(request, _("Logged out successfully!"))
        logout(request)
        request.session["current_user_type"] = settings.NON_EXPERT
        request.session[LANGUAGE_SESSION_KEY] = current_lang
        return redirect("frontend:home_mobile")

#Mobile Projects page
def projects_mobile(request):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    load_data(request, Theme, "list_themes_mobile", 0)
    search = request.GET.get('search', "")
    topic = request.GET.get('topic', "")
    sort = request.GET.get('sort', "modified")

    #filter = Q(shared__exact=True) & Q(show_in_mobile_apps__exact=True)
    filter = Q(shared__exact=True)
    if settings.CHECK_SHOW_IN_APPS:
        filter = filter & Q(show_in_mobile_apps__exact=True)

    country = request.GET.get('country', "")
    if country == "":
        country = settings.DEFAULT_COUNTRY

    state = request.GET.get('state', "")

    if "used_countries" not in request.session:
        get_countries(request)

    order_by = ['-is_popular', '-nb_favorites', 'title']

    #order_by = *order_by
    if sort == "new":
        order_by = ['-published_at', 'title']
    elif sort == "popular":
        order_by = ['-is_popular', '-nb_favorites', 'title']

    if(topic != ""):
        topic = topic.lower()
        filter = filter & (Q(theme__name__icontains=topic))
    if(search != ""):
        search = search.lower()
        filter = filter & (Q(title__icontains=search) | Q(notes__icontains=search) | Q(dash_code__exact=search) | Q(code__exact=search))

    filter = filter & (Q(project_type__exact='external') | (Q(project_type__exact='internal') & Q(shared__exact=True)))

    if(country != ""):
        filter = filter & (Q(country__exact=country))
    if(state != ""):
        filter = filter & (Q(state__icontains=state.lower()))

    projects = Project.objects.select_related('theme', 'status').filter(filter).order_by(*order_by)
    nbprojects = len(projects)

    page = request.GET.get('page', 1)
    paginator = Paginator(projects, settings.MAX_PROJECTS_PAGE)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    num_pages = paginator.num_pages
    page_no = int(page)

    if num_pages <= 11 or page_no <= 6:  # case 1 and 2
        pages = [x for x in range(1, min(num_pages + 1, 12))]
    elif page_no > num_pages - 6:  # case 4
        pages = [x for x in range(num_pages - 10, num_pages + 1)]
    else:  # case 3
        pages = [x for x in range(page_no - 5, page_no + 6)]

    is_mobile = mobile(request)

    return render(request = request,
                  template_name = "frontend/projects_mobile.html",
                  context={"pages": pages,"search": search, "sort": sort, "country": country, "state": state,
                  "projects": projects, "topic": request.GET.get('topic', ""), "nbprojects": nbprojects, "is_mobile": is_mobile})

#Mobile Detail project
def detail_project_mobile(request, code):
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    country = ("country" in request.session and request.session["country"]) or settings.DEFAULT_COUNTRY
    try:
        data = Project.objects.select_related('theme', 'status').get(dash_code__exact=code)
    except:
        data = None

    #Handle comments
    comment = ""
    name = (request.user and request.user.username) or ""
    attach = None
    att = None
    checklike = False
    checkfavorite = False
    get_project_statuses(request)

    if request.method == 'POST' and data:
        if request.POST.get('sdpemail') and request.POST.get('sdpid'):
            email = cleanhtml(request.POST.get('sdpemail'))

            try:
                subscribe, created = SubscribeDataProject.objects.get_or_create(project_id=int(data.pk), email=email, defaults={'project_id': int(data.pk), 'email': email})
                messages.success(request, _("Subscription saved successfully"))
            except Exception as e:
                print('Error details: '+ str(e))
                messages.error(request, _("Something went wrong"))

        elif request.POST.get('comment') and request.POST.get('name'):
            feedback = Feedback()
            feedback.project_id = data.pk
            feedback.comment = cleanhtml(request.POST.get('comment'))
            feedback.username = cleanhtml(request.POST.get('name'))
            feedback.feedback_type = cleanhtml(request.POST.get('feedback_type'))
            if request.POST.get('user_type'):
                feedback.user_type = request.POST.get('user_type')
            if request.POST.get('fdstatus'):
                sts= request.POST.get('fdstatus').split("_")
                feedback.comment = "#"+cleanhtml(sts[0])+"# " +feedback.comment
                if data.project_type == "proposed":
                    data.status_id = int(sts[1])
            if request.POST.get('rate') and int(request.POST.get('rate'))>0:
                feedback.comment = "#"+str(request.POST.get('rate'))+"#" +feedback.comment

            if request.POST.get('parent_feedback') and request.POST.get('parent_feedback') != "":
                feedback.parent_feedback_id = int(request.POST.get('parent_feedback'))
            if request.FILES and 'attach' in request.FILES:
                att = request.FILES['attach']
            if att:
                att_extension = os.path.splitext(att.name)[1]
                att_name = os.path.splitext(att.name)[0]
                attach = 'feedbacks/'+str(randint(1000, 9999))+"_"+att_name+att_extension
                path = default_storage.save(attach, ContentFile(att.read()))
            if attach:
                feedback.attach = attach
            try:
                feedback.save()
                data.has_new_comment = True
                data.nb_comments = data.nb_comments + 1

                if feedback.feedback_type != 'general':
                    data.last_comment = feedback.comment
                    if request.POST.get('fdstatus') and data.project_type == "proposed":
                        data.save(update_fields=['has_new_comment', 'last_comment', 'nb_comments', 'status'])
                    else:
                        data.save(update_fields=['has_new_comment', 'last_comment', 'nb_comments'])
                else:
                    data.last_general_comment = feedback.comment
                    data.save(update_fields=['has_new_comment', 'last_general_comment', 'nb_comments'])

                messages.success(request, _("Feedback saved successfully"))
            except Exception as e:
                print('Error details: '+ str(e))
                default_storage.delete(attach)
                messages.error(request, _("Something went wrong"))
        else:
            messages.error(request, _("Fields * are required"))
    #End Handle comments

    if data:
        code = data.code
        project = {"id":data.pk, "project_settings":data.project_settings,
        "project_history":data.project_history, "user":(data.user and data.user.username), "title":data.title, "notes":data.notes, "shared":data.shared, "code":data.code, "dash_code":data.dash_code,
        "updated_at": data.updated_at.strftime('%d/%m/%Y'), "published_at": data.published_at.strftime('%d/%m/%Y'), "project_type": data.project_type, "contact": data.contact, "image": (data.image and data.image.url) or None, "static_image": data.static_image,
        "theme": str(data.theme.name), "link": data.link, "country": data.country, "state": data.state, "nb_likes": data.nb_likes, "user_request_type": data.user_request_type,
        "status": data.status.id, "status_name": data.status.name, "data_status": data.status, "nb_favorites": data.nb_favorites, "list_datasets": data.list_datasets}

        project["feedbacks"]={}
        project["feedbacks_req"]={}
        project["feedbacks_sta"]={}
        checklike = check_like(request, "project", project["id"], "like")
        checkfavorite = check_like(request, "project", project["id"], "favorite")


        project_settings = data.project_settings
        if "files" in project_settings:
            file_codes = []
            for keyfile, file in project_settings["files"].items():
                file_codes.append(keyfile)
            list_data = list_files(request, file_codes, project)
            project["list_files"] = list_data

        feedbacks = Feedback.objects.filter((Q(project__id=data.pk) & Q(feedback_type__exact='general')) & (Q(parent_feedback__isnull=True) & Q(file__isnull=True))).prefetch_related('feedbacks').order_by('-created_at')
        if feedbacks:
            for feed in feedbacks:
                varfeedname = "feedbacks"
                if feed.feedback_type == "status":
                    varfeedname = "feedbacks_sta"
                elif feed.feedback_type == "requirement":
                    varfeedname = "feedbacks_req"
                project[varfeedname][feed.pk] = {"id":feed.pk, "reply": feed.pk, "username":feed.username, "comment":feed.comment, "created_at":timeago(feed.created_at),
                "feedback_type_div": feed.feedback_type,"feedback_type": settings.FEEDBACK_TYPES[feed.feedback_type], "attach": (feed.attach and feed.attach.url) or None,
                "user_type": _(settings.USER_TYPES[feed.user_type])}
                project[varfeedname][feed.pk]["subfeedbacks"] = {}
                for subfeed in feed.feedbacks.all():
                    project[varfeedname][feed.pk]["subfeedbacks"][subfeed.pk] = {"id":subfeed.pk, "reply": feed.pk, "username":subfeed.username, "comment":subfeed.comment, "created_at":timeago(subfeed.created_at),
                    "feedback_type_div": feed.feedback_type, "feedback_type": settings.FEEDBACK_TYPES[feed.feedback_type], "attach": (subfeed.attach and subfeed.attach.url) or None,
                    "user_type": _(settings.USER_TYPES[subfeed.user_type])}
    else:
        messages.error(request, _("Code invalid"))
        return redirect("frontend:projects_mobile")

        PROJECT_TYPES = [
            #('internal', _('Internal')),
            ('external', _('External')),
            ('proposed', _('Proposed'))
        ]
    """feedback_types = [
        ('general', _('General Comment'))
    ]
    feedback_filter_types = [
        ('general', _('General')),
    ]"""
    user_types = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    #if data.project_type and data.project_type == "proposed":
    feedback_types = [
        ('general', _('General Comment')),
        ('status', _('Update Project Status')),
        ('requirement', _('Requirement Clarification'))
        #('data', _('Data Issue'))
    ]
    feedback_filter_types = [
        ('general', _('General')),
        ('status', _('Project Status')),
        ('requirement', _('Requirement Clarification'))
        #('data', _('Data Issue'))
    ]
    is_mobile = mobile(request)

    return render(request = request,
                  template_name = "frontend/detail_project_mobile.html",
                  context={"checklike": checklike, "project": project, "comment": comment, "name": name, "feedback_types": feedback_types, "feedback_filter_types": feedback_filter_types,
                  "user_types": user_types, "checkfavorite": checkfavorite, "is_mobile": is_mobile, "country": country})

#Import reuses france page
def import_reuses(request):
    Project.objects.filter(theme__name_en__icontains="Uncategorized").delete()
    #reuses_fr(request,0,5)
    #reuses_fr(request,1,15)
    return render(request = request, template_name='frontend/index.html', context = {})


#home page transparency
def home_trans(request):
    #activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MOBILE_APP_LANG)
    activate("en")
    request.session["active_service"] = "TRANS"
    activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    load_data(request, Theme, "list_themes", 0)
    if "transcountries" not in request.session:
        f = open(settings.COUNTRY_JSON,)
        countries = json.load(f)
        f.close()
        countries = list(countries.values())
        request.session["transcountries"] = countries
    #if "used_transcountries" not in request.session:
    get_transcountries(request)

    #handle feedback form
    if request.method == 'POST':
        if request.POST.get('message') and request.POST.get('full_name') and request.POST.get('email'):
            message = "Content of the feedback: "
            if request.POST.get('full_name'):
                message += "\nFull Name: "+request.POST.get('full_name')
            if request.POST.get('email'):
                message += "\nEmail: "+request.POST.get('email')
            message += "\nMessage: "+request.POST.get('message')
            send_mail(
                    settings.EMAIL_SUBJECT_PROTO,
                    message,
                    settings.EMAIL_FROM,
                    settings.EMAIL_RECEIVERS,
                    fail_silently=False,
                )
            messages.success(request, _("Feedback sent successfully"))
        else:
            messages.error(request, _("Please fill message"))

    return render(request = request, template_name='frontend/home_trans.html', context = {})


def trans_started(request, code = ''):
    #activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    activate("en")
    request.session["active_service"] = "TRANS"

    if request.user and request.user.id:
        country = settings.DEFAULT_COUNTRY
        state = ""
        shared = False
        if "transcountries" not in request.session:
            f = open(settings.COUNTRY_JSON,)
            countries = json.load(f)
            f.close()
            countries = list(countries.values())
            request.session["transcountries"] = countries

        transproject_settings = {}

        load_data(request, Theme, "list_transthemes", 1)
        load_data(request, Project, "trans_projects", 1, "internal")
        for key, value in request.session["list_transthemes"].items():
             transproject_settings[str(key)] = ""

        if code != "":
            try:
                data = TransProject.objects.get(code__exact=code)
                if data and data.user.pk != request.user.id:
                    messages.error(request, _("You do not have access rights to edit this project"))
                    return redirect("frontend:home_trans")
                state = data.state
                country = data.country
                transproject_settings = data.transproject_settings
                shared = data.shared
            except Exception as e:
                print('Error details: '+ str(e))
                messages.error(request, _("Code invalid"))
                return redirect("frontend:home_trans")

        if request.method == 'POST':
            country = request.POST.get("country")
            state = request.POST.get("trans_state")
            shared = request.POST.get("shared")
            has_projects = False

            for key, value in request.POST.items():
            	if "settopic" in key:
                    #print(value)
                    #print(request.POST.getlist(key))
                    topickey = int(re.search(r'\d+', key).group())
                    transproject_settings[str(topickey)] = request.POST.getlist(key)
                    if value != "":
                        has_projects = True
            #print(transproject_settings)

            #code = request.POST.get("code")
            if shared:
                shared = True
            else:
                shared = False

            if code != "":
                try:
                    data = TransProject.objects.get(code__exact=code)
                except Exception as e:
                    data = TransProject()
            else:
                data = TransProject()

            if not data.shared and shared:
                data.published_at = datetime.datetime.now()

            data.shared = shared
            data.country = country
            data.state = state
            data.transproject_settings = transproject_settings
            data.has_projects = has_projects

            #try:
            data.save()
            code = data.code
            messages.success(request, _("Project saved successfully"))
            return redirect("frontend:view_trans", code=code)
            #except Exception as e:
            #    print('Error details: '+ str(e))

        context = {"trans_state": state, "country": country, "shared": shared, "transproject_settings": transproject_settings}

        return render(request = request,
                      template_name='frontend/trans_started.html',
                      context = context)
    else:
        response = redirect("frontend:login")
        response['Location'] += '?next=/trans-started'
        return response

def view_trans(request, code = '', theme = ''):
    #activate((LANGUAGE_SESSION_KEY in request.session and request.session[LANGUAGE_SESSION_KEY]) or settings.MODELTRANSLATION_DEFAULT_LANGUAGE)
    activate("en")
    request.session["active_service"] = "TRANS"
    load_data(request, Theme, "list_transthemes", 1)
    get_transcountries(request)
    data = None
    context = {}

    if request.method == 'POST':
        country = request.POST.get("country")
        state = request.POST.get("state")
        context["country"] = country
        context["state"] = state
        filter = (Q(country__exact=country) & Q(shared__exact=True)) & (Q(has_projects__exact=True))
        if(state != ""):
            filter = filter & (Q(state__icontains=state.lower()))
        try:
            transprojects = TransProject.objects.filter(filter).order_by('-updated_at', '-created_at')
            context["transprojects"] = transprojects
            context["code"] = ""
            context["current_theme"] = ""

            print(len(transprojects))
            if len(transprojects) == 1:
                transprojects = transprojects.get()
                code = transprojects
                return redirect("frontend:view_trans", code=code)
        except Exception as e:
            print('Error details: '+ str(e))
            context["code"] = ""
            context["current_theme"] = ""
            messages.error(request, _("No transparency project available for this area. Please change your search options."))
        return render(request = request,
                      template_name='frontend/view_trans.html',
                      context = context)
    elif code != "":
        try:
            data = TransProject.objects.get(code__exact=code)
            context = {"proj": data, "code": code, "current_theme": theme, "country": data.country, "state": data.state}
            if theme != "":
                arr = theme.split("-")
                theme_id = arr[-1]
                theme_id = str(theme_id)
                context["theme_id"] = theme_id
                mytheme = Theme.objects.get(pk=theme_id)
                context["mytheme"] = mytheme
                if len(data.transproject_settings[theme_id]) == 0:
                    messages.error(request, _("No avialable associated project"))
                elif len(data.transproject_settings[theme_id]) == 1:
                    return redirect("frontend:dashbaord", code=data.transproject_settings[theme_id][0],theme=theme,trans_code=code)
                elif len(data.transproject_settings[theme_id]) > 1:
                    #print(data.transproject_settings[theme_id])
                    list_data = {}
                    all_data = []
                    all_data = Project.objects.filter(dash_code__in=data.transproject_settings[theme_id]).order_by('-updated_at', '-created_at')
                    for data in all_data:
                        list_data[str(data.pk)] = {"id":data.pk, "code":data.code, "dash_code": data.dash_code, "image": (data.image and data.image.url) or (settings.DEFAULT_PROJECT_IMAGE), "static_image": data.static_image,
                        "notes":data.notes, "project_type":data.project_type, "title":data.title, "updated_at": (data.updated_at and data.updated_at.strftime("%d/%m/%Y")) or (data.created_at and data.created_at.strftime("%d/%m/%Y")) }
                    context["projects"] = list_data
                    context["goto"] = "projects"
            return render(request = request,
                          template_name='frontend/view_trans.html',
                          context = context)

        except Exception as e:
            code = ""
            context = {"code": code}
            print('Error details: '+ str(e))
            messages.error(request, _("Code invalid"))
            return render(request = request,
                          template_name='frontend/view_trans.html',
                          context = context)
    elif code == "":
        context = {"code": code}
        return render(request = request,
                template_name='frontend/view_trans.html',
                context = context)
