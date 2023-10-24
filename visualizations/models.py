from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
# import string library function
import string
import random
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from crum import get_current_user
from urllib.parse import urlparse
from django.contrib.postgres.fields import JSONField
from django.utils import timezone


#method to generate code
def code_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generate_code(model, prefix, size=6):
    code = prefix+""+code_generator(size)
    while model.objects.filter(code=code).exists():
        code = prefix+""+code_generator(size)
    return code

def generate_dash_code(model, prefix, size=6):
    code = prefix+""+code_generator(size)
    while model.objects.filter(dash_code=code).exists():
        code = prefix+""+code_generator(size)
    return code

#method to change the name of the uploaded file
def path_and_rename(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.code, ext)
    return os.path.join('uploads', filename)

#Model to store the feature
class Feature(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=5, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    apply_onlyto_viz = models.TextField(null=True, blank=True)
    sequence = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'
        ordering = ['sequence']

#Model to store the viz objectives
class VizGoal(models.Model):
    name = models.CharField(max_length=150)
    active = models.BooleanField(default=True)
    viz_types = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'VizGoal'
        verbose_name_plural = 'VizGoals'
        ordering = ['name']

#Model to store the datatype
class DataType(models.Model):
    DATA_TYPES = [
        ('numerical', _('Numerical')),
        ('temporal', _('Temporal')),
        ('geographical', _('Geographical')),
        ('categorical', _('Categorical'))
    ]
    name = models.CharField(max_length=150)
    icon = models.CharField(max_length=50, null=True, blank=True)
    abbreviation = models.CharField(max_length=20, null=True, blank=True)
    pandas_name = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    parent = models.CharField(
        max_length=30,
        choices=DATA_TYPES,
        default='categorical',
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'DataType'
        verbose_name_plural = 'DataTypes'
        ordering = ['name']

#Model to store the datatype rules
class DataTypeRule(models.Model):
    USER_TYPES = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    rule = models.TextField()
    datatype = models.ForeignKey(DataType, on_delete=models.CASCADE,
        related_name="datatyperules")
    user_type = models.CharField(
        max_length=30,
        choices=USER_TYPES,
        default='non-expert',
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='datatyperules',
        on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    update_date = models.BooleanField(default=True)
    address_ip = models.CharField(max_length=20, blank=True, editable=False)

    def __str__(self):
        return self.rule

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None and not self.user_type:
            self.user_type = user.user_type
        if not self.pk and user is not None:
            self.user = user
        if self.update_date:
            self.updated_at = timezone.now()
        super(DataTypeRule, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'DataTypeRule'
        verbose_name_plural = 'DataTypeRules'
        ordering = ['-created_at']

#Model to store the vizmark
class VizMark(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    sequence = models.IntegerField(default=0, blank=True)
    max_elements = models.IntegerField(default=1, blank=True)
    is_orientation = models.BooleanField(default=False)
    is_grouping = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'VizMark'
        verbose_name_plural = 'VizMarks'
        ordering = ['sequence', 'name']

#Model to store the viztype
class VizType(models.Model):
    """VIZ_TOOLS = [
        ('plotly', _('Plotly')),
        ('highcharts', _('Highcharts')),
        ('d3', _('D3')),
        ('vega', _('Vega')),
        ('matplotlib', _('Matplotlib')),
    ]"""
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    graph_function = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='viztypes/', null=True, blank=True)
    sequence = models.IntegerField(default=0, blank=True)
    active = models.BooleanField(default=True)
    include_marks = models.TextField(null=True, blank=True)
    """viz_tool = models.CharField(
        max_length=30,
        choices=VIZ_TOOLS,
        default='plotly',
    )"""

    def __str__(self):
        return self.name

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.image.url)
        else:
            return 'No Image Found'
    image_tag.short_description = 'Image'


    class Meta:
        verbose_name = 'VizType'
        verbose_name_plural = 'VizTypes'
        ordering = ['sequence', 'name']


#Model to store the input
class VizInput(models.Model):
    code = models.CharField(max_length=5, null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    insight = models.TextField(null=True, blank=True)
    scores = models.TextField(null=True, blank=True)
    feature_settings = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'VizInput'
        verbose_name_plural = 'VizInputs'
        ordering = ['code']

#Model to store the input feature
class VizInputFeature(models.Model):
    value = models.TextField(null=True, blank=True)
    formula = models.TextField(null=True, blank=True)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE,
        related_name="vizinputfeatures")
    vizinput = models.ForeignKey(VizInput, on_delete=models.CASCADE,
        related_name="vizinputfeatures")

    class Meta:
        verbose_name = 'VizInputFeature'
        verbose_name_plural = 'VizInputFeatures'

#Model to store the outputs for viz
class VizOutput(models.Model):
    code = models.CharField(max_length=5, null=True, blank=True, editable=False)
    USER_TYPES = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    score = models.DecimalField(max_digits=5, decimal_places=2)
    viztype = models.ForeignKey(VizType, on_delete=models.CASCADE,
        related_name="vizoutputs")
    vizinput = models.ForeignKey(VizInput, on_delete=models.CASCADE,
        related_name="vizoutputs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='vizoutputs',
        on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(
        max_length=30,
        choices=USER_TYPES,
        default='non-expert',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project_code = models.CharField(max_length=10, blank=True, null=True)
    viz_code = models.CharField(max_length=15, blank=True, null=True)
    mark_settings = JSONField(null=True, blank=True, default=dict)
    mark_settings_str = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None and not self.user_type:
            self.user_type = user.user_type
        if not self.pk and user is not None:
            self.user = user
        super(VizOutput, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'VizOutput'
        verbose_name_plural = 'VizOutputs'
        ordering = ['-created_at']

#Model to store the viztype marks
class VizTypeMark(models.Model):
    #('expert', _('Confident')),
    #('intermediate', _('Less confident')),
    #('non-expert', _('Not confident'))
    USER_TYPES = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    rule = JSONField(blank=True, null=True, default=dict)
    vizmark = models.ForeignKey(VizMark, on_delete=models.CASCADE,
        related_name="viztypemarks")
    viztype = models.ForeignKey(VizType, on_delete=models.CASCADE,
        related_name="viztypemarks")
    user_type = models.CharField(
        max_length=30,
        choices=USER_TYPES,
        default='non-expert',
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='viztypemarks',
        on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project_code = models.CharField(max_length=10, blank=True, null=True)
    viz_code = models.CharField(max_length=15, blank=True, null=True)
    vizoutput = models.ForeignKey(VizOutput, on_delete=models.CASCADE,
    related_name="viztypemarks", blank=True, null=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None and not self.user_type:
            self.user_type = user.user_type
        super(VizTypeMark, self).save(*args, **kwargs)

    def __str__(self):
        return self.viz_code

    class Meta:
        verbose_name = 'VizMarkRule'
        verbose_name_plural = 'VizMarkRules'
        ordering = ['-created_at']

#Model to store the different open data software such as CKAN, Opendatasoft
class PlatformPortal(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    more_details = JSONField(blank=True, default=dict)
    link = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'PlatformPortal'
        verbose_name_plural = 'PlatformPortals'
        ordering = ['name']

#Model to store the different open data portals
class DataPortal(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    more_details = JSONField(blank=True, default=dict)
    platform = models.ForeignKey(PlatformPortal,
        related_name="dataportals", on_delete=models.SET_NULL, null=True, blank=True)
    link = models.CharField(max_length=255, null=True, blank=True)
    is_popular = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='portals',
        on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    #Assign user, user before save
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None:
            self.user = user
        super(DataPortal, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'DataPortal'
        verbose_name_plural = 'DataPortals'
        ordering = ['name']

"""#Model to store the different tools
class Tool(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tools',
        on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tool'
        verbose_name_plural = 'Tools'
        ordering = ['name']"""


#Model to store the Theme of project
class Theme(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to='themes/', null=True, blank=True)
    sequence = models.IntegerField(default=0, blank=True)
    sequence_mobile = models.IntegerField(default=0, blank=True)
    active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.image.url)
        else:
            return 'No Image Found'
    image_tag.short_description = 'Image'

    class Meta:
        verbose_name = 'Theme'
        verbose_name_plural = 'Themes'
        ordering = ['sequence', 'name']

#Model to store the Theme of project
class ProjectStatus(models.Model):
    name = models.CharField(max_length=150)
    sequence = models.IntegerField(default=0, blank=True)
    for_update_status = models.BooleanField(default=False)
    for_suggested_project = models.BooleanField(default=False)
    for_existing_project = models.BooleanField(default=False)
    abbreviation = models.CharField(max_length=5, default="")
    icon = models.CharField(max_length=20, default="")
    color = models.CharField(max_length=10, default="")
    bg_color = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ProjectStatus'
        verbose_name_plural = 'ProjectStatuses'
        ordering = ['sequence', 'name']

#Model to store the project information
class Project(models.Model):
    PROJECT_TYPES = [
        ('internal', _('Internal')),
        ('external', _('External')),
        ('proposed', _('Proposed'))
    ]
    """USER_REQUEST_TYPES = [
        ('citizen', _('Citizen')),
        ('developer', _('Developer'))
    ]"""
    code = models.CharField(max_length=8, blank=True, editable=False)
    #register file settings such as is_real_time_data, file changement
    project_settings = JSONField(blank=True, default=dict)
    project_history = JSONField(blank=True, default=dict)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects',
        on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    developed_internally = models.BooleanField(default=False)
    show_in_mobile_apps = models.BooleanField(default=False)
    dash_code = models.CharField(max_length=8, blank=True, editable=False)
    address_ip = models.CharField(max_length=20, blank=True, editable=False)
    has_vizs = models.BooleanField(default=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    shared = models.BooleanField(default=False)
    theme = models.ForeignKey(Theme, related_name='themes',
        on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(ProjectStatus, related_name='statuses',
        on_delete=models.SET_NULL, null=True, blank=True)
    status_history = models.TextField(null=True, blank=True)
    project_type = models.CharField(
        max_length=30,
        choices=PROJECT_TYPES,
        default='internal',
    )
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    static_image = models.CharField(max_length=500, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    link = models.CharField(max_length=500, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    nb_likes = models.IntegerField(default=0, blank=True)
    nb_favorites = models.IntegerField(default=0, blank=True)
    user_request_type = models.CharField(max_length=30, null=True, blank=True)
    has_new_comment = models.BooleanField(default=False)
    last_comment = models.TextField(null=True, blank=True)
    last_general_comment = models.TextField(null=True, blank=True)
    nb_comments = models.IntegerField(default=0, blank=True)
    is_popular = models.BooleanField(default=False)
    list_datasets = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.code

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s" style="width: 45px; height:45px;" />' % self.image.url)
        else:
            return 'No Image Found'
    image_tag.short_description = 'Image'

    #Assign code, user before save
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None:
            self.user = user
        if not self.code and not self.pk:
            self.code = generate_code(Project, settings.PREFIX_PROJECT)
        if not self.dash_code and not self.pk:
            self.dash_code = generate_dash_code(Project, settings.PREFIX_DASH)
        super(Project, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']


#Model to store the transparency project information
class TransProject(models.Model):
    code = models.CharField(max_length=8, blank=True, editable=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    transproject_settings = JSONField(blank=True, default=dict)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='transprojects',
        on_delete=models.SET_NULL, null=True, blank=True)
    shared = models.BooleanField(default=False)
    has_projects = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.code

    #Assign code, user before save
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None:
            self.user = user
        if not self.code and not self.pk:
            self.code = generate_code(TransProject, settings.PREFIX_TRANSPROJECT)
        super(TransProject, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'TransProject'
        verbose_name_plural = 'TransProjects'
        ordering = ['-created_at']


#Model to store the file of user
class UploadFile(models.Model):
    code = models.CharField(max_length=8, blank=True, editable=False)
    # Url of the file in case the user just puts the link to access the file
    file_link = models.CharField(null=True, blank=True,max_length=250)
    # File name on the server in case the user just uploads some files
    file_name = models.FileField(upload_to=path_and_rename, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    file_ext = models.CharField(max_length=50, null=True, blank=True)
    is_demo = models.BooleanField(default=False)
    refresh_timeout = models.IntegerField(default=0, null=True, blank=True)
    portal = models.ForeignKey(DataPortal, related_name='uploadfiles',
        on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='uploadfiles',
        on_delete=models.SET_NULL, null=True, blank=True)
    init_settings = JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = JSONField(blank=True, default=dict)
    active = models.BooleanField(default=True)
    more_details = JSONField(blank=True, default=dict)
    related_files = models.ManyToManyField("self", blank=True, related_name="related_files")
    related_projects = models.ManyToManyField(Project, blank=True, related_name="related_projects")
    from_query = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)
    theme = models.ForeignKey(Theme, related_name='uploadfiles',
        on_delete=models.SET_NULL, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    nb_likes = models.IntegerField(default=0, blank=True)
    nb_favorites = models.IntegerField(default=0, blank=True)
    has_new_comment = models.BooleanField(default=False)
    last_comment = models.TextField(null=True, blank=True)
    last_general_comment = models.TextField(null=True, blank=True)
    nb_comments = models.IntegerField(default=0, blank=True)
    data_provided = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    #Assign title, user before save
    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None:
            self.user = user
        if not self.code and not self.pk:
            self.code = generate_code(UploadFile, settings.PREFIX_FILE)
        if not self.title and self.file_name:
            title = os.path.basename(self.file_name.name)
            self.title = os.path.splitext(title)[0]
            self.file_ext = os.path.splitext(title)[1]
        super(UploadFile, self).save(*args, **kwargs)

    #Need to drop table and file when delete record
    #def delete(self, *args, **kwargs):
    #    for obj in self:
    #        obj.img.delete()
    #    super(UploadFile, self).delete(*args, **kwargs)

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['-created_at']


class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('general', _('General')),
        ('status', _('Project Status')),
        ('data', _('Data Issue')),
        ('requirement', _('Requirement Clarification'))
    ]
    USER_TYPES = [
        ('non-expert', _('Citizen')),
        ('intermediate', _('Publisher')),
        ('expert', _('Developer'))
    ]
    comment = models.TextField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
        related_name="feedbacks", null=True, blank=True)
    file = models.ForeignKey(UploadFile, on_delete=models.CASCADE,
        related_name="feedbacks", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='feedbacks',
        on_delete=models.SET_NULL, null=True, blank=True)
    user_type = models.CharField(
        max_length=30,
        choices=USER_TYPES,
        default='non-expert',
    )
    username = models.CharField(max_length=255, null=True, blank=True)
    parent_feedback = models.ForeignKey('self', related_name='feedbacks',
        on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    feedback_type = models.CharField(
        max_length=30,
        choices=FEEDBACK_TYPES,
        default='general',
    )
    attach = models.FileField(upload_to='feedbacks/', null=True, blank=True)

    def __str__(self):
        return self.comment

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None:
            self.user = user
            #self.username = user.username

        super(Feedback, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']

class Like(models.Model):
    ACTION_TYPES = [
        ('like', _('Like')),
        ('favorite', _('Favorite'))
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
        related_name="likes", null=True, blank=True)
    file = models.ForeignKey(UploadFile, on_delete=models.CASCADE,
        related_name="likes", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes',
        on_delete=models.SET_NULL, null=True, blank=True)
    address_ip = models.CharField(max_length=20, blank=True, editable=False)
    action_type = models.CharField(
        max_length=30,
        choices=ACTION_TYPES,
        default='like',
    )

    def __str__(self):
        return self.address_ip

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        if not self.pk and user is not None:
            self.user = user
        super(Like, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'

class SubscribeDataProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE,
        related_name="subscribes", null=True, blank=True)
    file = models.ForeignKey(UploadFile, on_delete=models.CASCADE,
        related_name="subscribes", null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'SubscribeDataProject'
        verbose_name_plural = 'SubscribeDataProjects'

class SubscribeDataArea(models.Model):
    email = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'SubscribeDataArea'
        verbose_name_plural = 'SubscribeDataAreas'

#Set code to vizinput after save
@receiver(post_save, sender=VizInput)
def save_code_vizinput(sender, instance, **kwargs):
    if not instance.code:
        id = instance.id
        code = "VI" + str(id)
        instance.code = code
        instance.save()

#Set code to vizoutput after save
@receiver(post_save, sender=VizOutput)
def save_code_vizoutput(sender, instance, **kwargs):
    if not instance.code:
        id = instance.id
        code = "VO" + str(id)
        instance.code = code
        instance.save()

@receiver(post_save, sender=UploadFile)
def save_url_uploadfile(sender, instance, **kwargs):
    if instance.file_name and instance.file_link != instance.file_name.url:
        instance.file_link = instance.file_name.url
        instance.save()
