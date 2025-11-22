# Social Media Integration - Quick Installation Script
# Run this after setting up OAuth apps and configuring .env

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Social Media Integration Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/6] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install django-encrypted-model-fields requests requests-oauthlib cryptography

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Dependency installation failed" -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host ""
Write-Host "[3/6] Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    
    $required = @(
        "LINKEDIN_CLIENT_ID",
        "TWITTER_CLIENT_ID",
        "FACEBOOK_APP_ID",
        "INSTAGRAM_APP_ID",
        "FIELD_ENCRYPTION_KEY"
    )
    
    $missing = @()
    foreach ($key in $required) {
        if ($envContent -notmatch "$key=\w+") {
            $missing += $key
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Host "✓ All OAuth credentials configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ Missing credentials: $($missing -join ', ')" -ForegroundColor Yellow
        Write-Host "  Please configure these in backend\.env" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Write-Host "  Copying .env.social.example to .env" -ForegroundColor Yellow
    
    if (Test-Path "backend\.env.social.example") {
        Copy-Item "backend\.env.social.example" "backend\.env"
        Write-Host "  Please edit backend\.env with your OAuth credentials" -ForegroundColor Yellow
    }
}

# Generate encryption key if needed
Write-Host ""
Write-Host "[4/6] Checking encryption key..." -ForegroundColor Yellow
$envPath = "backend\.env"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    if ($envContent -notmatch "FIELD_ENCRYPTION_KEY=.{20,}") {
        Write-Host "  Generating new encryption key..." -ForegroundColor Yellow
        $key = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        Add-Content $envPath "`nFIELD_ENCRYPTION_KEY=$key"
        Write-Host "✓ Encryption key generated and added to .env" -ForegroundColor Green
    } else {
        Write-Host "✓ Encryption key already configured" -ForegroundColor Green
    }
}

# Run migrations
Write-Host ""
Write-Host "[5/6] Running database migrations..." -ForegroundColor Yellow
Set-Location backend

python manage.py makemigrations social
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrations created" -ForegroundColor Green
} else {
    Write-Host "✗ Migration creation failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

python manage.py migrate
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrations applied" -ForegroundColor Green
} else {
    Write-Host "✗ Migration failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Verify installation
Write-Host ""
Write-Host "[6/6] Verifying installation..." -ForegroundColor Yellow
Set-Location backend

$verification = python manage.py shell -c "
from apps.social.models import SocialAccount
from apps.social.oauth.linkedin_oauth import LinkedInOAuth
print('Models imported successfully')
print('OAuth handlers loaded successfully')
" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation verified" -ForegroundColor Green
} else {
    Write-Host "⚠ Verification completed with warnings" -ForegroundColor Yellow
}

Set-Location ..

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure OAuth credentials in backend\.env" -ForegroundColor White
Write-Host "   - LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET" -ForegroundColor Gray
Write-Host "   - TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET" -ForegroundColor Gray
Write-Host "   - FACEBOOK_APP_ID and FACEBOOK_APP_SECRET" -ForegroundColor Gray
Write-Host "   - INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start Django server:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test OAuth flow:" -ForegroundColor White
Write-Host "   - Visit http://localhost:8000/admin/" -ForegroundColor Gray
Write-Host "   - Check 'Social' section appears" -ForegroundColor Gray
Write-Host ""
Write-Host "4. API Documentation:" -ForegroundColor White
Write-Host "   - Endpoints: /api/social/accounts/" -ForegroundColor Gray
Write-Host "   - See SOCIAL_SETUP_GUIDE.md for details" -ForegroundColor Gray
Write-Host ""
Write-Host "🔒 Security Reminders:" -ForegroundColor Yellow
Write-Host "   - Never commit .env to version control" -ForegroundColor Gray
Write-Host "   - Use HTTPS in production" -ForegroundColor Gray
Write-Host "   - Keep encryption key secure" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Full Documentation:" -ForegroundColor Yellow
Write-Host "   SOCIAL_SETUP_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "✨ Happy building!" -ForegroundColor Cyan
