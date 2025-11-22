"""
API Views for Stock Photo Integration
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from .stock_photos import StockPhotoAggregator

logger = logging.getLogger(__name__)


class StockPhotoViewSet(viewsets.ViewSet):
    """ViewSet for stock photo search and management"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search stock photos across providers
        
        Query params:
        - q: str (required) - search query
        - providers: str (optional) - comma-separated provider names
        - per_page: int (optional, default: 20)
        - page: int (optional, default: 1)
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        providers_param = request.query_params.get('providers')
        providers = providers_param.split(',') if providers_param else None
        
        per_page = int(request.query_params.get('per_page', 20))
        page = int(request.query_params.get('page', 1))
        
        try:
            aggregator = StockPhotoAggregator()
            results = aggregator.search(
                query=query,
                providers=providers,
                per_page=per_page,
                page=page,
            )
            
            return Response(results)
            
        except Exception as e:
            logger.error(f"Stock photo search error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='ai-search')
    def ai_search(self, request):
        """
        AI-enhanced stock photo search
        
        Query params:
        - q: str (required) - search query
        - per_page: int (optional, default: 20)
        """
        query = request.query_params.get('q')
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        per_page = int(request.query_params.get('per_page', 20))
        
        try:
            aggregator = StockPhotoAggregator()
            results = aggregator.ai_enhanced_search(query, per_page)
            
            return Response(results)
            
        except Exception as e:
            logger.error(f"AI stock photo search error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='download')
    def download(self, request):
        """
        Download and save a stock photo
        
        Request body:
        - photo_url: str (required)
        - provider: str (optional, default: unsplash)
        """
        photo_url = request.data.get('photo_url')
        if not photo_url:
            return Response(
                {'error': 'photo_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        provider = request.data.get('provider', 'unsplash')
        
        try:
            aggregator = StockPhotoAggregator()
            saved_url = aggregator.download_photo(photo_url, provider)
            
            return Response({
                'success': True,
                'url': saved_url,
                'original_url': photo_url,
                'provider': provider,
            })
            
        except Exception as e:
            logger.error(f"Stock photo download error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='trending')
    def trending(self, request):
        """
        Get trending/popular photos
        
        Query params:
        - provider: str (optional, default: unsplash)
        - per_page: int (optional, default: 20)
        """
        provider = request.query_params.get('provider', 'unsplash')
        per_page = int(request.query_params.get('per_page', 20))
        
        try:
            aggregator = StockPhotoAggregator()
            results = aggregator.get_trending(provider, per_page)
            
            return Response(results)
            
        except Exception as e:
            logger.error(f"Trending photos error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
