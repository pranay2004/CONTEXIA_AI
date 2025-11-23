"""
API views for TrendMaster AI
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from django.utils import timezone
from asgiref.sync import sync_to_async
from celery.result import AsyncResult
import logging
import validators
import json
import asyncio

# ✅ Correct Global Imports
from apps.ingest.models import UploadedFile, GeneratedContent
from apps.ingest.extractors import TextExtractor, count_words
from apps.trends.models import TrendArticle
from apps.trends.vectorstore import get_trend_snippets
from apps.generator import ai_wrapper
from apps.generator.openai_wrapper import ContentStreamer
from apps.generator.analytics import UserPatternAnalyzer
from apps.users.models import UserProfile
from apps.media.tasks import generate_quote_card
from apps.media.models import MediaJob

from .serializers import (
    UploadedFileSerializer,
    FileUploadSerializer,
    GeneratedContentSerializer,
    GenerateRequestSerializer,
    TrendArticleSerializer
)

logger = logging.getLogger(__name__)

# --- STREAMING VIEW ---

@api_view(['POST'])
def generate_content_stream(request):
    """
    Streaming endpoint for real-time content generation.
    """
    uploaded_file_id = request.data.get('uploaded_file_id')
    if not uploaded_file_id:
        return Response({'error': 'Missing uploaded_file_id'}, status=400)

    try:
        uploaded_file = UploadedFile.objects.get(id=uploaded_file_id)
        extracted_text = uploaded_file.extracted_text
        topic = uploaded_file.detected_topic or "Marketing"
    except UploadedFile.DoesNotExist:
        return Response({'error': 'File not found'}, status=404)

    trend_snippets = get_trend_snippets(topic, k=3)
    
    visual_task = generate_quote_card.delay(
        text=f"Insights on {topic}", 
        author_handle="@Contexia"
    )

    async def event_stream():
        streamer = ContentStreamer()
        yield f"data: {json.dumps({'type': 'meta', 'visual_job_id': visual_task.id})}\n\n"
        
        async for chunk in streamer.generate_parallel_stream(extracted_text, trend_snippets, topic):
            yield chunk
            
            if "stream_done" in chunk:
                try:
                    data_str = chunk.replace("data: ", "").strip()
                    data_json = json.loads(data_str)
                    final_content = data_json.get('final_db_data')
                    
                    await sync_to_async(save_generated_content)(
                        request.user, uploaded_file, final_content, trend_snippets
                    )
                except Exception as e:
                    logger.error(f"Error saving final content: {e}")

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response

def save_generated_content(user, file, content, trends):
    if not user.is_authenticated:
        return
    GeneratedContent.objects.create(
        user=user,
        uploaded_file=file,
        content_json=content,
        trends_used=[{
                'title': snippet['title'],
                'source': snippet['source'],
                'viral_score': snippet.get('viral_score', 0)
            } for snippet in trends]
    )

# --- HELPER VIEW: TASK STATUS ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_task_status(request, task_id):
    """
    Poll status of a background Celery task (Content Generation or Visual Generation).
    """
    task_result = AsyncResult(task_id)
    
    response = {
        'task_id': task_id,
        'status': task_result.status.lower() if task_result.status else 'pending',
        'result': None
    }

    if task_result.status == 'SUCCESS':
        result_data = task_result.result
        
        if isinstance(result_data, dict) and 'content_id' in result_data:
            response['status'] = 'completed'
            try:
                content_id = result_data['content_id']
                generated_content = GeneratedContent.objects.get(id=content_id)
                response['result'] = {
                    'id': generated_content.id,
                    'content_json': generated_content.content_json,
                    'trends_used': generated_content.trends_used,
                    'created_at': generated_content.created_at.isoformat()
                }
            except GeneratedContent.DoesNotExist:
                response['result'] = result_data
        else:
            response['result'] = result_data
            try:
                job = MediaJob.objects.get(task_id=task_id)
                if job.output_file:
                    response['media_url'] = request.build_absolute_uri(job.output_file.url)
            except MediaJob.DoesNotExist:
                pass
    
    elif task_result.status == 'PENDING':
        response['status'] = 'pending'
        response['message'] = 'Task is queued or starting...'
    
    elif task_result.status == 'PROCESSING':
        response['status'] = 'processing'
        if task_result.info:
            response['progress'] = task_result.info
    
    elif task_result.status == 'FAILURE':
        response['status'] = 'failed'
        response['error'] = str(task_result.result) if task_result.result else 'Unknown error'

    return Response(response)

# --- SYNC VIEW ---

@api_view(['POST'])
def generate_content(request):
    """
    Generate platform-optimized content using AI + RAG (Asynchronous with Celery)
    Only triggers AI image generation if explicitly requested via 'generate_images' flag
    """
    from apps.generator.tasks import generate_content_async
    from apps.media.tasks import generate_ai_images
    
    serializer = GenerateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    
    try:
        uploaded_file = UploadedFile.objects.get(id=data['uploaded_file_id'])
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Start content generation task
        content_task = generate_content_async.delay(
            uploaded_file_id=data['uploaded_file_id'],
            platforms=data.get('platforms', ['linkedin', 'twitter', 'blog']),
            trend_count=data.get('trend_count', 5),
            user_id=user_id
        )
        
        # Only start AI image generation if explicitly requested
        image_task = None
        generate_images = data.get('generate_images', False)
        has_manual_images = data.get('has_images', False)
        
        # Only generate AI images if:
        # 1. User explicitly requested it (generate_images=True)
        # 2. No manual images were provided
        # 3. There's text content to work with
        if generate_images and not has_manual_images and uploaded_file.extracted_text:
            image_task = generate_ai_images.delay(
                text_content=uploaded_file.extracted_text[:2000],  # Use first 2000 chars
                num_images=4,
                user_id=user_id
            )
            logger.info(f"AI image generation task started: {image_task.id}")
        else:
            logger.info(f"Skipping AI image generation - generate_images={generate_images}, has_manual_images={has_manual_images}")
        
        response_data = {
            'task_id': content_task.id,
            'status': 'processing',
            'message': 'Content generation started. Poll /api/jobs/{task_id}/ for status.'
        }
        
        # Include image task ID if started
        if image_task:
            response_data['image_task_id'] = image_task.id
            response_data['message'] += ' AI images are being generated in the background.'
        
        return Response(response_data, status=status.HTTP_202_ACCEPTED)
        
    except UploadedFile.DoesNotExist:
        return Response({'error': 'Uploaded file not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error starting content generation: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- ANALYTICS & DASHBOARD VIEWS ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics(request):
    """
    Get user analytics stats matching the frontend UserStats interface.
    """
    user = request.user
    uploads = UploadedFile.objects.filter(user=user)
    generations = GeneratedContent.objects.filter(user=user)
    
    # Get basic counts
    total_uploads = uploads.count()
    total_generations = generations.count()
    
    # Safe retrieval of scheduled posts
    total_scheduled = 0
    try:
        from apps.social.models import ScheduledPost
        total_scheduled = ScheduledPost.objects.filter(user=user).count()
    except (ImportError, Exception):
        pass

    # Metrics
    time_saved_hours = total_generations * 0.5
    recent = GeneratedContentSerializer(generations.order_by('-created_at')[:5], many=True).data
    
    try:
        company = user.profile.company_name
        voice = user.profile.brand_voice
    except Exception:
        company = ""
        voice = ""
        
    # Return strictly matching keys for frontend interface
    return Response({
        'total_uploads': total_uploads,
        'total_generations': total_generations,
        'total_posts': total_generations, 
        'total_scheduled': total_scheduled,
        'engagement_rate': 0.0, 
        'hours_saved': time_saved_hours,
        'trending_score': 85,
        'recent': recent,
        'brand_profile': {'company': company, 'voice': voice}
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """
    Get merged recent activity log for the dashboard (Uploads + Generations).
    """
    try:
        # 1. Generations
        generations = GeneratedContent.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        # 2. Uploads
        uploads = UploadedFile.objects.filter(
            user=request.user
        ).order_by('-processed_at')[:5]
        
        activity = []
        
        # Helper for "X min ago"
        def _get_time_ago(timestamp):
            if not timestamp: return ""
            now = timezone.now()
            diff = now - timestamp
            if diff.days > 0: return f"{diff.days}d ago"
            elif diff.seconds > 3600: return f"{diff.seconds // 3600}h ago"
            elif diff.seconds > 60: return f"{diff.seconds // 60}m ago"
            else: return "Just now"

        # Format Generations
        for gen in generations:
            platform = "Content"
            if gen.content_json:
                if 'linkedin' in gen.content_json: platform = 'LinkedIn'
                elif 'long_blog' in gen.content_json: platform = 'Blog'
                elif 'youtube' in gen.content_json: platform = 'YouTube'
                
            activity.append({
                'id': f"gen-{gen.id}",
                'description': f"Generated {platform} Content",
                'platform': platform.lower(),
                'status': 'completed',
                'timestamp': gen.created_at,
                'time_ago': _get_time_ago(gen.created_at)
            })
            
        # Format Uploads
        for up in uploads:
            activity.append({
                'id': f"up-{up.id}",
                'description': f"Uploaded {up.original_filename}",
                'platform': 'system',
                'status': 'completed',
                'timestamp': up.processed_at,
                'time_ago': _get_time_ago(up.processed_at)
            })
            
        # Sort combined list by timestamp descending
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response(activity[:10])
        
    except Exception as e:
        logger.error(f"Error fetching recent activity: {e}")
        return Response([], status=status.HTTP_200_OK)

# --- STANDARD VIEWS ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_voice_sample(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']
    try:
        ext = uploaded_file.name.lower().split('.')[-1]
        text_content = TextExtractor.extract_text(
            file_content=uploaded_file.read(),
            file_type=ext
        )
        if len(text_content) < 100:
            return Response({'error': 'File contains insufficient text'}, status=400)

        analyzer = UserPatternAnalyzer(request.user)
        analysis = analyzer.analyze_from_file(text_content)

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.brand_voice = analysis.get('system_instruction', '')
        profile.voice_fingerprint = analysis
        profile.save()

        return Response(analysis)
    except Exception as e:
        logger.error(f"Voice upload failed: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([])  # Allow unauthenticated access
def extract_content(request):
    serializer = FileUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    extracted_text = ""
    file_type = ""
    original_filename = ""
    url = ""
    try:
        if 'file' in data:
            uploaded_file = data['file']
            original_filename = uploaded_file.name
            file_content = uploaded_file.read()
            ext = original_filename.lower().split('.')[-1]
            if ext in ['pdf', 'docx', 'pptx', 'txt']:
                file_type = ext
            else:
                return Response({'error': f'Unsupported file type: {ext}'}, status=status.HTTP_400_BAD_REQUEST)
            extracted_text = TextExtractor.extract_text(file_content=file_content, file_type=file_type)
        elif 'url' in data:
            url = data['url']
            if not validators.url(url):
                return Response({'error': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
            file_type = 'url'
            extracted_text = TextExtractor.extract_text(url=url)
        elif 'text' in data:
            extracted_text = data['text']
            file_type = 'txt'
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            return Response({'error': 'Could not extract text content'}, status=status.HTTP_400_BAD_REQUEST)
        
        word_count = count_words(extracted_text)
        detected_topic = ai_wrapper.extract_topic_from_text(extracted_text)
        
        user = request.user if request.user.is_authenticated else None
        uploaded_file_obj = UploadedFile.objects.create(
            user=user,
            file_type=file_type,
            original_filename=original_filename,
            url=url,
            extracted_text=extracted_text,
            word_count=word_count,
            detected_topic=detected_topic,
            processed_at=timezone.now()
        )
        if 'file' in data:
            uploaded_file_obj.file = data['file']
            uploaded_file_obj.save()
        
        serializer = UploadedFileSerializer(uploaded_file_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error extracting content: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_generated_content(request, content_id):
    try:
        generated_content = GeneratedContent.objects.get(id=content_id, user=request.user)
        serializer = GeneratedContentSerializer(generated_content)
        return Response(serializer.data)
    except GeneratedContent.DoesNotExist:
        return Response({'error': 'Generated content not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_trends(request):
    source = request.query_params.get('source')
    limit = int(request.query_params.get('limit', 20))
    queryset = TrendArticle.objects.all()
    if source:
        queryset = queryset.filter(source=source)
    queryset = queryset[:limit]
    serializer = TrendArticleSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def generate_viral_hooks(request):
    topic = request.data.get('topic', '')
    count = int(request.data.get('count', 5))
    if not topic:
        return Response({'error': 'Topic is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        hooks = ai_wrapper.generate_hooks(topic, count)
        return Response({'hooks': hooks})
    except Exception as e:
        logger.error(f"Error generating hooks: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])  # Allow unauthenticated access
def process_images(request):
    """
    Process up to 4 images: create collage and add professional frames with AI-powered design.
    """
    from apps.media.image_processor import ImageProcessor
    from apps.media.models import ProcessedImage
    
    # Get uploaded images
    image_files = []
    for i in range(1, 5):  # max 4 images
        file_key = f'image_{i}'
        if file_key in request.FILES:
            image_files.append(request.FILES[file_key])
    
    if not image_files:
        return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(image_files) > 4:
        return Response({'error': 'Maximum 4 images allowed'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Get optional content text for AI-powered design
        content_text = request.data.get('content_text', None) or request.POST.get('content_text', None)
        
        # Process images with optional AI-powered design
        collage_file, framed_files = ImageProcessor.create_professional_collage_with_frames(
            image_files, 
            content_text=content_text
        )
        
        # Save to database
        # First, create or get an UploadedFile for reference
        uploaded_file = UploadedFile.objects.create(
            user=user,
            original_filename='image_batch',
            file_type='image',
            extracted_text='',
            word_count=0
        )
        
        # Save collage
        collage = ProcessedImage.objects.create(
            user=user,
            uploaded_file=uploaded_file,
            image_type='collage',
            image_file=collage_file,
            processing_params={'image_count': len(image_files)}
        )
        
        # Save framed images
        framed_images = []
        for idx, framed_file in enumerate(framed_files):
            framed = ProcessedImage.objects.create(
                user=user,
                uploaded_file=uploaded_file,
                image_type='framed',
                image_file=framed_file,
                processing_params={'frame_index': idx, 'frame_style': ['classic', 'modern', 'minimal', 'elegant'][idx % 4]}
            )
            framed_images.append({
                'id': framed.id,
                'url': request.build_absolute_uri(framed.image_file.url),
                'width': framed.width,
                'height': framed.height
            })
        
        return Response({
            'collage': {
                'id': collage.id,
                'url': request.build_absolute_uri(collage.image_file.url),
                'width': collage.width,
                'height': collage.height
            },
            'framed_images': framed_images,
            'uploaded_file_id': uploaded_file.id
        })
        
    except Exception as e:
        logger.error(f"Error processing images: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])  # Allow unauthenticated access
def generate_ai_images(request):
    """
    Generate AI images using Nano Banana API via Celery task
    """
    from apps.media.tasks import generate_ai_images as generate_task
    
    text_content = request.data.get('text_content', '')
    num_images = int(request.data.get('num_images', 4))
    
    if not text_content:
        return Response({'error': 'text_content is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    if num_images < 1 or num_images > 4:
        return Response({'error': 'num_images must be between 1 and 4'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user_id = request.user.id if request.user.is_authenticated else None
        
        # Start Celery task
        task = generate_task.delay(text_content, num_images, user_id)
        
        return Response({
            'status': 'processing',
            'task_id': task.id,
            'message': 'AI image generation started. Use task_id to check status.'
        }, status=status.HTTP_202_ACCEPTED)
        
    except Exception as e:
        logger.error(f"Error starting AI image generation: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def check_image_task_status(request, task_id):
    """
    Check the status of an AI image generation task
    """
    try:
        task_result = AsyncResult(task_id)
        
        if task_result.ready():
            if task_result.successful():
                result = task_result.result
                return Response({
                    'status': 'completed',
                    'result': result
                })
            else:
                return Response({
                    'status': 'failed',
                    'error': str(task_result.result)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'status': 'processing',
                'state': task_result.state
            })
    except Exception as e:
        logger.error(f"Error checking image task status: {e}")
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'ok', 'timestamp': timezone.now().isoformat()})

class TrendArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrendArticle.objects.all()
    serializer_class = TrendArticleSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        return queryset