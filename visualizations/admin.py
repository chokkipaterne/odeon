from django.contrib import admin
from .models import Feature, DataType, VizMark, VizType, VizInput, UploadFile, DataTypeRule, VizTypeMark, \
VizInputFeature, VizOutput, Project, VizGoal, DataPortal, PlatformPortal, Feedback, Theme, Like, ProjectStatus, \
SubscribeDataArea, SubscribeDataProject, TransProject

# Register your models here.
# djangoprojet mysite for more settings or https://docs.djangoproject.com/en/3.0/ref/contrib/admin/

class InlineDataTypeRule(admin.TabularInline):
    model = DataTypeRule
    extra = 0

class DataTypeAdmin(admin.ModelAdmin):
    inlines = [InlineDataTypeRule]
    list_display = ["name", "icon", "abbreviation", "pandas_name", "parent", "active"]
    list_display_links = ["name"]
    list_editable = ["icon", "active"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name", "abbreviation", "pandas_name", "parent"]
    list_filter = ["parent", "active"]

class InlineVizTypeMark(admin.TabularInline):
    model = VizTypeMark
    extra = 0

class VizTypeAdmin(admin.ModelAdmin):
    inlines = [InlineVizTypeMark]
    list_display = ["image_tag", "name", "graph_function", "include_marks", "sequence", "active"]
    list_display_links = ["name"]
    list_editable = ["include_marks",  "graph_function", "sequence", "active"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name", "description"]
    list_filter = ["active"]

class VizMarkAdmin(admin.ModelAdmin):
    inlines = [InlineVizTypeMark]
    list_display = ["name", "description", "sequence", "max_elements", "is_orientation", "active"]
    list_editable = ["sequence", "description", "max_elements", "is_orientation", "active"]
    list_display_links = ["name"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name", "description"]
    list_filter = ["active"]

class InlineVizInputFeature(admin.TabularInline):
    model = VizInputFeature
    extra = 0

class InlineVizOutput(admin.TabularInline):
    model = VizOutput
    extra = 0

class VizInputAdmin(admin.ModelAdmin):
    inlines = [InlineVizInputFeature, InlineVizOutput]
    list_display = ["code", "insight", "scores"]
    search_fields = ["code", "insight", "scores"]


class UploadFileAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "is_demo", "is_requested", "active", "from_query", "portal", "user", "file_link", "init_settings"]
    list_display_links = ["code"]
    list_editable = ["is_demo", "active", "init_settings"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["code", "title", "country", "state"]
    list_filter = ["user","is_demo", "active", "from_query", "portal", "is_requested"]

class FeatureAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["code", "name", "sequence", "formula", "apply_onlyto_viz", "active", "is_primary"]
    list_display_links = ["name"]
    list_editable = ["active", "sequence", "is_primary", "formula", "apply_onlyto_viz"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name", "code", "description"]
    list_filter = ["active", "is_primary"]

class ProjectAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["image_tag", "code", "dash_code", "project_type", "show_in_mobile_apps", "is_popular", "shared", "nb_favorites", "theme", "user", "contact", "address_ip", "created_at"]
    list_display_links = ["code"]
    list_editable = ["theme", "shared", "show_in_mobile_apps", "is_popular", "nb_favorites"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["code", "country"]
    list_filter = ["user", "theme", "project_type", "shared", "show_in_mobile_apps", "project_type", "is_popular"]

class DataTypeRuleAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["created_at", "updated_at", "rule", "datatype", "user_type", "user"]
    list_display_links = ["created_at"]
    list_editable = ["rule"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["rule", "user_type"]
    list_filter = ["user", "datatype"]

class VizGoalAdmin(admin.ModelAdmin):
    list_display = ["name", "viz_types", "active"]
    list_display_links = ["name"]
    list_editable = ["viz_types", "active"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]
    list_filter = ["active"]

class DataPortalAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["name", "link", "active", "is_popular", "platform", "more_details", "created_at"]
    list_display_links = ["name"]
    list_editable = ["link", "more_details", "active", "is_popular"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]
    list_filter = ["active", "platform"]

class PlatformPortalAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["name", "link", "active", "more_details", "created_at"]
    list_display_links = ["name"]
    list_editable = ["link", "more_details", "active"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]
    list_filter = ["active"]

class FeedbackAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["created_at", "comment", "feedback_type", "project", "file", "user", "parent_feedback"]
    list_display_links = ["created_at"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["comment"]
    list_filter = ["project", "user", "file", "parent_feedback", "feedback_type"]

class ThemeAdmin(admin.ModelAdmin):
    list_display = ["image_tag", "name", "is_popular", "sequence", "sequence_mobile", "active"]
    list_display_links = ["image_tag", "name"]
    list_editable = ["sequence_mobile", "sequence", "is_popular", "active"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]
    list_filter = ["active"]

class LikeAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["address_ip", "action_type", "project", "file", "user"]
    list_display_links = ["address_ip"]
    search_fields = ["address_ip"]
    list_filter = ["project", "user", "file", "action_type"]

class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation", "sequence", "icon", "color", "bg_color", "for_update_status", "for_suggested_project", "for_existing_project"]
    list_display_links = ["name", "abbreviation"]
    list_editable = ["sequence", "icon", "color", "bg_color", "for_update_status", "for_suggested_project", "for_existing_project"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]

class SubscribeDataProjectAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["email", "project", "file"]
    list_display_links = ["email"]
    search_fields = ["email"]
    list_filter = ["project", "file"]

class SubscribeDataAreaAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["email", "country", "state"]
    list_display_links = ["email"]
    search_fields = ["email", "country", "state"]

"""class ToolAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = ["name", "link", "active", "is_popular", "contact", "description", "created_at"]
    list_display_links = ["name"]
    list_editable = ["link", "contact", "active", "is_popular"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["name"]
    list_filter = ["active", "is_popular"]"""

class TransProjectAdmin(admin.ModelAdmin):
    # Fields to display in the table (can't add many2many relataion)
    list_display = [ "code", "country", "state", "shared", "has_projects", "user",  "created_at"]
    list_display_links = ["code"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["code", "country", "state"]
    list_filter = ["user",  "shared", "has_projects"]

admin.site.register(Feature, FeatureAdmin)
admin.site.register(DataType, DataTypeAdmin)
admin.site.register(DataTypeRule, DataTypeRuleAdmin)
admin.site.register(VizMark, VizMarkAdmin)
admin.site.register(VizType, VizTypeAdmin)
admin.site.register(VizInput, VizInputAdmin)
admin.site.register(UploadFile, UploadFileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(VizGoal, VizGoalAdmin)
admin.site.register(DataPortal, DataPortalAdmin)
admin.site.register(PlatformPortal, PlatformPortalAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Theme, ThemeAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(ProjectStatus, ProjectStatusAdmin)
admin.site.register(SubscribeDataArea, SubscribeDataAreaAdmin)
admin.site.register(SubscribeDataProject, SubscribeDataProjectAdmin)
admin.site.register(TransProject, TransProjectAdmin)
#admin.site.register(Tool, ToolAdmin)
