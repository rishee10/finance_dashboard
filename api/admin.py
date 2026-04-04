from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from .models import User, FinancialRecord

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_active')
    fieldsets     = UserAdmin.fieldsets + (
        ('Role & Status', {'fields': ('role',)}),
    )

@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display  = ('id', 'entry_type', 'category', 'amount', 'date', 'is_deleted')
    list_filter   = ('entry_type', 'category', 'is_deleted')
    search_fields = ('description',)