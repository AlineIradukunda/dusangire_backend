from django.contrib import admin
from .models import School, Contribution, AdminUser, Distribution
from django.contrib.auth.admin import UserAdmin

admin.site.site_header = "Dusangire Lunch"
admin.site.site_title = "Dusangire Lunch"
admin.site.index_title = "Dusangire Lunch"
admin.site.register(School)
admin.site.register(Contribution)
admin.site.register(AdminUser, UserAdmin)
admin.site.register(Distribution)
