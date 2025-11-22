from django.urls import path
from .views import RegisterView, manage_profile

urlpatterns = [
    path('', RegisterView.as_view(), name='register'),
    path('me/', manage_profile, name='profile'),
]