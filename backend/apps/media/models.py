from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class MediaJob(models.Model):
    """
    Tracks media processing jobs (images/videos)
    """
    JOB_TYPE_CHOICES = [
        ('remove_bg', 'Remove Background'),
        ('upscale', 'Upscale Image'),
        ('restore_face', 'Restore Face'),
        ('video_scenes', 'Detect Video Scenes'),
        ('video_transcribe', 'Transcribe Video'),
        ('ai_image_generation', 'AI Image Generation'),  # NEW: For AI-generated images
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input/Output files (nullable for AI generation tasks)
    input_file = models.FileField(upload_to='media_jobs/input/%Y/%m/%d/', null=True, blank=True)
    output_file = models.FileField(upload_to='media_jobs/output/%Y/%m/%d/', null=True, blank=True)
    
    # Job metadata
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Celery task ID
    task_id = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_job_type_display()} - {self.status}"


class ProcessedImage(models.Model):
    """
    Stores processed images (collages, framed images)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_images', null=True)
    
    # Link to uploaded file if applicable
    uploaded_file = models.ForeignKey(
        'ingest.UploadedFile',
        on_delete=models.CASCADE,
        related_name='processed_images',
        null=True,
        blank=True
    )
    
    # Image type
    IMAGE_TYPE_CHOICES = [
        ('collage', 'Collage'),
        ('framed', 'Framed Individual'),
        ('social_ready', 'Social Media Ready'),
    ]
    image_type = models.CharField(max_length=20, choices=IMAGE_TYPE_CHOICES)
    
    # Image file
    image_file = models.ImageField(upload_to='processed_images/%Y/%m/%d/')
    
    # Metadata
    original_filename = models.CharField(max_length=255, blank=True)
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)
    file_size = models.IntegerField(null=True)  # in bytes
    
    # Processing details
    processing_params = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_image_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
