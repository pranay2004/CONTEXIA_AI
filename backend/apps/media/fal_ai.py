"""
Fal.ai Image Generation Module (Fallback Provider)
Using Fal.ai API for AI-powered image generation when primary provider fails
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_image_with_fal(prompt: str, num_images: int = 1, size: str = "square_hd"):
    """
    Generate images using Fal.ai API (Flux Pro model)
    
    Args:
        prompt: Text description of the image to generate
        num_images: Number of images to generate (1-4)
        size: Image size preset (square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9)
    
    Returns:
        dict: {
            'status': 'success' or 'failed',
            'images': [base64_string, ...],
            'error': error message if failed
        }
    """
    api_key = getattr(settings, 'FAL_API_KEY', '5d450066-99db-4a1e-9107-ee5032d5b629:15e0ab78d00922abe0118e6eff0c80f1')
    
    try:
        # Fal.ai uses a queue-based system
        # First, submit the generation request
        submit_url = "https://queue.fal.run/fal-ai/flux-pro/v1.1"
        
        headers = {
            'Authorization': f'Key {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Generate multiple images by making separate requests
        all_images = []
        
        for i in range(min(num_images, 4)):
            try:
                payload = {
                    "prompt": prompt,
                    "image_size": size,
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "num_images": 1,
                    "enable_safety_checker": True,
                    "output_format": "png"
                }
                
                # Submit request
                submit_response = requests.post(
                    submit_url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if submit_response.status_code != 200:
                    logger.error(f"Fal.ai submit error {submit_response.status_code}: {submit_response.text}")
                    continue
                
                submit_data = submit_response.json()
                request_id = submit_data.get('request_id')
                
                if not request_id:
                    logger.error("No request_id in Fal.ai response")
                    continue
                
                # Poll for result (synchronous for now)
                status_url = f"https://queue.fal.run/fal-ai/flux-pro/v1.1/requests/{request_id}/status"
                
                import time
                max_attempts = 30  # 30 seconds max
                for attempt in range(max_attempts):
                    status_response = requests.get(status_url, headers=headers, timeout=5)
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        
                        if status_data.get('status') == 'COMPLETED':
                            # Get the result
                            result_url = f"https://queue.fal.run/fal-ai/flux-pro/v1.1/requests/{request_id}"
                            result_response = requests.get(result_url, headers=headers, timeout=5)
                            
                            if result_response.status_code == 200:
                                result_data = result_response.json()
                                
                                # Extract image URL and convert to base64
                                if 'images' in result_data and len(result_data['images']) > 0:
                                    image_url = result_data['images'][0].get('url')
                                    
                                    if image_url:
                                        # Download image and convert to base64
                                        img_response = requests.get(image_url, timeout=15)
                                        if img_response.status_code == 200:
                                            import base64
                                            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
                                            all_images.append(img_base64)
                                            logger.info(f"Successfully generated image {i+1}/{num_images}")
                                            break
                            
                        elif status_data.get('status') == 'FAILED':
                            logger.error(f"Fal.ai generation failed: {status_data.get('error')}")
                            break
                    
                    time.sleep(1)  # Wait 1 second before polling again
                
            except Exception as e:
                logger.error(f"Error generating image {i+1}: {e}")
                continue
        
        if all_images:
            logger.info(f"Successfully generated {len(all_images)} images with Fal.ai")
            return {
                'status': 'success',
                'images': all_images
            }
        else:
            return {
                'status': 'failed',
                'error': 'No images generated'
            }
            
    except requests.exceptions.Timeout:
        error_msg = "Fal.ai request timeout"
        logger.error(error_msg)
        return {'status': 'failed', 'error': error_msg}
    
    except Exception as e:
        error_msg = f"Fal.ai generation failed: {str(e)}"
        logger.error(error_msg)
        return {'status': 'failed', 'error': error_msg}


def generate_collage_images_with_fal(text_content: str, num_images: int = 4):
    """
    Generate multiple images for collage creation using Fal.ai
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
        prompt = f"""Create a professional, modern image that represents: {text_preview}. 
        Style: Clean, corporate, high-quality, professional photography. 
        No text or watermarks."""
        
        # Generate images
        result = generate_image_with_fal(prompt, num_images=num_images, size="square_hd")
        
        return result
        
    except Exception as e:
        logger.error(f"Collage generation with Fal.ai failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }
