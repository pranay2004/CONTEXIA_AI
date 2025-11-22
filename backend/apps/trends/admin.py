from django.contrib import admin
from .models import TrendArticle, ScraperJob

@admin.register(TrendArticle)
class TrendArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'published_date', 'scraped_at')
    list_filter = ('source', 'published_date', 'scraped_at')
    search_fields = ('title', 'snippet', 'tags')
    readonly_fields = ('scraped_at', 'updated_at')
    ordering = ('-published_date',)
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'url', 'snippet', 'full_text', 'tags')
        }),
        ('Metadata', {
            'fields': ('source', 'published_date')
        }),
        ('Timestamps', {
            'fields': ('scraped_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ScraperJob)
class ScraperJobAdmin(admin.ModelAdmin):
    list_display = ('source', 'status', 'articles_scraped', 'started_at', 'completed_at')
    list_filter = ('status', 'source', 'created_at')
    readonly_fields = ('created_at', 'started_at', 'completed_at')
    ordering = ('-created_at',)