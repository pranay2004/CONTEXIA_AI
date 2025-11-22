"""
Celery tasks for asynchronous content generation
"""
import logging
from celery import shared_task
from typing import Dict, List
from apps.ingest.models import UploadedFile, GeneratedContent
from apps.trends.vectorstore import get_trend_snippets
from . import ai_wrapper

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='generator.generate_content_async')
def generate_content_async(self, uploaded_file_id: int, platforms: List[str], trend_count: int = 5, user_id: int = None):
    """
    1. Extracts topic
    2. Fetches trends
    3. Generates content via Multi-Agent AI
    4. SAVES result to database
    """
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Loading file...'})
        
        uploaded_file = UploadedFile.objects.get(id=uploaded_file_id)
        topic = uploaded_file.detected_topic or "marketing trends"
        
        self.update_state(state='PROCESSING', meta={'status': 'Fetching trends...'})
        trend_snippets = get_trend_snippets(topic, k=trend_count)
        
        self.update_state(state='PROCESSING', meta={'status': 'Generating content with AI Agents...'})
        
        # FIX: Call the generic wrapper function, not the OpenAI specific one directly
        content_json = ai_wrapper.generate_content(
            extracted_text=uploaded_file.extracted_text,
            trend_snippets=trend_snippets,
            platforms=platforms
        )
        
        self.update_state(state='PROCESSING', meta={'status': 'Saving to database...'})
        
        # Get User
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id) if user_id else None
        
        # === SAVE TO DATABASE ===
        generated_content = GeneratedContent.objects.create(
            user=user,
            uploaded_file=uploaded_file,
            content_json=content_json,
            model_used="gpt-4o",
            trends_used=[{
                'title': snippet['title'],
                'source': snippet['source']
            } for snippet in trend_snippets[:5]]
        )
        
        return {
            'status': 'completed',
            'content_id': generated_content.id,
            'content': content_json
        }
        
    except UploadedFile.DoesNotExist:
        return {'status': 'failed', 'error': 'Uploaded file not found'}
    except Exception as e:
        logger.error(f"Task failed: {e}", exc_info=True)
        return {'status': 'failed', 'error': str(e)}