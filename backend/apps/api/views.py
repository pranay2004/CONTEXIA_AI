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
    """
    from apps.generator.tasks import generate_content_async
    
    serializer = GenerateRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    data = serializer.validated_data
    
    try:
        uploaded_file = UploadedFile.objects.get(id=data['uploaded_file_id'])
        user_id = request.user.id if request.user.is_authenticated else None
        
        task = generate_content_async.delay(
            uploaded_file_id=data['uploaded_file_id'],
            platforms=data.get('platforms', ['linkedin', 'twitter', 'blog']),
            trend_count=data.get('trend_count', 5),
            user_id=user_id
        )
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'Content generation started. Poll /api/jobs/{task_id}/ for status.'
        }, status=status.HTTP_202_ACCEPTED)
        
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