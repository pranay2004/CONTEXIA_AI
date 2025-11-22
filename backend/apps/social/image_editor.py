"""
Smart Image Editor with Platform-Specific Optimization
"""
import logging
from typing import Dict, Tuple, Optional
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from io import BytesIO
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class PlatformSpecs:
    """Platform-specific image specifications"""
    
    SPECS = {
        'instagram': {
            'square': (1080, 1080),
            'portrait': (1080, 1350),
            'landscape': (1080, 566),
            'story': (1080, 1920),
        },
        'facebook': {
            'feed': (1200, 630),
            'cover': (820, 312),
            'profile': (180, 180),
        },
        'twitter': {
            'feed': (1200, 675),
            'header': (1500, 500),
            'profile': (400, 400),
        },
        'linkedin': {
            'feed': (1200, 627),
            'banner': (1584, 396),
            'profile': (400, 400),
        },
    }
    
    @classmethod
    def get_size(cls, platform: str, variant: str = 'feed') -> Tuple[int, int]:
        """Get recommended size for platform"""
        return cls.SPECS.get(platform, {}).get(variant, (1200, 630))


class ImageEditor:
    """Smart image editor with various transformation capabilities"""
    
    def __init__(self, image_source: str):
        """
        Initialize editor with image
        
        Args:
            image_source: URL or file path to image
        """
        self.image = self._load_image(image_source)
        self.original_image = self.image.copy()
    
    def _load_image(self, source: str) -> Image.Image:
        """Load image from URL or file path"""
        try:
            if source.startswith('http'):
                response = requests.get(source, timeout=30)
                response.raise_for_status()
                return Image.open(BytesIO(response.content))
            else:
                return Image.open(source)
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise
    
    def resize(self, width: int, height: int, maintain_aspect: bool = True) -> 'ImageEditor':
        """Resize image"""
        if maintain_aspect:
            self.image.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            self.image = self.image.resize((width, height), Image.Resampling.LANCZOS)
        return self
    
    def optimize_for_platform(self, platform: str, variant: str = 'feed') -> 'ImageEditor':
        """Optimize image for specific platform"""
        target_size = PlatformSpecs.get_size(platform, variant)
        
        # Calculate crop/resize strategy
        img_ratio = self.image.width / self.image.height
        target_ratio = target_size[0] / target_size[1]
        
        if abs(img_ratio - target_ratio) < 0.1:
            # Close enough, just resize
            self.resize(target_size[0], target_size[1], maintain_aspect=False)
        else:
            # Crop to match ratio, then resize
            self.smart_crop(target_ratio)
            self.resize(target_size[0], target_size[1], maintain_aspect=False)
        
        logger.info(f"Optimized for {platform} {variant}: {target_size}")
        return self
    
    def smart_crop(self, target_ratio: float) -> 'ImageEditor':
        """
        Intelligently crop image to target aspect ratio
        Tries to keep center/focus area
        """
        img_ratio = self.image.width / self.image.height
        
        if img_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(self.image.height * target_ratio)
            left = (self.image.width - new_width) // 2
            self.image = self.image.crop((left, 0, left + new_width, self.image.height))
        else:
            # Image is taller, crop height
            new_height = int(self.image.width / target_ratio)
            top = (self.image.height - new_height) // 2
            self.image = self.image.crop((0, top, self.image.width, top + new_height))
        
        return self
    
    def crop(self, left: int, top: int, right: int, bottom: int) -> 'ImageEditor':
        """Manual crop"""
        self.image = self.image.crop((left, top, right, bottom))
        return self
    
    def adjust_brightness(self, factor: float) -> 'ImageEditor':
        """
        Adjust brightness
        factor: 0.0 = black, 1.0 = original, 2.0 = twice as bright
        """
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(factor)
        return self
    
    def adjust_contrast(self, factor: float) -> 'ImageEditor':
        """
        Adjust contrast
        factor: 0.0 = gray, 1.0 = original, 2.0 = twice contrast
        """
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(factor)
        return self
    
    def adjust_saturation(self, factor: float) -> 'ImageEditor':
        """
        Adjust color saturation
        factor: 0.0 = grayscale, 1.0 = original, 2.0 = twice saturation
        """
        enhancer = ImageEnhance.Color(self.image)
        self.image = enhancer.enhance(factor)
        return self
    
    def adjust_sharpness(self, factor: float) -> 'ImageEditor':
        """
        Adjust sharpness
        factor: 0.0 = blurred, 1.0 = original, 2.0 = twice sharpness
        """
        enhancer = ImageEnhance.Sharpness(self.image)
        self.image = enhancer.enhance(factor)
        return self
    
    def apply_filter(self, filter_name: str) -> 'ImageEditor':
        """Apply predefined filter"""
        filters = {
            'blur': ImageFilter.BLUR,
            'contour': ImageFilter.CONTOUR,
            'detail': ImageFilter.DETAIL,
            'edge_enhance': ImageFilter.EDGE_ENHANCE,
            'emboss': ImageFilter.EMBOSS,
            'sharpen': ImageFilter.SHARPEN,
            'smooth': ImageFilter.SMOOTH,
        }
        
        if filter_name in filters:
            self.image = self.image.filter(filters[filter_name])
        
        return self
    
    def add_text(
        self,
        text: str,
        position: Tuple[int, int],
        font_size: int = 48,
        color: str = 'white',
        stroke_width: int = 2,
        stroke_color: str = 'black',
    ) -> 'ImageEditor':
        """Add text overlay to image"""
        draw = ImageDraw.Draw(self.image)
        
        # Try to use a better font if available
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Draw text with stroke for better readability
        draw.text(
            position,
            text,
            font=font,
            fill=color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color,
        )
        
        return self
    
    def add_watermark(
        self,
        watermark_text: str,
        position: str = 'bottom-right',
        opacity: float = 0.5,
    ) -> 'ImageEditor':
        """Add watermark to image"""
        # Create watermark layer
        watermark = Image.new('RGBA', self.image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Font setup
        font_size = int(self.image.width * 0.03)  # 3% of image width
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate position
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        margin = 20
        positions_map = {
            'bottom-right': (self.image.width - text_width - margin, self.image.height - text_height - margin),
            'bottom-left': (margin, self.image.height - text_height - margin),
            'top-right': (self.image.width - text_width - margin, margin),
            'top-left': (margin, margin),
        }
        
        pos = positions_map.get(position, positions_map['bottom-right'])
        
        # Draw watermark
        alpha = int(255 * opacity)
        draw.text(pos, watermark_text, font=font, fill=(255, 255, 255, alpha))
        
        # Composite watermark onto image
        if self.image.mode != 'RGBA':
            self.image = self.image.convert('RGBA')
        self.image = Image.alpha_composite(self.image, watermark)
        
        return self
    
    def rotate(self, angle: int) -> 'ImageEditor':
        """Rotate image"""
        self.image = self.image.rotate(angle, expand=True)
        return self
    
    def flip(self, direction: str = 'horizontal') -> 'ImageEditor':
        """Flip image"""
        if direction == 'horizontal':
            self.image = self.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            self.image = self.image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return self
    
    def reset(self) -> 'ImageEditor':
        """Reset to original image"""
        self.image = self.original_image.copy()
        return self
    
    def save(self, format: str = 'JPEG', quality: int = 85) -> str:
        """
        Save edited image to storage
        
        Returns:
            URL to saved image
        """
        try:
            # Convert to RGB if saving as JPEG
            if format == 'JPEG' and self.image.mode in ('RGBA', 'LA', 'P'):
                self.image = self.image.convert('RGB')
            
            # Generate filename
            import uuid
            ext = format.lower()
            filename = f"edited/{uuid.uuid4().hex}.{ext}"
            
            # Save to buffer
            buffer = BytesIO()
            self.image.save(buffer, format=format, quality=quality, optimize=True)
            buffer.seek(0)
            
            # Save to storage
            path = default_storage.save(filename, ContentFile(buffer.read()))
            full_url = default_storage.url(path)
            
            logger.info(f"Saved edited image to {path}")
            return full_url
            
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    def get_image_data(self, format: str = 'JPEG', quality: int = 85) -> bytes:
        """Get image as bytes"""
        buffer = BytesIO()
        
        # Convert to RGB if saving as JPEG
        img = self.image
        if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img.save(buffer, format=format, quality=quality, optimize=True)
        return buffer.getvalue()
    
    def get_dimensions(self) -> Tuple[int, int]:
        """Get current image dimensions"""
        return (self.image.width, self.image.height)


# Preset filters
class FilterPresets:
    """Predefined filter combinations"""
    
    @staticmethod
    def vibrant(editor: ImageEditor) -> ImageEditor:
        """Vibrant, colorful look"""
        return editor.adjust_saturation(1.3).adjust_contrast(1.1).adjust_sharpness(1.2)
    
    @staticmethod
    def muted(editor: ImageEditor) -> ImageEditor:
        """Soft, muted colors"""
        return editor.adjust_saturation(0.7).adjust_brightness(1.1).adjust_contrast(0.9)
    
    @staticmethod
    def dramatic(editor: ImageEditor) -> ImageEditor:
        """High contrast, dramatic look"""
        return editor.adjust_contrast(1.3).adjust_saturation(1.1).adjust_brightness(0.9)
    
    @staticmethod
    def vintage(editor: ImageEditor) -> ImageEditor:
        """Vintage, retro look"""
        return editor.adjust_saturation(0.8).adjust_brightness(1.05).adjust_contrast(1.1)
    
    @staticmethod
    def professional(editor: ImageEditor) -> ImageEditor:
        """Clean, professional look"""
        return editor.adjust_sharpness(1.15).adjust_contrast(1.05)


# Convenience function
def edit_image(image_source: str) -> ImageEditor:
    """Create image editor instance"""
    return ImageEditor(image_source)
