"""
API Views for Image Editor
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from .image_editor import ImageEditor, PlatformSpecs, FilterPresets

logger = logging.getLogger(__name__)


class ImageEditorViewSet(viewsets.ViewSet):
    """ViewSet for image editing operations"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='optimize')
    def optimize_for_platform(self, request):
        """
        Optimize image for a specific platform
        
        Request body:
        - image_url: str (required)
        - platform: str (required)
        - variant: str (optional, default: 'feed')
        """
        image_url = request.data.get('image_url')
        platform = request.data.get('platform')
        
        if not image_url or not platform:
            return Response(
                {'error': 'image_url and platform are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        variant = request.data.get('variant', 'feed')
        
        try:
            editor = ImageEditor(image_url)
            editor.optimize_for_platform(platform, variant)
            saved_url = editor.save()
            
            return Response({
                'success': True,
                'url': saved_url,
                'dimensions': editor.get_dimensions(),
                'platform': platform,
                'variant': variant,
            })
            
        except Exception as e:
            logger.error(f"Image optimization error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='edit')
    def edit(self, request):
        """
        Apply multiple edits to an image
        
        Request body:
        - image_url: str (required)
        - operations: list of operations
        
        Operations format:
        [
            {"type": "resize", "width": 1200, "height": 630},
            {"type": "brightness", "factor": 1.2},
            {"type": "crop", "left": 0, "top": 0, "right": 1000, "bottom": 1000},
            {"type": "filter", "name": "vibrant"},
            {"type": "text", "text": "Hello", "position": [100, 100]},
            {"type": "watermark", "text": "© Brand"}
        ]
        """
        image_url = request.data.get('image_url')
        operations = request.data.get('operations', [])
        
        if not image_url:
            return Response(
                {'error': 'image_url is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            editor = ImageEditor(image_url)
            
            for op in operations:
                op_type = op.get('type')
                
                if op_type == 'resize':
                    editor.resize(op['width'], op['height'], op.get('maintain_aspect', True))
                
                elif op_type == 'crop':
                    editor.crop(op['left'], op['top'], op['right'], op['bottom'])
                
                elif op_type == 'brightness':
                    editor.adjust_brightness(op['factor'])
                
                elif op_type == 'contrast':
                    editor.adjust_contrast(op['factor'])
                
                elif op_type == 'saturation':
                    editor.adjust_saturation(op['factor'])
                
                elif op_type == 'sharpness':
                    editor.adjust_sharpness(op['factor'])
                
                elif op_type == 'filter':
                    filter_name = op['name']
                    if hasattr(FilterPresets, filter_name):
                        getattr(FilterPresets, filter_name)(editor)
                    else:
                        editor.apply_filter(filter_name)
                
                elif op_type == 'text':
                    editor.add_text(
                        op['text'],
                        tuple(op['position']),
                        op.get('font_size', 48),
                        op.get('color', 'white'),
                    )
                
                elif op_type == 'watermark':
                    editor.add_watermark(
                        op['text'],
                        op.get('position', 'bottom-right'),
                        op.get('opacity', 0.5),
                    )
                
                elif op_type == 'rotate':
                    editor.rotate(op['angle'])
                
                elif op_type == 'flip':
                    editor.flip(op.get('direction', 'horizontal'))
            
            saved_url = editor.save()
            
            return Response({
                'success': True,
                'url': saved_url,
                'dimensions': editor.get_dimensions(),
                'operations_applied': len(operations),
            })
            
        except Exception as e:
            logger.error(f"Image editing error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='platform-specs')
    def platform_specs(self, request):
        """Get platform-specific image specifications"""
        return Response({
            'specs': PlatformSpecs.SPECS
        })
    
    @action(detail=False, methods=['get'], url_path='filters')
    def available_filters(self, request):
        """Get available filter presets"""
        return Response({
            'filters': [
                {'name': 'vibrant', 'description': 'Vibrant, colorful look'},
                {'name': 'muted', 'description': 'Soft, muted colors'},
                {'name': 'dramatic', 'description': 'High contrast, dramatic look'},
                {'name': 'vintage', 'description': 'Vintage, retro look'},
                {'name': 'professional', 'description': 'Clean, professional look'},
                {'name': 'blur', 'description': 'Blur effect'},
                {'name': 'sharpen', 'description': 'Sharpen effect'},
                {'name': 'edge_enhance', 'description': 'Edge enhancement'},
            ]
        })
