from django.contrib import admin
from .models import FeeHead, Payment


@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'frequency', 'is_active']
    search_fields = ['name']
    list_filter = ['frequency', 'is_active', 'branch']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'status', 'due_date', 'paid_date']
    search_fields = ['student__name']
    list_filter = ['status', 'due_date', 'branch']
