from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django.forms import ModelForm
from visualizations.models import UploadFile
from django.utils.translation import ugettext_lazy as _
import requests
from django.conf import settings
from utils.viz import is_downloadable, get_filename_from_cd

class UploadFileForm(ModelForm):
    class Meta:
        model = UploadFile
        fields = ["file_name"]

class ExternalLinkForm(ModelForm):
    EXT_TYPES = [
        ('.csv', _('csv')),
        ('.json', _('json')),
        ('.xls', _('xls')),
        ('.xlsx', _('xlsx'))
    ]
    file_ext = forms.ChoiceField(
        choices=EXT_TYPES,
        required=True, label=_("Extension")
    )
    file_link = forms.URLField(required=True, label=_("Link"))
    title = forms.CharField(required=True, label=_("Title"), max_length=100)
    description = forms.CharField(widget=forms.Textarea, max_length=700)
    refresh_timeout = forms.IntegerField(required=False, label=_("Refresh Timeout"), help_text=_("Let empty if you don't need to refresh data"))

    def clean(self):
        cleaned_data = super().clean()
        file_link = cleaned_data.get("file_link")
        file_ext = cleaned_data.get("file_ext")
        """theme = cleaned_data.get("theme")
        if not theme:
            raise forms.ValidationError(_("File theme is required"))"""

        if file_link and file_ext:
            if not is_downloadable(file_link):
                raise forms.ValidationError(_("Link isn't downloadable"))
            r = requests.get(file_link, allow_redirects=True)
            content = r.content
            if not content or content is None:
                raise forms.ValidationError(_("Link invalid"))

            filename = get_filename_from_cd(r.headers.get('content-disposition'))
            #print("filename===========================")
            #print(filename)
            real_file_ext = filename.split(".")[-1]
            #print(real_file_ext)
            if real_file_ext not in settings.LIST_EXTENSIONS:
                raise forms.ValidationError(_("File extension not valid"))
            real_file_ext = "."+real_file_ext
            if real_file_ext != file_ext:
                raise forms.ValidationError(_("File extension doesn't match with the file to download"))


    class Meta:
        model = UploadFile
        fields = ("file_link", "title", "refresh_timeout", "file_ext")
    field_order = ['file_ext', 'file_link', 'title', 'description', 'refresh_timeout']

    def save(self, commit=True):
        file = super(ExternalLinkForm, self).save(commit=False)
        file.file_link = self.cleaned_data["file_link"]
        file.title = self.cleaned_data["title"]
        #file.theme = self.cleaned_data["theme"]
        file.refresh_timeout = self.cleaned_data["refresh_timeout"]
        file.file_ext = self.cleaned_data["file_ext"]
        file.more_details = {"title": file.title, "description": self.cleaned_data["description"] or ""}
        if not self.cleaned_data["refresh_timeout"]:
            file.refresh_timeout = 0
        if commit:
            file.save()
        return file

class NewUserForm(UserCreationForm):
    USER_TYPES = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        required=True, label=_("User Type")
    )
    email = forms.EmailField(required=True, label=_("Email address"))

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email")

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password2']:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.user_type = self.cleaned_data["user_type"]
        if commit:
            user.save()
        return user
