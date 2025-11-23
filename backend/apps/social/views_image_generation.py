from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .image_generation import generate_image
import logging

logger = logging.getLogger(__name__)

class ImageGenerationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate images using AI with fallback strategies.
        Payload: { "prompt": "...", "style": "...", "aspect_ratio": "..." }
        """
        prompt = request.data.get('prompt')
        style = request.data.get('style', 'photorealistic')
        aspect_ratio = request.data.get('aspect_ratio', '1:1')
        
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=400)

        # Map simple aspect ratios to pixel dimensions for the generator
        size_map = {
            '1:1': '1024x1024',
            '9:16': '1024x1792',
            '16:9': '1792x1024'
        }
        size = size_map.get(aspect_ratio, '1024x1024')

        # Enhance prompt with style if needed
        full_prompt = f"{prompt}, {style} style, high quality"

        try:
            # Call the unified generator
            images = generate_image(prompt=full_prompt, size=size, n=1)
            
            return Response({
                'status': 'success',
                'images': images, # List of { url, generator, prompt }
                'count': len(images)
            })

        except Exception as e:
            logger.error(f"Image generation view error: {e}")
            return Response({
                'status': 'failed',
                'error': str(e)
            }, status=500)