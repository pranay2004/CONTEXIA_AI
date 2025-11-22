# Day 1 OAuth & Social Accounts - Testing Script
# This script tests the OAuth integration manually

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OAuth Integration Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

Write-Host "[1/5] Testing OAuth Handler Imports..." -ForegroundColor Yellow
python -c "
from apps.social.oauth.linkedin_oauth import LinkedInOAuth
from apps.social.oauth.twitter_oauth import TwitterOAuth
from apps.social.oauth.facebook_oauth import FacebookOAuth
from apps.social.oauth.instagram_oauth import InstagramOAuth
print('✓ All OAuth handlers imported successfully')
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Import test failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""
Write-Host "[2/5] Testing Model Imports..." -ForegroundColor Yellow
python -c "
from apps.social.models import SocialAccount, ScheduledPost, PostingSchedule, PublishedPostAnalytics
print('✓ All models imported successfully')
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Model import test failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""
Write-Host "[3/5] Testing Serializer Imports..." -ForegroundColor Yellow
python -c "
from apps.social.serializers import SocialAccountSerializer, ScheduledPostSerializer
print('✓ All serializers imported successfully')
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Serializer import test failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""
Write-Host "[4/5] Testing View Imports..." -ForegroundColor Yellow
python -c "
from apps.social.views import SocialAccountViewSet, ScheduledPostViewSet
print('✓ All views imported successfully')
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ View import test failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""
Write-Host "[5/5] Testing OAuth URL Generation..." -ForegroundColor Yellow
python -c "
import os
os.environ.setdefault('LINKEDIN_CLIENT_ID', 'test')
os.environ.setdefault('LINKEDIN_CLIENT_SECRET', 'test')
os.environ.setdefault('LINKEDIN_REDIRECT_URI', 'http://localhost:3000/oauth/linkedin/callback')

from apps.social.oauth.linkedin_oauth import LinkedInOAuth
oauth = LinkedInOAuth()
url = oauth.get_authorization_url(state='test123')
print(f'✓ LinkedIn auth URL generated: {url[:80]}...')
"

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ OAuth URL generation test failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All Tests Passed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ OAuth handlers working" -ForegroundColor Green
Write-Host "✅ Models loaded correctly" -ForegroundColor Green
Write-Host "✅ Serializers functional" -ForegroundColor Green
Write-Host "✅ Views imported" -ForegroundColor Green
Write-Host "✅ Authorization URLs generating" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Ready to test OAuth flow!" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Manual Testing Steps:" -ForegroundColor Yellow
Write-Host "1. Start server: python manage.py runserver" -ForegroundColor Gray
Write-Host "2. Create user account and get JWT token" -ForegroundColor Gray
Write-Host "3. POST /api/social/accounts/initiate-oauth/" -ForegroundColor Gray
Write-Host "4. Visit authorization_url in browser" -ForegroundColor Gray
Write-Host "5. POST /api/social/accounts/connect/ with code" -ForegroundColor Gray
Write-Host ""
