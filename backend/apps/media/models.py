from django.db import models
from django.utils import timezone


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
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input/Output files
    input_file = models.FileField(upload_to='media_jobs/input/%Y/%m/%d/')
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
