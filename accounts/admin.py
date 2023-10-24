from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "email", "user_type"]
    list_display_links = ["username"]
    # Fields that you want to search by (can't search by foreign key)
    search_fields = ["username", "first_name", "last_name", "email", "user_type"]
    # Fields that we can filter. the filter will be shown on the right side of the table
    list_filter = ['user_type']
# Change text shown on Admin header
admin.site.site_header = "ODEON Administration"
# Disable group on admin page
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
