from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer
from .models import UserProfile

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def manage_profile(request):
    user = request.user
    
    # FIX: Create profile if it doesn't exist yet
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        user_data = request.data.get('user', {})
        if 'email' in user_data:
            user.email = user_data['email']
            user.save()
            
        profile_data = request.data.get('profile', {})
        profile_serializer = UserProfileSerializer(profile, data=profile_data, partial=True)
        
        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(UserSerializer(user).data)
        
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)