from django.contrib import admin
from .models import MediaJob


@admin.register(MediaJob)
class MediaJobAdmin(admin.ModelAdmin):
    list_display = ('job_type', 'status', 'created_at', 'started_at', 'completed_at')
    list_filter = ('job_type', 'status', 'created_at')
    readonly_fields = ('task_id', 'created_at', 'started_at', 'completed_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Job Info', {
            'fields': ('job_type', 'status', 'task_id')
        }),
        ('Files', {
            'fields': ('input_file', 'output_file')
        }),
        ('Results', {
            'fields': ('result_data', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
    )
