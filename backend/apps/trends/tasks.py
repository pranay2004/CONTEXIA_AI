"""
Celery tasks for trend scraping and index management
"""
from celery import shared_task
from django.utils import timezone
import logging

from .scrapers import get_scraper
from .models import TrendArticle, ScraperJob
from .vectorstore import TrendVectorStore

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def scrape_source(self, source: str, max_pages: int = 3):
    """
    Scrape articles from a single source
    
    Args:
        source: Source name ('sprout_social', 'later', 'social_media_examiner')
        max_pages: Maximum pages to scrape
    """
    # Create job record
    job = ScraperJob.objects.create(
        source=source,
        status='running',
        started_at=timezone.now()
    )
    
    try:
        # Get scraper
        scraper = get_scraper(source)
        
        # Scrape articles
        logger.info(f"Starting scrape for {source}")
        articles_data = scraper.scrape(max_pages=max_pages)
        
        # Save articles to database
        articles_created = 0
        articles_updated = 0
        
        for data in articles_data:
            try:
                # Check if article already exists
                article, created = TrendArticle.objects.update_or_create(
                    url=data['url'],
                    defaults=data
                )
                
                if created:
                    articles_created += 1
                    # Add to vector store
                    vector_store = TrendVectorStore()
                    vector_store.add_article(article)
                else:
                    articles_updated += 1
                
            except Exception as e:
                logger.error(f"Error saving article: {str(e)}")
                continue
        
        # Save vector store
        if articles_created > 0:
            vector_store = TrendVectorStore()
            vector_store.save_index()
        
        # Update job
        job.status = 'completed'
        job.articles_scraped = articles_created
        job.completed_at = timezone.now()
        job.save()
        
        logger.info(f"Scrape complete for {source}: {articles_created} new, {articles_updated} updated")
        
        return {
            'source': source,
            'articles_created': articles_created,
            'articles_updated': articles_updated,
        }
        
    except Exception as e:
        logger.error(f"Error scraping {source}: {str(e)}")
        job.status = 'failed'
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
        raise


@shared_task
def scrape_all_sources(max_pages: int = 3):
    """
    Scrape all sources (scheduled daily)
    """
    sources = ['sprout_social', 'later', 'social_media_examiner']
    
    results = []
    for source in sources:
        try:
            result = scrape_source.delay(source, max_pages)
            results.append({'source': source, 'task_id': result.id})
        except Exception as e:
            logger.error(f"Error starting scrape for {source}: {str(e)}")
            results.append({'source': source, 'error': str(e)})
    
    return results


@shared_task
def rebuild_faiss_index():
    """
    Rebuild FAISS index from database (scheduled daily)
    """
    try:
        logger.info("Starting scheduled FAISS index rebuild")
        vector_store = TrendVectorStore()
        vector_store.rebuild_index()
        logger.info("Scheduled FAISS index rebuild complete")
        return {'status': 'success', 'total_vectors': vector_store.index.ntotal}
    except Exception as e:
        logger.error(f"Error rebuilding FAISS index: {str(e)}")
        raise


@shared_task
def add_article_to_vectorstore(article_id: int):
    """
    Add a single article to vector store
    """
    try:
        article = TrendArticle.objects.get(id=article_id)
        vector_store = TrendVectorStore()
        
        if vector_store.add_article(article):
            vector_store.save_index()
            return {'status': 'success', 'article_id': article_id}
        else:
            return {'status': 'failed', 'article_id': article_id}
            
    except TrendArticle.DoesNotExist:
        logger.error(f"Article {article_id} not found")
        return {'status': 'not_found', 'article_id': article_id}
    except Exception as e:
        logger.error(f"Error adding article to vectorstore: {str(e)}")
        raise
