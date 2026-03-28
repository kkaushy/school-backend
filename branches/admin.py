from django.contrib import admin
from .models import Branch, BranchUser


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'company_admin']
    search_fields = ['name', 'location']


@admin.register(BranchUser)
class BranchUserAdmin(admin.ModelAdmin):
    list_display = ['branch', 'user']
    list_filter = ['branch']
