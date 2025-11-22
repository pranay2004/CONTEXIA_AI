from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class UploadedFile(models.Model):
    """
    Stores uploaded files and their extracted content
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads', null=True)

    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('pptx', 'PowerPoint'),
        ('txt', 'Text File'),
        ('video', 'Video'),
        ('url', 'URL'),
    ]
    
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    original_filename = models.CharField(max_length=500, blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    url = models.URLField(blank=True)
    
    # Extracted content
    extracted_text = models.TextField()
    word_count = models.IntegerField(default=0)
    detected_topic = models.CharField(max_length=200, blank=True)
    
    # Metadata
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_file_type_display()} - {self.original_filename or self.url or 'Text'}"


class GeneratedContent(models.Model):
    """
    Stores generated content for user uploads
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generations', null=True)

    uploaded_file = models.ForeignKey(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='generated_contents'
    )
    
    # Generated content JSON
    content_json = models.JSONField()
    
    # Metadata
    model_used = models.CharField(max_length=100, default='gemini-1.5-flash')
    trends_used = models.JSONField(default=list)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Generated content for {self.uploaded_file}"
