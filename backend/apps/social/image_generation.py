"""
AI Image Generation using DALL-E 3 and Stable Diffusion
"""
import logging
import os
from typing import Dict, List, Optional, Literal
from io import BytesIO
import requests
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import openai

# Optional replicate import for Stable Diffusion (Python 3.14 compatibility issue)
try:
    import replicate
    REPLICATE_AVAILABLE = True
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Replicate not available: {e}")
    REPLICATE_AVAILABLE = False
    replicate = None

logger = logging.getLogger(__name__)

# Initialize APIs
openai.api_key = settings.OPENAI_API_KEY


class ImageGenerator:
    """Generate images using DALL-E 3 and Stable Diffusion"""
    
    DALL_E_COST_PER_IMAGE = 0.04  # $0.04 per 1024x1024 image
    DALL_E_HD_COST_PER_IMAGE = 0.08  # $0.08 per HD image
    
    def __init__(self):
        self.dalle_model = "dall-e-3"
        self.sd_model = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
    
    def generate_image(
        self,
        prompt: str,
        size: Literal["1024x1024", "1024x1792", "1792x1024"] = "1024x1024",
        quality: Literal["standard", "hd"] = "standard",
        style: Literal["vivid", "natural"] = "vivid",
        use_dalle: bool = True,
        n: int = 1,
    ) -> List[Dict[str, str]]:
        """
        Generate images using AI
        
        Args:
            prompt: Text description of desired image
            size: Image dimensions
            quality: Image quality (DALL-E only)
            style: Image style (DALL-E only)
            use_dalle: Use DALL-E 3 (True) or Stable Diffusion (False)
            n: Number of images to generate
            
        Returns:
            List of generated image data with URLs and metadata
        """
        # Optimize prompt
        optimized_prompt = self._optimize_prompt(prompt)
        
        if use_dalle:
            return self._generate_with_dalle(optimized_prompt, size, quality, style, n)
        else:
            return self._generate_with_stable_diffusion(optimized_prompt, size, n)
    
    def _optimize_prompt(self, prompt: str) -> str:
        """
        Use GPT-4o-mini to optimize image generation prompt
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at writing prompts for image generation AI. Enhance the user's prompt to be more detailed, specific, and effective for generating high-quality images. Keep it under 400 characters."
                    },
                    {
                        "role": "user",
                        "content": f"Optimize this image prompt: {prompt}"
                    }
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            optimized = response.choices[0].message.content.strip()
            logger.info(f"Prompt optimized from '{prompt}' to '{optimized}'")
            return optimized
            
        except Exception as e:
            logger.warning(f"Prompt optimization failed, using original: {e}")
            return prompt
    
    def _generate_with_dalle(
        self,
        prompt: str,
        size: str,
        quality: str,
        style: str,
        n: int,
    ) -> List[Dict[str, str]]:
        """Generate images using DALL-E 3"""
        try:
            response = openai.Image.create(
                model=self.dalle_model,
                prompt=prompt,
                n=n,
                size=size,
                quality=quality,
                style=style,
            )
            
            results = []
            cost_per_image = self.DALL_E_HD_COST_PER_IMAGE if quality == "hd" else self.DALL_E_COST_PER_IMAGE
            
            for image_data in response.data:
                # Download and save image
                image_url = image_data.url
                saved_path = self._download_and_save_image(image_url, "dalle")
                
                results.append({
                    'url': saved_path,
                    'original_url': image_url,
                    'prompt': prompt,
                    'generator': 'dalle-3',
                    'size': size,
                    'quality': quality,
                    'style': style,
                    'cost': cost_per_image,
                    'revised_prompt': getattr(image_data, 'revised_prompt', prompt),
                })
            
            total_cost = cost_per_image * n
            logger.info(f"Generated {n} images with DALL-E 3 (${total_cost:.2f})")
            
            return results
            
        except Exception as e:
            logger.error(f"DALL-E generation failed: {e}")
            # Fallback to Stable Diffusion
            logger.info("Falling back to Stable Diffusion...")
            return self._generate_with_stable_diffusion(prompt, size, n)
    
    def _generate_with_stable_diffusion(
        self,
        prompt: str,
        size: str,
        n: int,
    ) -> List[Dict[str, str]]:
        """Generate images using Stable Diffusion XL via Replicate"""
        if not REPLICATE_AVAILABLE:
            raise Exception("Stable Diffusion not available: Replicate package not compatible with Python 3.14. Please use DALL-E instead.")
        
        try:
            # Parse size
            width, height = map(int, size.split('x'))
            
            results = []
            
            for i in range(n):
                output = replicate.run(
                    self.sd_model,
                    input={
                        "prompt": prompt,
                        "width": width,
                        "height": height,
                        "num_outputs": 1,
                        "scheduler": "K_EULER",
                        "num_inference_steps": 50,
                        "guidance_scale": 7.5,
                        "prompt_strength": 0.8,
                    }
                )
                
                # output is a list of URLs
                for image_url in output:
                    saved_path = self._download_and_save_image(image_url, "stable_diffusion")
                    
                    results.append({
                        'url': saved_path,
                        'original_url': image_url,
                        'prompt': prompt,
                        'generator': 'stable-diffusion-xl',
                        'size': size,
                        'quality': 'standard',
                        'style': 'natural',
                        'cost': 0.0,  # Free via Replicate (or low cost depending on plan)
                        'revised_prompt': prompt,
                    })
            
            logger.info(f"Generated {n} images with Stable Diffusion XL")
            
            return results
            
        except Exception as e:
            logger.error(f"Stable Diffusion generation failed: {e}")
            raise Exception(f"Image generation failed: {str(e)}")
    
    def _download_and_save_image(self, url: str, prefix: str) -> str:
        """
        Download image from URL and save to media storage
        
        Returns:
            str: Path to saved image
        """
        try:
            # Download image
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Open with PIL
            img = Image.open(BytesIO(response.content))
            
            # Generate filename
            import uuid
            filename = f"generated/{prefix}_{uuid.uuid4().hex}.png"
            
            # Save to storage
            buffer = BytesIO()
            img.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)
            
            path = default_storage.save(filename, ContentFile(buffer.read()))
            
            # Get full URL
            full_url = default_storage.url(path)
            
            logger.info(f"Saved generated image to {path}")
            
            return full_url
            
        except Exception as e:
            logger.error(f"Failed to download/save image: {e}")
            # Return original URL as fallback
            return url
    
    def generate_variations(
        self,
        image_url: str,
        n: int = 3,
    ) -> List[Dict[str, str]]:
        """
        Generate variations of an existing image (DALL-E only)
        
        Args:
            image_url: URL of source image
            n: Number of variations
            
        Returns:
            List of variation image data
        """
        try:
            # Download source image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # DALL-E variations API
            image_file = BytesIO(response.content)
            image_file.name = "image.png"
            
            dalle_response = openai.Image.create_variation(
                image=image_file,
                n=n,
                size="1024x1024",
            )
            
            results = []
            for image_data in dalle_response.data:
                saved_path = self._download_and_save_image(image_data.url, "dalle_variation")
                
                results.append({
                    'url': saved_path,
                    'original_url': image_data.url,
                    'prompt': 'Variation of source image',
                    'generator': 'dalle-3-variation',
                    'size': '1024x1024',
                    'cost': self.DALL_E_COST_PER_IMAGE,
                })
            
            logger.info(f"Generated {n} image variations")
            
            return results
            
        except Exception as e:
            logger.error(f"Variation generation failed: {e}")
            raise Exception(f"Variation generation failed: {str(e)}")
    
    def get_style_presets(self) -> Dict[str, Dict[str, str]]:
        """Get predefined style presets for image generation"""
        return {
            'photorealistic': {
                'name': 'Photorealistic',
                'prompt_suffix': ', photorealistic, ultra detailed, 8k resolution, professional photography',
                'style': 'natural',
            },
            'digital_art': {
                'name': 'Digital Art',
                'prompt_suffix': ', digital art, highly detailed, artstation, concept art, smooth, sharp focus',
                'style': 'vivid',
            },
            'illustration': {
                'name': 'Illustration',
                'prompt_suffix': ', illustration, colorful, vibrant, detailed, professional',
                'style': 'vivid',
            },
            '3d_render': {
                'name': '3D Render',
                'prompt_suffix': ', 3D render, octane render, highly detailed, volumetric lighting',
                'style': 'vivid',
            },
            'watercolor': {
                'name': 'Watercolor',
                'prompt_suffix': ', watercolor painting, soft colors, artistic, beautiful',
                'style': 'natural',
            },
            'anime': {
                'name': 'Anime',
                'prompt_suffix': ', anime style, manga, detailed, vibrant colors',
                'style': 'vivid',
            },
            'minimalist': {
                'name': 'Minimalist',
                'prompt_suffix': ', minimalist, clean design, simple, elegant',
                'style': 'natural',
            },
            'vintage': {
                'name': 'Vintage',
                'prompt_suffix': ', vintage style, retro, nostalgic, film grain',
                'style': 'natural',
            },
        }
    
    def apply_style_preset(self, prompt: str, preset_key: str) -> Dict[str, str]:
        """
        Apply a style preset to a prompt
        
        Returns:
            Dict with enhanced prompt and recommended settings
        """
        presets = self.get_style_presets()
        
        if preset_key not in presets:
            preset_key = 'photorealistic'
        
        preset = presets[preset_key]
        
        return {
            'prompt': prompt + preset['prompt_suffix'],
            'style': preset['style'],
            'preset_name': preset['name'],
        }


# Convenience functions
def generate_image(prompt: str, **kwargs) -> List[Dict[str, str]]:
    """Generate images using default generator"""
    generator = ImageGenerator()
    return generator.generate_image(prompt, **kwargs)


def generate_variations(image_url: str, n: int = 3) -> List[Dict[str, str]]:
    """Generate variations of an image"""
    generator = ImageGenerator()
    return generator.generate_variations(image_url, n)
