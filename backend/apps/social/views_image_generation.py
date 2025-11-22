"""
API Views for Image Generation
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import logging

from .image_generation import ImageGenerator

logger = logging.getLogger(__name__)


class ImageGenerationViewSet(viewsets.ViewSet):
    """ViewSet for AI image generation"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """
        Generate images using AI
        
        Request body:
        - prompt: str (required)
        - size: str (optional, default: "1024x1024")
        - quality: str (optional, default: "standard")
        - style: str (optional, default: "vivid")
        - use_dalle: bool (optional, default: true)
        - n: int (optional, default: 1, max: 4)
        - style_preset: str (optional)
        """
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        size = request.data.get('size', '1024x1024')
        quality = request.data.get('quality', 'standard')
        style_param = request.data.get('style', 'vivid')
        use_dalle = request.data.get('use_dalle', True)
        n = min(int(request.data.get('n', 1)), 4)  # Max 4 images
        style_preset = request.data.get('style_preset')
        
        try:
            generator = ImageGenerator()
            
            # Apply style preset if provided
            if style_preset:
                preset_data = generator.apply_style_preset(prompt, style_preset)
                prompt = preset_data['prompt']
                style_param = preset_data['style']
            
            # Generate images
            results = generator.generate_image(
                prompt=prompt,
                size=size,
                quality=quality,
                style=style_param,
                use_dalle=use_dalle,
                n=n,
            )
            
            return Response({
                'success': True,
                'images': results,
                'count': len(results),
            })
            
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='variations')
    def variations(self, request):
        """
        Generate variations of an existing image
        
        Request body:
        - image_url: str (required)
        - n: int (optional, default: 3, max: 4)
        """
        image_url = request.data.get('image_url')
        if not image_url:
            return Response(
                {'error': 'Image URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        n = min(int(request.data.get('n', 3)), 4)
        
        try:
            generator = ImageGenerator()
            results = generator.generate_variations(image_url, n)
            
            return Response({
                'success': True,
                'variations': results,
                'count': len(results),
            })
            
        except Exception as e:
            logger.error(f"Variation generation error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='presets')
    def style_presets(self, request):
        """Get available style presets"""
        generator = ImageGenerator()
        presets = generator.get_style_presets()
        
        return Response({
            'presets': presets
        })
    
    @action(detail=False, methods=['post'], url_path='optimize-prompt')
    def optimize_prompt(self, request):
        """
        Optimize a prompt for image generation
        
        Request body:
        - prompt: str (required)
        """
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generator = ImageGenerator()
            optimized = generator._optimize_prompt(prompt)
            
            return Response({
                'original_prompt': prompt,
                'optimized_prompt': optimized,
            })
            
        except Exception as e:
            logger.error(f"Prompt optimization error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
