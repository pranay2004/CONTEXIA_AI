# AI Image Generation Setup Guide

Your content generation is working, but AI image generation is currently failing due to API credential issues. Here's how to fix it:

## Current Issues:

1. **Nano Banana (Google Imagen)** - 401 Unauthorized
   - Your API key is invalid or expired
   - May require billing account setup

2. **Fal.ai** - 403 Forbidden (Exhausted Balance)
   - Your account has run out of credits
   - Need to top up balance

3. **Freepik** - Not yet tested (likely will work as fallback)

## Solutions:

### Option 1: Fix Existing Providers (Recommended)

#### Nano Banana (Google Imagen 3.0)
1. Go to: https://console.cloud.google.com/
2. Enable "Vertex AI API" or "Imagen API"
3. Set up billing (requires credit card)
4. Create new API key in "APIs & Services" → "Credentials"
5. Update `NANO_BANANA_API_KEY` in `.env`

#### Fal.ai
1. Go to: https://fal.ai/dashboard/billing
2. Top up your balance (starting at $5)
3. Your existing API key will work once balance is added
4. OR: Create new free account and get new API key

#### Freepik (Free Tier Available)
1. Go to: https://www.freepik.com/api/dashboard
2. Sign up for free tier
3. Get API key from dashboard
4. Update `FREEPIK_API_KEY` in `.env`

### Option 2: Use Manual Images Only

You can skip AI image generation completely:
- Just upload 1-4 images when creating content
- The system will still create beautiful collages and frames
- No API costs involved

### Option 3: Add Alternative Providers

Consider adding these free/cheaper alternatives:

**Stable Diffusion XL (via Replicate)**
- Update `REPLICATE_API_TOKEN` in `.env`
- Free tier: $0.0055 per image
- Get token: https://replicate.com/account/api-tokens

## Testing Your Setup:

After updating API keys, restart Celery:
```bash
# Stop current worker (Ctrl+C)
celery -A project worker --loglevel=info --pool=solo
```

Then try generating content again!

## Current Workaround:

The system will continue to work with manual image uploads:
1. Upload your document/text
2. Upload 1-4 images
3. Click "Generate Content"
4. AI will create beautiful frames and collages with your images

The AI-powered design system (smart themes, dynamic colors, etc.) still works with manual images!
