"""
Celery tasks for AI-powered recommendations
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_posting_recommendations(social_account_id: int, lookback_days: int = 90):
    """
    Generate AI-powered posting time recommendations
    
    Args:
        social_account_id: SocialAccount ID
        lookback_days: Days of historical data to analyze (default: 90)
    """
    from apps.social.ai_recommendations import generate_recommendations_for_account
    
    try:
        recommendations = generate_recommendations_for_account(social_account_id, lookback_days)
        logger.info(f"Generated {len(recommendations)} recommendations for account {social_account_id}")
        return {
            'account_id': social_account_id,
            'recommendations_count': len(recommendations),
            'recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"Failed to generate recommendations for account {social_account_id}: {e}")
        raise


@shared_task
def bulk_generate_recommendations():
    """
    Periodic task to regenerate recommendations for all active accounts
    Should be run weekly
    """
    from apps.social.models import SocialAccount
    
    active_accounts = SocialAccount.objects.filter(is_active=True)
    
    count = 0
    for account in active_accounts:
        # Queue individual tasks
        generate_posting_recommendations.delay(account.id)
        count += 1
    
    logger.info(f"Queued {count} recommendation generation tasks")
    return f"Queued {count} accounts for recommendation generation"
