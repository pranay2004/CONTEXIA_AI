"""
Nano Banana AI Image Generation Module
Using Google's Imagen API for AI-powered image generation
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_image_with_nano_banana(prompt: str, negative_prompt: str = "", aspect_ratio: str = "1:1", num_images: int = 1):
    """
    Generate images using Nano Banana (Google Imagen) API
    
    Args:
        prompt: Text description of the image to generate
        negative_prompt: What to avoid in the image
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4)
        num_images: Number of images to generate (1-4)
    
    Returns:
        dict: {
            'status': 'success' or 'failed',
            'images': [base64_string, ...],
            'error': error message if failed
        }
    """
    api_key = getattr(settings, 'NANO_BANANA_API_KEY', '')
    api_url = getattr(settings, 'NANO_BANANA_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict')
    
    try:
        # Prepare request payload
        payload = {
            "instances": [{
                "prompt": prompt,
                "negativePrompt": negative_prompt,
                "aspectRatio": aspect_ratio,
                "numberOfImages": min(num_images, 4),
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_adult"
            }],
            "parameters": {
                "sampleCount": min(num_images, 4)
            }
        }
        
        # Make API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.post(
            f"{api_url}?key={api_key}",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract generated images
            images = []
            if 'predictions' in result:
                for pred in result['predictions']:
                    if 'bytesBase64Encoded' in pred:
                        images.append(pred['bytesBase64Encoded'])
                    elif 'image' in pred:
                        images.append(pred['image'])
            
            if images:
                logger.info(f"Successfully generated {len(images)} images")
                return {
                    'status': 'success',
                    'images': images
                }
            else:
                logger.error("No images in API response")
                return {
                    'status': 'failed',
                    'error': 'No images generated'
                }
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {
                'status': 'failed',
                'error': error_msg
            }
            
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - image generation took too long"
        logger.error(error_msg)
        return {'status': 'failed', 'error': error_msg}
    
    except Exception as e:
        error_msg = f"Image generation failed: {str(e)}"
        logger.error(error_msg)
        return {'status': 'failed', 'error': error_msg}


def generate_collage_images(text_content: str, num_images: int = 4):
    """
    Generate images based on extracted text content for collage creation
    
    Args:
        text_content: Text to analyze and generate images from
        num_images: Number of images to generate (1-4)
    
    Returns:
        dict with status and images list
    """
    # Create a compelling prompt from the content
    prompt = f"Professional, high-quality image representing: {text_content[:500]}"
    
    return generate_image_with_nano_banana(
        prompt=prompt,
        negative_prompt="low quality, blurry, distorted, watermark, text overlay",
        aspect_ratio="1:1",
        num_images=num_images
    )
