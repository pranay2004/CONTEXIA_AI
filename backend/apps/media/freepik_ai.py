"""
Freepik AI Image Generation Module (Third Fallback Provider)
Using Freepik API for AI-powered image generation
"""
import requests
import logging
import time
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_image_with_freepik(prompt: str, num_images: int = 1, style: str = "photo"):
    """
    Generate images using Freepik AI API
    
    Args:
        prompt: Text description of the image to generate
        num_images: Number of images to generate (1-4)
        style: Image style (photo, digital-art, painting, illustration, 3d)
    
    Returns:
        dict: {
            'status': 'success' or 'failed',
            'images': [base64_string, ...],
            'error': error message if failed
        }
    """
    api_key = getattr(settings, 'FREEPIK_API_KEY', 'FPSX4cbadf272cd1c5613a88a513914e2703')
    
    try:
        # Freepik AI API endpoint
        api_url = "https://api.freepik.com/v1/ai/text-to-image"
        
        headers = {
            'x-freepik-api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        all_images = []
        
        # Generate images one by one
        for i in range(min(num_images, 4)):
            try:
                payload = {
                    "prompt": prompt,
                    "styling": {
                        "style": style
                    },
                    "image": {
                        "size": "square_1_1"  # 1024x1024
                    }
                }
                
                # Submit generation request
                response = requests.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Freepik returns image data directly
                    if 'data' in result:
                        data = result['data'][0] if isinstance(result['data'], list) else result['data']
                        
                        # Get image URL
                        image_url = data.get('image', {}).get('url') or data.get('url')
                        
                        if image_url:
                            # Download image and convert to base64
                            img_response = requests.get(image_url, timeout=15)
                            
                            if img_response.status_code == 200:
                                import base64
                                img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                                all_images.append(img_base64)
                                logger.info(f"Successfully generated Freepik image {i+1}/{num_images}")
                        
                        # Rate limiting - wait between requests
                        if i < num_images - 1:
                            time.sleep(1)
                            
                elif response.status_code == 429:
                    logger.warning("Freepik rate limit reached")
                    break
                    
                else:
                    logger.error(f"Freepik API error {response.status_code}: {response.text}")
                    
            except Exception as e:
                logger.error(f"Error generating Freepik image {i+1}: {e}")
                continue
        
        if all_images:
            logger.info(f"Successfully generated {len(all_images)} images with Freepik")
            return {
                'status': 'success',
                'images': all_images
            }
        else:
            return {
                'status': 'failed',
                'error': 'No images generated from Freepik'
            }
            
    except requests.exceptions.Timeout:
        error_msg = "Freepik request timeout"
        logger.error(error_msg)
        return {'status': 'failed', 'error': error_msg}
    
    except Exception as e:
        error_msg = f"Freepik generation failed: {str(e)}"
        logger.error(error_msg)
        return {'status': 'failed', 'error': error_msg}


def generate_collage_images_with_freepik(text_content: str, num_images: int = 4):
    """
    Generate multiple images for collage creation using Freepik
    Creates contextual prompts from text content
    
    Args:
        text_content: Source text to generate images from
        num_images: Number of images to generate (1-4)
    
    Returns:
        dict: {
            'status': 'success' or 'failed',
            'images': [base64_string, ...],
            'error': error message if failed
        }
    """
    try:
        # Extract key themes from text
        text_preview = text_content[:500] if len(text_content) > 500 else text_content
        
        # Create a visual prompt
        prompt = f"""Professional business image representing: {text_preview}. 
        High quality, modern, corporate style, professional photography. 
        Clean composition, no text overlays."""
        
        # Generate images with photo style
        result = generate_image_with_freepik(prompt, num_images=num_images, style="photo")
        
        return result
        
    except Exception as e:
        logger.error(f"Collage generation with Freepik failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }
