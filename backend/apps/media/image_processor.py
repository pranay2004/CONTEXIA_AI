"""
Image Processing and Collage Generation
Handles multi-image uploads, creates professional collages with frames
"""
import logging
import io
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import os
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Professional image collage and frame generator"""
    
    # Professional color schemes
    FRAME_COLORS = {
        'classic': '#2C3E50',
        'modern': '#1A1A1A',
        'minimal': '#FFFFFF',
        'elegant': '#8B7355',
        'vibrant': '#4F46E5'
    }
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def create_gradient(width: int, height: int, color1: str, color2: str, direction: str = 'vertical') -> Image.Image:
        """Create a gradient image"""
        base = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(base)
        
        rgb1 = ImageProcessor.hex_to_rgb(color1)
        rgb2 = ImageProcessor.hex_to_rgb(color2)
        
        if direction == 'vertical':
            for i in range(height):
                r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * i / height)
                g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * i / height)
                b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * i / height)
                draw.line([(0, i), (width, i)], fill=(r, g, b))
        else:  # horizontal
            for i in range(width):
                r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * i / width)
                g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * i / width)
                b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * i / width)
                draw.line([(i, 0), (i, height)], fill=(r, g, b))
        
        return base
    
    @staticmethod
    def add_professional_frame(image: Image.Image, frame_width: int = 40, color: str = 'classic', 
                               frame_spec: Optional[Dict] = None) -> Image.Image:
        """
        Add a professional frame to an image with shadow effect and dynamic styling
        
        Args:
            image: PIL Image object
            frame_width: Width of the frame in pixels
            color: Frame color scheme (classic, modern, minimal, elegant, vibrant)
            frame_spec: Optional dict with advanced frame specifications
            
        Returns:
            Image with professional frame
        """
        try:
            # Use frame_spec if provided for AI-generated designs
            if frame_spec:
                frame_color = frame_spec.get('color', '#2C3E50')
                frame_width = frame_spec.get('width', 40)
                gradient_colors = frame_spec.get('gradient', None)
                border_style = frame_spec.get('border_style', 'solid')
            else:
                # Get frame color from predefined schemes
                frame_color = ImageProcessor.FRAME_COLORS.get(color, ImageProcessor.FRAME_COLORS['classic'])
                gradient_colors = None
                border_style = 'solid'
            
            # Calculate new size
            new_width = image.width + (frame_width * 2)
            new_height = image.height + (frame_width * 2)
            
            # Create frame with gradient if specified
            if gradient_colors:
                framed = ImageProcessor.create_gradient(new_width, new_height, 
                                                       gradient_colors[0], gradient_colors[1], 
                                                       'vertical')
            else:
                rgb_color = ImageProcessor.hex_to_rgb(frame_color) if frame_color.startswith('#') else (44, 62, 80)
                framed = Image.new('RGB', (new_width, new_height), rgb_color)
            
            # Add decorative border based on style
            draw = ImageDraw.Draw(framed)
            if border_style == 'double_line':
                # Tech/futuristic double line
                draw.rectangle([5, 5, new_width-5, new_height-5], outline=(100, 200, 255), width=2)
                draw.rectangle([10, 10, new_width-10, new_height-10], outline=(100, 200, 255), width=1)
            elif border_style == 'ornate':
                # Elegant ornate corners
                corner_size = 30
                for corner in [(0, 0), (new_width-corner_size, 0), 
                              (0, new_height-corner_size), (new_width-corner_size, new_height-corner_size)]:
                    draw.rectangle([corner[0], corner[1], corner[0]+corner_size, corner[1]+corner_size], 
                                 outline=(200, 180, 150), width=3)
            
            # Add shadow effect (inner shadow)
            shadow_width = 8
            shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            for i in range(shadow_width):
                alpha = int(100 - (i * 12))
                shadow_draw.rectangle([i, i, image.width-i, image.height-i], 
                                    outline=(0, 0, 0, alpha), width=1)
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=4))
            
            # Paste image onto frame
            framed.paste(image, (frame_width, frame_width))
            
            # Paste shadow
            if shadow.mode == 'RGBA':
                framed.paste(shadow, (frame_width, frame_width), shadow)
            
            return framed
            
        except Exception as e:
            logger.error(f"Frame addition failed: {e}")
            return image
    
    @staticmethod
    def resize_maintain_aspect(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        try:
            ratio = min(max_width / image.width, max_height / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        except Exception as e:
            logger.error(f"Resize failed: {e}")
            return image
    
    @staticmethod
    def create_grid_collage(images: List[Image.Image], spacing: int = 20, bg_color: str = '#F8FAFC',
                           collage_spec: Optional[Dict] = None) -> Image.Image:
        """
        Create a professional grid collage from multiple images with dynamic styling
        
        Args:
            images: List of PIL Image objects (max 4)
            spacing: Spacing between images in pixels
            bg_color: Background color
            collage_spec: Optional dict with advanced collage specifications
            
        Returns:
            Collage image
        """
        try:
            num_images = len(images)
            if num_images == 0:
                raise ValueError("No images provided")
            
            # Use collage_spec if provided
            if collage_spec:
                spacing = collage_spec.get('spacing', 20)
                bg_color = collage_spec.get('background_color', '#F8FAFC')
                border_radius = collage_spec.get('border_radius', 0)
                layout = collage_spec.get('layout', 'balanced')
            else:
                border_radius = 0
                layout = 'balanced'
            
            # Determine grid layout based on layout style
            if layout == 'dynamic':
                # Creative asymmetric layout
                grid_rows, grid_cols = (1, 2) if num_images == 2 else (2, 2)
            elif layout == 'geometric':
                # Tech-inspired perfect grid
                grid_rows, grid_cols = (2, 2) if num_images > 2 else (1, 2)
            else:  # balanced, refined, organic, orderly, energetic, stable
                # Standard layout
                if num_images == 1:
                    grid_rows, grid_cols = 1, 1
                elif num_images == 2:
                    grid_rows, grid_cols = 1, 2
                elif num_images == 3:
                    grid_rows, grid_cols = 2, 2  # 2x2 with one empty
                else:  # 4 images
                    grid_rows, grid_cols = 2, 2
            
            # Calculate cell size (each image will fit in this)
            max_cell_width = 800
            max_cell_height = 800
            
            # Resize all images to fit cells
            resized_images = []
            for img in images:
                resized = ImageProcessor.resize_maintain_aspect(img, max_cell_width, max_cell_height)
                resized_images.append(resized)
            
            # Calculate actual cell dimensions based on resized images
            cell_width = max(img.width for img in resized_images) + spacing
            cell_height = max(img.height for img in resized_images) + spacing
            
            # Calculate canvas size
            canvas_width = grid_cols * cell_width + spacing
            canvas_height = grid_rows * cell_height + spacing
            
            # Create canvas
            collage = Image.new('RGB', (canvas_width, canvas_height), bg_color)
            
            # Place images
            for idx, img in enumerate(resized_images):
                row = idx // grid_cols
                col = idx % grid_cols
                
                # Center image in cell
                x = col * cell_width + spacing + (cell_width - img.width - spacing) // 2
                y = row * cell_height + spacing + (cell_height - img.height - spacing) // 2
                
                collage.paste(img, (x, y))
            
            return collage
            
        except Exception as e:
            logger.error(f"Collage creation failed: {e}")
            # Return first image as fallback
            return images[0] if images else Image.new('RGB', (800, 600), bg_color)
    
    @staticmethod
    def enhance_image_quality(image: Image.Image) -> Image.Image:
        """Apply professional enhancement to image"""
        try:
            # Enhance sharpness slightly
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.1)
            
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.05)
            
            # Enhance color vibrancy
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            
            return image
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            return image
    
    @staticmethod
    def process_uploaded_images(uploaded_files: List[InMemoryUploadedFile], add_frames: bool = True,
                               frame_specs: Optional[List[Dict]] = None) -> List[dict]:
        """
        Process multiple uploaded images with optional AI-generated frame specifications
        
        Args:
            uploaded_files: List of uploaded image files (max 4)
            add_frames: Whether to add professional frames
            frame_specs: Optional list of frame specification dicts for each image
            
        Returns:
            List of dicts with 'image': PIL Image and 'filename': str
        """
        processed_images = []
        
        for i, file in enumerate(uploaded_files[:4]):  # Max 4 images
            try:
                # Open image
                image = Image.open(file)
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Enhance quality
                image = ImageProcessor.enhance_image_quality(image)
                
                # Add frame if requested
                if add_frames:
                    if frame_specs and i < len(frame_specs):
                        # Use AI-generated frame specification
                        image = ImageProcessor.add_professional_frame(image, frame_spec=frame_specs[i])
                    else:
                        # Use default frame styles
                        frame_styles = ['classic', 'modern', 'elegant', 'vibrant']
                        frame_style = frame_styles[i % len(frame_styles)]
                        image = ImageProcessor.add_professional_frame(image, frame_width=40, color=frame_style)
                
                processed_images.append({
                    'image': image,
                    'filename': file.name,
                    'original_size': (image.width, image.height)
                })
                
            except Exception as e:
                logger.error(f"Failed to process image {file.name}: {e}")
                continue
        
        return processed_images
    
    @staticmethod
    def save_image_to_content_file(image: Image.Image, filename: str, format: str = 'PNG', quality: int = 95) -> ContentFile:
        """
        Save PIL Image to Django ContentFile
        
        Args:
            image: PIL Image object
            filename: Output filename
            format: Image format (PNG, JPEG, etc.)
            quality: Quality for JPEG (1-100)
            
        Returns:
            Django ContentFile
        """
        try:
            buffer = io.BytesIO()
            
            if format.upper() == 'JPEG':
                image.save(buffer, format='JPEG', quality=quality, optimize=True)
            else:
                image.save(buffer, format='PNG', optimize=True)
            
            buffer.seek(0)
            return ContentFile(buffer.read(), name=filename)
            
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise
    
    @staticmethod
    def create_professional_collage_with_frames(
        uploaded_files: List[InMemoryUploadedFile],
        content_text: Optional[str] = None
    ) -> Tuple[ContentFile, List[ContentFile]]:
        """
        Main function to create collage and individual framed images with AI-powered design
        
        Args:
            uploaded_files: List of uploaded image files (max 4)
            content_text: Optional content text for AI design analysis
            
        Returns:
            Tuple of (collage_content_file, list_of_framed_images_content_files)
        """
        try:
            # Analyze content and generate design specifications if content provided
            design_specs = None
            if content_text:
                try:
                    from .design_analyzer import DesignAnalyzer
                    analysis = DesignAnalyzer.analyze_content(content_text)
                    design_specs = DesignAnalyzer.generate_design_specs(analysis, len(uploaded_files))
                    logger.info(f"Generated {design_specs['theme']} design theme with {design_specs['mood']} mood")
                except Exception as e:
                    logger.warning(f"Design analysis failed, using defaults: {e}")
            
            # Extract frame specs if available
            frame_specs = design_specs['frame_specs'] if design_specs else None
            collage_spec = design_specs['collage_spec'] if design_specs else None
            
            # Process all images with design specs
            processed = ImageProcessor.process_uploaded_images(
                uploaded_files, 
                add_frames=True, 
                frame_specs=frame_specs
            )
            
            if not processed:
                raise ValueError("No valid images to process")
            
            # Extract PIL images
            pil_images = [p['image'] for p in processed]
            
            # Create collage from non-framed versions with design specs
            non_framed_images = []
            for file in uploaded_files[:4]:
                try:
                    img = Image.open(file)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    non_framed_images.append(img)
                except:
                    continue
            
            collage = ImageProcessor.create_grid_collage(non_framed_images, collage_spec=collage_spec)
            
            # Save collage
            collage_file = ImageProcessor.save_image_to_content_file(
                collage, 
                'collage.png', 
                format='PNG'
            )
            
            # Save individual framed images
            framed_files = []
            for i, p in enumerate(processed):
                framed_file = ImageProcessor.save_image_to_content_file(
                    p['image'],
                    f"framed_{i+1}.png",
                    format='PNG'
                )
                framed_files.append(framed_file)
            
            return collage_file, framed_files
            
        except Exception as e:
            logger.error(f"Collage creation failed: {e}")
            raise


def generate_social_media_images(
    images: List[InMemoryUploadedFile], 
    content_text: str = None
) -> dict:
    """
    Generate social media ready images
    
    Args:
        images: List of uploaded images
        content_text: Optional text to overlay (future feature)
        
    Returns:
        Dict with URLs of generated images
    """
    try:
        processor = ImageProcessor()
        collage_file, framed_files = processor.create_professional_collage_with_frames(images)
        
        return {
            'collage': collage_file,
            'framed_images': framed_files,
            'count': len(framed_files)
        }
        
    except Exception as e:
        logger.error(f"Social media image generation failed: {e}")
        return {
            'error': str(e),
            'collage': None,
            'framed_images': [],
            'count': 0
        }
