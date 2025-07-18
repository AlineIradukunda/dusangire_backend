from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import (
    School, TransferReceived, AdminUser, Distribution, Report
)
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse


admin.site.site_header = "Dusangire Lunch"
admin.site.site_title = "Dusangire Lunch"
admin.site.index_title = "Dusangire Lunch"

# Regular models
admin.site.register(TransferReceived)
admin.site.register(AdminUser, UserAdmin)
admin.site.register(Distribution)
admin.site.register(Report)

# Custom Record Admin

class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "sector", "AccountNumber", "delete_status")
    search_fields = ("name", "district", "sector", "AccountNumber")

admin.site.register(School, SchoolAdmin)


