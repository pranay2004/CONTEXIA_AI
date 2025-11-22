from django.contrib import admin
from .models import UploadedFile, GeneratedContent


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file_type', 'original_filename', 'word_count', 'detected_topic', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('original_filename', 'url', 'extracted_text', 'detected_topic')
    readonly_fields = ('uploaded_at', 'processed_at', 'word_count')
    ordering = ('-uploaded_at',)


@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ('uploaded_file', 'model_used', 'created_at')
    list_filter = ('model_used', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
