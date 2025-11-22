"""
Photo Processing API Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import json
import uuid

from .photo_processor import PhotoProcessor


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_photo(request):
    """
    Process a single photo with filters and effects
    
    Request body:
    - photo: image file
    - platform: x, linkedin, instagram, facebook
    - filters: {brightness, contrast, saturation, preset}
    - overlay: gradient-top, gradient-bottom, vignette, frame, none
    - text: optional text to add
    """
    try:
        photo = request.FILES.get('photo')
        if not photo:
            return Response(
                {'error': 'No photo provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        platform = request.POST.get('platform', 'x')
        overlay = request.POST.get('overlay', None)
        text = request.POST.get('text', None)
        
        # Parse filters
        filters = {}
        if request.POST.get('filters'):
            try:
                filters = json.loads(request.POST.get('filters'))
            except json.JSONDecodeError:
                pass
        
        # Process photo
        processor = PhotoProcessor()
        image_data = photo.read()
        processed_image = processor.process_photo(
            image_data,
            platform=platform,
            filters=filters,
            overlay=overlay,
            text=text
        )
        
        # Save processed image
        output = BytesIO()
        processed_image.save(output, format='PNG', quality=95)
        output.seek(0)
        
        # Generate unique filename
        filename = f"processed_{uuid.uuid4().hex}.png"
        file_path = default_storage.save(f"processed_photos/{filename}", ContentFile(output.read()))
        file_url = default_storage.url(file_path)
        
        return Response({
            'success': True,
            'url': file_url,
            'filename': filename,
            'platform': platform,
            'size': processed_image.size
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_collage(request):
    """
    Create a collage from multiple photos
    
    Request body:
    - photos: list of image files
    - template: single, side-by-side, grid-2x2, grid-3x3, story, hero
    - spacing: spacing between images (default: 10)
    - filters: optional filters to apply to all images
    """
    try:
        photos = request.FILES.getlist('photos')
        if not photos:
            return Response(
                {'error': 'No photos provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = request.POST.get('template', 'grid-2x2')
        spacing = int(request.POST.get('spacing', 10))
        platform = request.POST.get('platform', 'x')
        
        # Parse filters
        filters = {}
        if request.POST.get('filters'):
            try:
                filters = json.loads(request.POST.get('filters'))
            except json.JSONDecodeError:
                pass
        
        # Load and process images
        processor = PhotoProcessor()
        images = []
        
        for photo in photos:
            image_data = photo.read()
            image = processor.load_image(image_data)
            
            # Apply filters if provided
            if filters:
                preset = filters.get('preset')
                if preset:
                    image = processor.apply_preset_filter(image, preset)
                else:
                    image = processor.apply_filters(
                        image,
                        brightness=filters.get('brightness', 100) / 100,
                        contrast=filters.get('contrast', 100) / 100,
                        saturation=filters.get('saturation', 100) / 100
                    )
            
            images.append(image)
        
        # Create collage
        collage = processor.create_collage(images, template=template, spacing=spacing)
        
        # Resize for platform
        collage = processor.resize_for_platform(collage, platform)
        
        # Save collage
        output = BytesIO()
        collage.save(output, format='PNG', quality=95)
        output.seek(0)
        
        # Generate unique filename
        filename = f"collage_{uuid.uuid4().hex}.png"
        file_path = default_storage.save(f"collages/{filename}", ContentFile(output.read()))
        file_url = default_storage.url(file_path)
        
        return Response({
            'success': True,
            'url': file_url,
            'filename': filename,
            'template': template,
            'photo_count': len(images),
            'size': collage.size
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_process(request):
    """
    Process multiple photos with same settings
    
    Request body:
    - photos: list of image files
    - platform: target platform
    - filters: filters to apply
    - overlay: overlay to apply
    """
    try:
        photos = request.FILES.getlist('photos')
        if not photos:
            return Response(
                {'error': 'No photos provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        platform = request.POST.get('platform', 'x')
        overlay = request.POST.get('overlay', None)
        
        # Parse filters
        filters = {}
        if request.POST.get('filters'):
            try:
                filters = json.loads(request.POST.get('filters'))
            except json.JSONDecodeError:
                pass
        
        # Process all photos
        processor = PhotoProcessor()
        results = []
        
        for idx, photo in enumerate(photos):
            try:
                image_data = photo.read()
                processed_image = processor.process_photo(
                    image_data,
                    platform=platform,
                    filters=filters,
                    overlay=overlay
                )
                
                # Save processed image
                output = BytesIO()
                processed_image.save(output, format='PNG', quality=95)
                output.seek(0)
                
                filename = f"batch_{uuid.uuid4().hex}.png"
                file_path = default_storage.save(f"processed_photos/{filename}", ContentFile(output.read()))
                file_url = default_storage.url(file_path)
                
                results.append({
                    'index': idx,
                    'url': file_url,
                    'filename': filename,
                    'size': processed_image.size
                })
                
            except Exception as e:
                results.append({
                    'index': idx,
                    'error': str(e)
                })
        
        return Response({
            'success': True,
            'processed_count': len([r for r in results if 'url' in r]),
            'results': results
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_templates(request):
    """Get available collage templates"""
    templates = [
        {
            'id': 'single',
            'name': 'Single Photo',
            'photos_needed': 1,
            'aspect_ratio': '16:9',
            'description': 'One large photo'
        },
        {
            'id': 'side-by-side',
            'name': 'Side by Side',
            'photos_needed': 2,
            'aspect_ratio': '2:1',
            'description': 'Two photos next to each other'
        },
        {
            'id': 'grid-2x2',
            'name': '2×2 Grid',
            'photos_needed': 4,
            'aspect_ratio': '1:1',
            'description': 'Four photos in a grid'
        },
        {
            'id': 'grid-3x3',
            'name': '3×3 Grid',
            'photos_needed': 9,
            'aspect_ratio': '1:1',
            'description': 'Nine photos in a grid'
        },
        {
            'id': 'story',
            'name': 'Story Layout',
            'photos_needed': 3,
            'aspect_ratio': '9:16',
            'description': 'Vertical story format'
        },
        {
            'id': 'hero',
            'name': 'Hero + 3',
            'photos_needed': 4,
            'aspect_ratio': '4:3',
            'description': 'One large hero image with 3 smaller'
        }
    ]
    
    return Response(templates)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_filters(request):
    """Get available filter presets"""
    filters = [
        {
            'id': 'none',
            'name': 'Original',
            'description': 'No filters applied'
        },
        {
            'id': 'vivid',
            'name': 'Vivid',
            'description': 'Boost colors and contrast'
        },
        {
            'id': 'cool',
            'name': 'Cool',
            'description': 'Blue tint with reduced saturation'
        },
        {
            'id': 'warm',
            'name': 'Warm',
            'description': 'Warm tones with enhanced brightness'
        },
        {
            'id': 'bw',
            'name': 'Black & White',
            'description': 'Classic monochrome'
        },
        {
            'id': 'vintage',
            'name': 'Vintage',
            'description': 'Sepia tones with reduced contrast'
        }
    ]
    
    return Response(filters)
