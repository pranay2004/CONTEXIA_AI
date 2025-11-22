# Celery Beat Schedule Configuration
# Add this to your celery.py file

from celery.schedules import crontab

# Celery Beat Schedule
app.conf.beat_schedule = {
    'check-due-posts-every-minute': {
        'task': 'apps.social.tasks.check_and_publish_due_posts',
        'schedule': crontab(minute='*'),  # Every minute
    },
    'update-analytics-hourly': {
        'task': 'apps.social.tasks.bulk_update_analytics',
        'schedule': crontab(minute=0, hour='*'),  # Every hour
    },
}

# Timezone
app.conf.timezone = 'UTC'
