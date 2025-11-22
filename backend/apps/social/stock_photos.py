"""
Stock Photo Integration with Unsplash, Pexels, and Pixabay
"""
import logging
import requests
from typing import Dict, List, Optional
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import openai

logger = logging.getLogger(__name__)

# Initialize OpenAI for AI-powered search
openai.api_key = settings.OPENAI_API_KEY


class StockPhotoProvider:
    """Base class for stock photo providers"""
    
    def search(self, query: str, per_page: int = 20, page: int = 1) -> Dict:
        """Search for photos"""
        raise NotImplementedError
    
    def download_photo(self, photo_url: str) -> str:
        """Download and save photo to storage"""
        try:
            response = requests.get(photo_url, timeout=30)
            response.raise_for_status()
            
            # Generate filename
            import uuid
            filename = f"stock_photos/{uuid.uuid4().hex}.jpg"
            
            # Optimize image
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Optimize size (max 2000px on longest side)
            max_size = 2000
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save optimized image
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            path = default_storage.save(filename, ContentFile(buffer.read()))
            full_url = default_storage.url(path)
            
            logger.info(f"Downloaded and optimized stock photo to {path}")
            return full_url
            
        except Exception as e:
            logger.error(f"Failed to download photo: {e}")
            return photo_url


class UnsplashProvider(StockPhotoProvider):
    """Unsplash stock photo provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', None)
        self.base_url = 'https://api.unsplash.com'
    
    def search(self, query: str, per_page: int = 20, page: int = 1) -> Dict:
        """Search Unsplash photos"""
        if not self.api_key:
            logger.warning("Unsplash API key not configured")
            return {'results': [], 'total': 0, 'provider': 'unsplash'}
        
        try:
            response = requests.get(
                f'{self.base_url}/search/photos',
                params={
                    'query': query,
                    'per_page': per_page,
                    'page': page,
                    'orientation': 'landscape',
                },
                headers={'Authorization': f'Client-ID {self.api_key}'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get('results', []):
                results.append({
                    'id': photo['id'],
                    'url': photo['urls']['regular'],
                    'thumbnail': photo['urls']['thumb'],
                    'download_url': photo['urls']['full'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'photographer': photo['user']['name'],
                    'photographer_url': photo['user']['links']['html'],
                    'description': photo.get('alt_description', ''),
                    'provider': 'unsplash',
                    'attribution_required': True,
                })
            
            return {
                'results': results,
                'total': data.get('total', 0),
                'provider': 'unsplash',
            }
            
        except Exception as e:
            logger.error(f"Unsplash API error: {e}")
            return {'results': [], 'total': 0, 'provider': 'unsplash'}


class PexelsProvider(StockPhotoProvider):
    """Pexels stock photo provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'PEXELS_API_KEY', None)
        self.base_url = 'https://api.pexels.com/v1'
    
    def search(self, query: str, per_page: int = 20, page: int = 1) -> Dict:
        """Search Pexels photos"""
        if not self.api_key:
            logger.warning("Pexels API key not configured")
            return {'results': [], 'total': 0, 'provider': 'pexels'}
        
        try:
            response = requests.get(
                f'{self.base_url}/search',
                params={
                    'query': query,
                    'per_page': per_page,
                    'page': page,
                    'orientation': 'landscape',
                },
                headers={'Authorization': self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get('photos', []):
                results.append({
                    'id': photo['id'],
                    'url': photo['src']['large'],
                    'thumbnail': photo['src']['small'],
                    'download_url': photo['src']['original'],
                    'width': photo['width'],
                    'height': photo['height'],
                    'photographer': photo['photographer'],
                    'photographer_url': photo['photographer_url'],
                    'description': photo.get('alt', ''),
                    'provider': 'pexels',
                    'attribution_required': True,
                })
            
            return {
                'results': results,
                'total': data.get('total_results', 0),
                'provider': 'pexels',
            }
            
        except Exception as e:
            logger.error(f"Pexels API error: {e}")
            return {'results': [], 'total': 0, 'provider': 'pexels'}


class PixabayProvider(StockPhotoProvider):
    """Pixabay stock photo provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'PIXABAY_API_KEY', None)
        self.base_url = 'https://pixabay.com/api/'
    
    def search(self, query: str, per_page: int = 20, page: int = 1) -> Dict:
        """Search Pixabay photos"""
        if not self.api_key:
            logger.warning("Pixabay API key not configured")
            return {'results': [], 'total': 0, 'provider': 'pixabay'}
        
        try:
            response = requests.get(
                self.base_url,
                params={
                    'key': self.api_key,
                    'q': query,
                    'image_type': 'photo',
                    'per_page': per_page,
                    'page': page,
                    'orientation': 'horizontal',
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get('hits', []):
                results.append({
                    'id': photo['id'],
                    'url': photo['largeImageURL'],
                    'thumbnail': photo['previewURL'],
                    'download_url': photo['largeImageURL'],
                    'width': photo['imageWidth'],
                    'height': photo['imageHeight'],
                    'photographer': photo['user'],
                    'photographer_url': f"https://pixabay.com/users/{photo['user']}-{photo['user_id']}/",
                    'description': photo.get('tags', ''),
                    'provider': 'pixabay',
                    'attribution_required': False,
                })
            
            return {
                'results': results,
                'total': data.get('totalHits', 0),
                'provider': 'pixabay',
            }
            
        except Exception as e:
            logger.error(f"Pixabay API error: {e}")
            return {'results': [], 'total': 0, 'provider': 'pixabay'}


class StockPhotoAggregator:
    """Aggregate results from multiple stock photo providers"""
    
    def __init__(self):
        self.providers = {
            'unsplash': UnsplashProvider(),
            'pexels': PexelsProvider(),
            'pixabay': PixabayProvider(),
        }
    
    def search(
        self,
        query: str,
        providers: Optional[List[str]] = None,
        per_page: int = 20,
        page: int = 1,
    ) -> Dict:
        """
        Search across multiple providers
        
        Args:
            query: Search query
            providers: List of provider names (default: all)
            per_page: Results per provider
            page: Page number
            
        Returns:
            Aggregated results from all providers
        """
        if providers is None:
            providers = list(self.providers.keys())
        
        all_results = []
        total = 0
        
        for provider_name in providers:
            if provider_name not in self.providers:
                continue
            
            provider = self.providers[provider_name]
            data = provider.search(query, per_page, page)
            
            all_results.extend(data['results'])
            total += data['total']
        
        return {
            'results': all_results,
            'total': total,
            'query': query,
            'providers': providers,
        }
    
    def ai_enhanced_search(self, query: str, per_page: int = 20) -> Dict:
        """
        Use AI to enhance search query and find better matching images
        """
        try:
            # Use GPT-4o-mini to generate better search keywords
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a search query optimizer for stock photo websites. Generate 3-5 highly relevant search keywords/phrases that would find the best stock photos for the user's request. Return only the keywords, comma-separated."
                    },
                    {
                        "role": "user",
                        "content": f"Find stock photos for: {query}"
                    }
                ],
                temperature=0.5,
                max_tokens=50,
            )
            
            keywords = response.choices[0].message.content.strip()
            search_terms = [k.strip() for k in keywords.split(',')]
            
            logger.info(f"AI-enhanced search: '{query}' -> {search_terms}")
            
            # Search using first keyword
            results = self.search(search_terms[0], per_page=per_page)
            results['ai_enhanced'] = True
            results['ai_keywords'] = search_terms
            
            return results
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, using original query: {e}")
            results = self.search(query, per_page=per_page)
            results['ai_enhanced'] = False
            return results
    
    def download_photo(self, photo_url: str, provider: str = 'unsplash') -> str:
        """Download and save photo"""
        if provider in self.providers:
            return self.providers[provider].download_photo(photo_url)
        return photo_url
    
    def get_trending(self, provider: str = 'unsplash', per_page: int = 20) -> Dict:
        """Get trending/popular photos"""
        # For simplicity, search for generic popular terms
        trending_queries = ['business', 'technology', 'nature', 'people', 'office']
        import random
        query = random.choice(trending_queries)
        
        return self.search(query, providers=[provider], per_page=per_page)


# Convenience functions
def search_stock_photos(query: str, **kwargs) -> Dict:
    """Search stock photos across all providers"""
    aggregator = StockPhotoAggregator()
    return aggregator.search(query, **kwargs)


def ai_search_stock_photos(query: str, **kwargs) -> Dict:
    """AI-enhanced stock photo search"""
    aggregator = StockPhotoAggregator()
    return aggregator.ai_enhanced_search(query, **kwargs)


def download_stock_photo(photo_url: str, provider: str = 'unsplash') -> str:
    """Download and optimize stock photo"""
    aggregator = StockPhotoAggregator()
    return aggregator.download_photo(photo_url, provider)
