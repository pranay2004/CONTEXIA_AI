"""
Additional API views for user stats and activity
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ingest.models import UploadedFile, GeneratedContent


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """
    Get user statistics for dashboard
    """
    user = request.user
    
    total_uploads = UploadedFile.objects.filter(user=user).count()
    total_posts = GeneratedContent.objects.filter(user=user).count()
    hours_saved = total_posts * 0.25  # 15 minutes per post
    
    return Response({
        'total_uploads': total_uploads,
        'total_posts': total_posts,
        'hours_saved': round(hours_saved, 1)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_activity(request):
    """
    Get user's recent activity for dashboard
    """
    user = request.user
    limit = int(request.GET.get('limit', 10))
    
    activities = []
    
    # Get recent uploads
    recent_uploads = UploadedFile.objects.filter(user=user).order_by('-uploaded_at')[:limit]
    for upload in recent_uploads:
        activities.append({
            'id': upload.id,
            'action': 'uploaded',
            'title': upload.original_filename or upload.url or 'Text content',
            'timestamp': upload.uploaded_at.isoformat(),
            'status': 'completed',
            'formats': 0,
            'score': None
        })
    
    # Get recent generations
    recent_generations = GeneratedContent.objects.filter(user=user).order_by('-created_at')[:limit]
    for gen in recent_generations:
        # Calculate score from trends_used if available
        score = 85  # Default score
        if gen.trends_used and isinstance(gen.trends_used, list) and len(gen.trends_used) > 0:
            # Use average of trend scores if available
            trend_scores = [t.get('score', 85) for t in gen.trends_used if isinstance(t, dict)]
            if trend_scores:
                score = int(sum(trend_scores) / len(trend_scores))
        
        # Extract LinkedIn and Twitter content for quick posting
        linkedin_content = None
        twitter_content = None
        
        if gen.content_json:
            # LinkedIn
            if 'linkedin' in gen.content_json:
                linkedin_data = gen.content_json['linkedin']
                if isinstance(linkedin_data, dict):
                    linkedin_content = {
                        'text': linkedin_data.get('post_text') or linkedin_data.get('text') or '',
                        'hashtags': linkedin_data.get('hashtags', [])
                    }
            
            # Twitter/X
            if 'twitter_thread' in gen.content_json:
                twitter_data = gen.content_json['twitter_thread']
                if isinstance(twitter_data, list) and len(twitter_data) > 0:
                    twitter_content = {
                        'thread': twitter_data,
                        'first_tweet': twitter_data[0] if twitter_data else ''
                    }
            elif 'x_thread' in gen.content_json:
                twitter_data = gen.content_json['x_thread']
                if isinstance(twitter_data, list) and len(twitter_data) > 0:
                    twitter_content = {
                        'thread': twitter_data,
                        'first_tweet': twitter_data[0] if twitter_data else ''
                    }
        
        activities.append({
            'id': f'gen-{gen.id}',
            'action': 'generated',
            'title': gen.uploaded_file.original_filename if gen.uploaded_file else 'Content',
            'timestamp': gen.created_at.isoformat(),
            'status': 'completed',
            'formats': 3,
            'score': score,
            'linkedin_content': linkedin_content,
            'twitter_content': twitter_content
        })
    
    # Sort by timestamp and limit
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:limit]
    
    return Response(activities)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upload_status(request, upload_id):
    """
    Get upload processing status
    """
    try:
        upload = UploadedFile.objects.get(id=upload_id, user=request.user)
        
        return Response({
            'id': upload.id,
            'status': 'completed' if upload.processed_at else 'processing',
            'progress': 100 if upload.processed_at else 50,
            'error': None
        })
    except UploadedFile.DoesNotExist:
        return Response({'error': 'Upload not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_generation_status(request, task_id):
    """
    Get content generation status (mock for now)
    """
    return Response({
        'status': 'completed',
        'progress': 100,
        'result': None,
        'error': None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_uploads(request):
    """
    Get user's uploaded files
    """
    user = request.user
    queryset = UploadedFile.objects.filter(user=user).order_by('-uploaded_at')
    
    limit = int(request.GET.get('limit', 20))
    offset = int(request.GET.get('offset', 0))
    total = queryset.count()
    results = queryset[offset:offset+limit]
    
    data = [{
        'id': upload.id,
        'filename': upload.original_filename or upload.url or 'Text content',
        'status': 'completed' if upload.processed_at else 'processing',
        'created_at': upload.uploaded_at.isoformat()
    } for upload in results]
    
    return Response({'count': total, 'results': data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_posts(request):
    """
    Get user's generated posts
    """
    user = request.user
    queryset = GeneratedContent.objects.filter(user=user).order_by('-created_at')
    
    limit = int(request.GET.get('limit', 20))
    offset = int(request.GET.get('offset', 0))
    total = queryset.count()
    results = queryset[offset:offset+limit]
    
    data = [{
        'id': post.id,
        'platform': 'multiple',
        'content': str(post.content_json)[:100],
        'status': 'generated',
        'created_at': post.created_at.isoformat(),
        'trend_score': post.trend_score or 85
    } for post in results]
    
    return Response({'count': total, 'results': data})
