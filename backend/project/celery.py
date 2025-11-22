"""
Celery configuration for TrendMaster AI
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('trendmaster')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic Tasks
app.conf.beat_schedule = {
    'scrape-trends-daily': {
        'task': 'apps.trends.tasks.scrape_all_sources',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'rebuild-faiss-index-daily': {
        'task': 'apps.trends.tasks.rebuild_faiss_index',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    # Social media publishing tasks
    'check-due-posts-every-minute': {
        'task': 'apps.social.tasks.check_and_publish_due_posts',
        'schedule': crontab(minute='*'),  # Every minute
    },
    'update-analytics-hourly': {
        'task': 'apps.social.tasks.bulk_update_analytics',
        'schedule': crontab(minute=0, hour='*'),  # Every hour
    },
    # AI recommendations - weekly on Sunday at 1 AM
    'generate-recommendations-weekly': {
        'task': 'apps.social.tasks_recommendations.bulk_generate_recommendations',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),  # Sunday 1 AM
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
