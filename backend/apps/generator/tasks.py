"""
Celery tasks for asynchronous content generation
"""
import logging
from celery import shared_task
from typing import Dict, List
from apps.ingest.models import UploadedFile, GeneratedContent
from apps.trends.vectorstore import get_trend_snippets
from django.contrib.auth import get_user_model
from . import ai_wrapper

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='generator.generate_content_async', time_limit=600, soft_time_limit=540)
def generate_content_async(self, uploaded_file_id: int, platforms: List[str], trend_count: int = 5, user_id: int = None):
    """
    1. Extracts topic
    2. Fetches trends
    3. Fetches User Brand Voice
    4. Generates content via Multi-Agent AI
    5. SAVES result to database
    """
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Loading file...'})
        
        uploaded_file = UploadedFile.objects.get(id=uploaded_file_id)
        topic = uploaded_file.detected_topic or "marketing trends"
        
        # --- NEW: Fetch User & Brand Voice ---
        User = get_user_model()
        user = None
        brand_voice = ""
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                # Check if profile exists and has brand voice
                if hasattr(user, 'profile') and user.profile.brand_voice:
                    brand_voice = user.profile.brand_voice
                    logger.info(f"Applying Brand Voice for user {user.username}")
            except User.DoesNotExist:
                logger.warning(f"User ID {user_id} not found")

        self.update_state(state='PROCESSING', meta={'status': 'Fetching trends...'})
        trend_snippets = get_trend_snippets(topic, k=trend_count)
        
        self.update_state(state='PROCESSING', meta={'status': 'Generating content with AI Agents...'})
        
        # --- UPDATED: Use generic wrapper and pass brand_voice ---
        content_json = ai_wrapper.generate_content(
            extracted_text=uploaded_file.extracted_text,
            trend_snippets=trend_snippets,
            platforms=platforms,
            brand_voice=brand_voice  # <--- Passing the voice settings
        )
        
        self.update_state(state='PROCESSING', meta={'status': 'Saving to database...'})
        
        # === SAVE TO DATABASE ===
        generated_content = GeneratedContent.objects.create(
            user=user,
            uploaded_file=uploaded_file,
            content_json=content_json,
            model_used=ai_wrapper.AI_PROVIDER, # Dynamic model name
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