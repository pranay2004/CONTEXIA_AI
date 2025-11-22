from django.db import models
from django.utils import timezone
from pgvector.django import VectorField, HnswIndex

class TrendArticle(models.Model):
    """
    Stores scraped marketing trend articles with their embeddings
    """
    SOURCE_CHOICES = [
        ('sprout_social', 'Sprout Social Insights'),
        ('later', 'Later Blog'),
        ('social_media_examiner', 'Social Media Examiner'),
    ]
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, db_index=True)
    title = models.CharField(max_length=500)
    url = models.URLField(unique=True)
    snippet = models.TextField(blank=True)
    full_text = models.TextField()
    published_date = models.DateTimeField(null=True, blank=True)
    # Scraping metadata
    scraped_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Vector storage (Nullable to prevent migration errors)
    embedding = VectorField(dimensions=384, null=True, blank=True)
    
    class Meta:
        ordering = ['-published_date', '-scraped_at']
        indexes = [
            # HNSW Index for fast approximate nearest neighbor search
            HnswIndex(
                name='trend_embedding_index',
                fields=['embedding'],
                m=16,
                ef_construction=64,
                opclasses=['vector_l2_ops']
            )
        ]
    
    def __str__(self):
        return f"{self.get_source_display()} - {self.title[:50]}"
    
    @property
    def recency_factor(self):
        """Calculate recency score (0-1) based on published date"""
        if not self.published_date:
            return 0.5
        
        days_old = (timezone.now() - self.published_date).days
        
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        elif days_old <= 180:
            return 0.4
        else:
            return 0.2


class ScraperJob(models.Model):
    """
    Tracks scraper execution jobs
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    source = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    articles_scraped = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.source} - {self.status} ({self.created_at})"