"""
Photo Processing Service
Provides AI-powered photo editing, collage creation, and platform optimization
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from io import BytesIO
import base64
from typing import List, Dict, Optional, Tuple
import math


class PhotoProcessor:
    """Advanced photo processing with AI-powered enhancements"""
    
    # Platform-specific dimensions
    PLATFORM_SIZES = {
        'x': {
            'single': (1200, 675),  # 16:9
            'card': (800, 418),     # Twitter card
            'post': (1200, 1200),   # Square
        },
        'linkedin': {
            'post': (1200, 627),    # Link preview
            'article': (1200, 628),
            'square': (1200, 1200),
        },
        'instagram': {
            'post': (1080, 1080),   # Square
            'story': (1080, 1920),  # 9:16
            'reel': (1080, 1920),
        },
        'facebook': {
            'post': (1200, 630),
            'story': (1080, 1920),
        }
    }
    
    def __init__(self):
        self.default_font_size = 48
        
    def load_image(self, image_data: bytes) -> Image.Image:
        """Load image from bytes"""
        return Image.open(BytesIO(image_data)).convert('RGBA')
    
    def resize_for_platform(
        self, 
        image: Image.Image, 
        platform: str = 'x',
        format_type: str = 'post'
    ) -> Image.Image:
        """Resize image for specific platform"""
        target_size = self.PLATFORM_SIZES.get(platform, {}).get(format_type, (1200, 675))
        
        # Calculate aspect ratio
        img_ratio = image.width / image.height
        target_ratio = target_size[0] / target_size[1]
        
        if img_ratio > target_ratio:
            # Image is wider, crop width
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            left = (new_width - target_size[0]) // 2
            image = image.crop((left, 0, left + target_size[0], new_height))
        else:
            # Image is taller, crop height
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            top = (new_height - target_size[1]) // 2
            image = image.crop((0, top, new_width, top + target_size[1]))
        
        return image
    
    def apply_filters(
        self,
        image: Image.Image,
        brightness: float = 1.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        sharpness: float = 1.0
    ) -> Image.Image:
        """Apply color and enhancement filters"""
        # Brightness
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        # Contrast
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
        
        # Saturation
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(saturation)
        
        # Sharpness
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(sharpness)
        
        return image
    
    def apply_preset_filter(self, image: Image.Image, preset: str) -> Image.Image:
        """Apply preset filter styles"""
        if preset == 'vivid':
            return self.apply_filters(image, brightness=1.1, contrast=1.2, saturation=1.4)
        elif preset == 'cool':
            img = self.apply_filters(image, brightness=1.05, contrast=1.1, saturation=0.9)
            # Add blue tint
            return self._add_color_overlay(img, (0, 100, 200, 30))
        elif preset == 'warm':
            img = self.apply_filters(image, brightness=1.1, contrast=1.05, saturation=1.2)
            # Add warm tint
            return self._add_color_overlay(img, (255, 150, 50, 30))
        elif preset == 'bw':
            return image.convert('L').convert('RGBA')
        elif preset == 'vintage':
            img = self.apply_filters(image, brightness=0.95, contrast=0.9, saturation=0.8)
            # Add sepia tone
            return self._add_color_overlay(img, (112, 66, 20, 40))
        return image
    
    def _add_color_overlay(self, image: Image.Image, color: Tuple[int, int, int, int]) -> Image.Image:
        """Add color overlay to image"""
        overlay = Image.new('RGBA', image.size, color)
        return Image.alpha_composite(image.convert('RGBA'), overlay)
    
    def add_gradient_overlay(
        self,
        image: Image.Image,
        direction: str = 'bottom',
        color: Tuple[int, int, int] = (0, 0, 0),
        intensity: float = 0.5
    ) -> Image.Image:
        """Add gradient overlay"""
        gradient = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        if direction == 'bottom':
            for y in range(image.height):
                alpha = int(255 * intensity * (y / image.height))
                draw.rectangle([(0, y), (image.width, y + 1)], fill=(*color, alpha))
        elif direction == 'top':
            for y in range(image.height):
                alpha = int(255 * intensity * (1 - y / image.height))
                draw.rectangle([(0, y), (image.width, y + 1)], fill=(*color, alpha))
        
        return Image.alpha_composite(image.convert('RGBA'), gradient)
    
    def add_vignette(self, image: Image.Image, intensity: float = 0.5) -> Image.Image:
        """Add vignette effect"""
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        
        center_x, center_y = image.width // 2, image.height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        for x in range(image.width):
            for y in range(image.height):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                value = int(255 * (1 - (distance / max_radius) * intensity))
                mask.putpixel((x, y), max(0, min(255, value)))
        
        vignette_img = image.convert('RGBA')
        vignette_img.putalpha(mask)
        
        background = Image.new('RGBA', image.size, (0, 0, 0, 255))
        return Image.alpha_composite(background, vignette_img)
    
    def add_text(
        self,
        image: Image.Image,
        text: str,
        position: str = 'center',
        color: Tuple[int, int, int] = (255, 255, 255),
        background: bool = True
    ) -> Image.Image:
        """Add text overlay to image"""
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", self.default_font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate position
        if position == 'center':
            x = (image.width - text_width) // 2
            y = (image.height - text_height) // 2
        elif position == 'top':
            x = (image.width - text_width) // 2
            y = 50
        elif position == 'bottom':
            x = (image.width - text_width) // 2
            y = image.height - text_height - 50
        else:
            x, y = 50, 50
        
        # Add background if requested
        if background:
            padding = 20
            draw.rectangle(
                [(x - padding, y - padding), (x + text_width + padding, y + text_height + padding)],
                fill=(0, 0, 0, 180)
            )
        
        # Draw text
        draw.text((x, y), text, fill=color, font=font)
        
        return image
    
    def create_collage(
        self,
        images: List[Image.Image],
        template: str = 'grid-2x2',
        spacing: int = 10,
        background_color: Tuple[int, int, int] = (255, 255, 255)
    ) -> Image.Image:
        """Create collage from multiple images"""
        if template == 'single' and len(images) >= 1:
            return images[0]
        
        elif template == 'side-by-side' and len(images) >= 2:
            width = images[0].width + images[1].width + spacing
            height = max(images[0].height, images[1].height)
            collage = Image.new('RGB', (width, height), background_color)
            collage.paste(images[0], (0, 0))
            collage.paste(images[1], (images[0].width + spacing, 0))
            return collage
        
        elif template == 'grid-2x2' and len(images) >= 4:
            # Resize all to same size
            size = min(img.size[0] for img in images[:4])
            resized = [img.resize((size, size), Image.Resampling.LANCZOS) for img in images[:4]]
            
            width = size * 2 + spacing
            height = size * 2 + spacing
            collage = Image.new('RGB', (width, height), background_color)
            
            collage.paste(resized[0], (0, 0))
            collage.paste(resized[1], (size + spacing, 0))
            collage.paste(resized[2], (0, size + spacing))
            collage.paste(resized[3], (size + spacing, size + spacing))
            
            return collage
        
        elif template == 'grid-3x3' and len(images) >= 9:
            size = min(img.size[0] for img in images[:9]) // 3
            resized = [img.resize((size, size), Image.Resampling.LANCZOS) for img in images[:9]]
            
            width = size * 3 + spacing * 2
            height = size * 3 + spacing * 2
            collage = Image.new('RGB', (width, height), background_color)
            
            for i, img in enumerate(resized):
                row = i // 3
                col = i % 3
                x = col * (size + spacing)
                y = row * (size + spacing)
                collage.paste(img, (x, y))
            
            return collage
        
        elif template == 'hero' and len(images) >= 4:
            # Large hero image on left, 3 smaller on right
            hero = images[0].resize((800, 800), Image.Resampling.LANCZOS)
            small_size = 260
            smalls = [img.resize((small_size, small_size), Image.Resampling.LANCZOS) for img in images[1:4]]
            
            width = 800 + small_size + spacing * 2
            height = 800
            collage = Image.new('RGB', (width, height), background_color)
            
            collage.paste(hero, (0, 0))
            for i, img in enumerate(smalls):
                y = i * (small_size + spacing)
                collage.paste(img, (800 + spacing, y))
            
            return collage
        
        # Fallback: just return first image
        return images[0] if images else Image.new('RGB', (800, 800), background_color)
    
    def add_frame(self, image: Image.Image, width: int = 20, color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        """Add frame around image"""
        new_size = (image.width + width * 2, image.height + width * 2)
        framed = Image.new('RGB', new_size, color)
        framed.paste(image, (width, width))
        return framed
    
    def to_base64(self, image: Image.Image, format: str = 'PNG') -> str:
        """Convert image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode()
    
    def process_photo(
        self,
        image_data: bytes,
        platform: str = 'x',
        filters: Optional[Dict] = None,
        overlay: Optional[str] = None,
        text: Optional[str] = None
    ) -> Image.Image:
        """Full photo processing pipeline"""
        # Load image
        image = self.load_image(image_data)
        
        # Resize for platform
        image = self.resize_for_platform(image, platform)
        
        # Apply filters
        if filters:
            preset = filters.get('preset')
            if preset:
                image = self.apply_preset_filter(image, preset)
            else:
                image = self.apply_filters(
                    image,
                    brightness=filters.get('brightness', 100) / 100,
                    contrast=filters.get('contrast', 100) / 100,
                    saturation=filters.get('saturation', 100) / 100
                )
        
        # Apply overlay
        if overlay:
            if overlay == 'gradient-top':
                image = self.add_gradient_overlay(image, 'top')
            elif overlay == 'gradient-bottom':
                image = self.add_gradient_overlay(image, 'bottom')
            elif overlay == 'vignette':
                image = self.add_vignette(image)
            elif overlay == 'frame':
                image = self.add_frame(image)
        
        # Add text
        if text:
            image = self.add_text(image, text)
        
        return image
