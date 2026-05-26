from django.contrib import admin
from .models import Inquiry


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display    = ('name', 'email', 'project_type', 'status', 'created_at')
    list_filter     = ('status', 'project_type')
    search_fields   = ('name', 'email', 'message')
    readonly_fields = ('ip_address', 'created_at', 'updated_at')
    ordering        = ('-created_at',)

    fieldsets = (
        ('Contact Details', {
            'fields': ('name', 'email', 'project_type')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Management', {
            'fields': ('status', 'ip_address', 'created_at', 'updated_at')
        }),
    )
