"""
Unified AI Image Generation Service
Priority: Nano Banana (Google) -> Freepik -> Fal.ai
"""
import logging
import base64
import uuid
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Import your specific provider modules
# Ensure these files exist in backend/apps/media/
from apps.media.nano_banana import generate_image_with_nano_banana
from apps.media.freepik_ai import generate_image_with_freepik
from apps.media.fal_ai import generate_image_with_fal

logger = logging.getLogger(__name__)

class ImageGenerator:
    """
    Orchestrates image generation across multiple providers with fallback logic.
    """

    def generate_image(self, prompt: str, size="1024x1024", n=1, **kwargs):
        """
        Attempts to generate an image using providers in sequence.
        Returns list of objects: [{'url': '...', 'provider': 'name', ...}]
        """
        
        # 1. Attempt Nano Banana (Primary)
        try:
            logger.info(f"Attempting Nano Banana generation for: {prompt[:30]}...")
            # Map generic size to Nano Banana aspect ratio
            aspect_ratio = "1:1" 
            if size == "1024x1792": aspect_ratio = "9:16"
            elif size == "1792x1024": aspect_ratio = "16:9"

            result = generate_image_with_nano_banana(
                prompt=prompt, 
                aspect_ratio=aspect_ratio, 
                num_images=n
            )
            
            if result['status'] == 'success':
                return self._process_results(result['images'], prompt, 'nano-banana')
            
            logger.warning(f"Nano Banana failed: {result.get('error')}")
            
        except Exception as e:
            logger.error(f"Nano Banana exception: {e}")

        # 2. Fallback to Freepik
        try:
            logger.info("Falling back to Freepik...")
            result = generate_image_with_freepik(prompt, num_images=n)
            
            if result['status'] == 'success':
                return self._process_results(result['images'], prompt, 'freepik')
            
            logger.warning(f"Freepik failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Freepik exception: {e}")

        # 3. Fallback to Fal.ai
        try:
            logger.info("Falling back to Fal.ai...")
            # Map size to Fal.ai format
            fal_size = "square_hd"
            if size == "1024x1792": fal_size = "portrait_16_9"
            elif size == "1792x1024": fal_size = "landscape_16_9"

            result = generate_image_with_fal(prompt, num_images=n, size=fal_size)
            
            if result['status'] == 'success':
                return self._process_results(result['images'], prompt, 'fal-ai')
            
            logger.warning(f"Fal.ai failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Fal.ai exception: {e}")

        # If we reach here, everything failed
        raise Exception("All image generation providers failed. Please check API keys or try again later.")

    def _process_results(self, base64_images, prompt, provider):
        """
        Decodes Base64 images, saves them to storage, and returns URLs.
        """
        results = []
        for b64_str in base64_images:
            try:
                # Clean base64 string if it has header
                if ';base64,' in b64_str:
                    format_str, imgstr = b64_str.split(';base64,')
                    ext = format_str.split('/')[-1]
                else:
                    imgstr = b64_str
                    ext = 'png'

                data = base64.b64decode(imgstr)
                
                # Generate unique filename
                filename = f"generated/{provider}_{uuid.uuid4().hex}.{ext}"
                
                # Save to Django Default Storage (Media folder)
                file_path = default_storage.save(filename, ContentFile(data))
                
                # Generate Full URL
                # NOTE: In local dev, default_storage.url might return a relative path '/media/...'
                # The view will handle making it absolute if needed, or we assume frontend handles root.
                file_url = default_storage.url(file_path)
                
                results.append({
                    'url': file_url,
                    'prompt': prompt,
                    'generator': provider,
                    'original_url': file_url # Frontend expects this key sometimes
                })
                logger.info(f"Saved generated image to {file_url}")
                
            except Exception as e:
                logger.error(f"Failed to save image from {provider}: {e}")
                
        return results

# Convenience function for external calls
def generate_image(prompt: str, **kwargs):
    generator = ImageGenerator()
    return generator.generate_image(prompt, **kwargs)