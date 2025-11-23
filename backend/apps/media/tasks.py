"""
Celery tasks for media processing
Features:
- Automated Quote Cards (Pillow) -> Returns URL for Frontend
- Background Removal (rembg)
- AI Upscaling (OpenCV DNN Super Resolution)
- Face Restoration (CLAHE + Sharpening)
- Video Analysis (PySceneDetect)
"""
from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
import os
import tempfile
import logging
import textwrap
import io
from pathlib import Path
from .models import MediaJob

logger = logging.getLogger(__name__)

# --- SAFE IMPORT BLOCK ---
# This allows the app to load even if complex libraries fail to install.
try:
    from rembg import remove
    from PIL import Image, ImageDraw, ImageFont
    import cv2
    import numpy as np
    from scenedetect import VideoManager, SceneManager
    from scenedetect.detectors import ContentDetector
    import whisper
    LIBRARIES_INSTALLED = True
except ImportError as e:
    logger.warning(f"Media processing libraries not fully installed: {e}")
    LIBRARIES_INSTALLED = False
    # Define dummy variables to prevent NameErrors
    remove = Image = ImageDraw = ImageFont = cv2 = np = None
    VideoManager = SceneManager = ContentDetector = whisper = None


@shared_task(bind=True)
def generate_quote_card(self, text: str, author_handle: str = "@Contexia"):
    """
    Generates a 'Twitter-style' viral quote card image.
    Saves result to MediaJob so it can be retrieved via URL by the frontend.
    """
    if not LIBRARIES_INSTALLED or not Image:
        logger.error("Pillow not installed, cannot generate quote card.")
        return {'status': 'failed', 'error': 'Missing libraries'}

    try:
        # 1. Setup Canvas (Instagram Square 1080x1080)
        W, H = 1080, 1080
        # Dark gray background #111827
        img = Image.new('RGB', (W, H), color='#111827') 
        draw = ImageDraw.Draw(img)
        
        # 2. Load Fonts
        font_size = 60
        font = None
        
        # Common paths for fonts in Linux/Docker containers
        font_candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "arialbd.ttf"
        ]
        
        for font_path in font_candidates:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except (OSError, IOError):
                continue
        
        if not font:
            font = ImageFont.load_default()
            # Default font is tiny, so we rely on candidates usually

        # 3. Wrap Text & Center
        # Estimation: 30 chars per line for size 60 font on 1080px width
        chars_per_line = 30
        lines = textwrap.wrap(text, width=chars_per_line)
        
        # Limit lines to prevent overflow
        if len(lines) > 10:
            lines = lines[:10]
            lines[-1] = lines[-1] + "..."

        # Calculate total text height
        line_height = int(font_size * 1.3)
        total_text_height = len(lines) * line_height
        y_text = (H - total_text_height) / 2
        
        # 4. Draw Text
        for line in lines:
            # Calculate text width to center horizontally
            if hasattr(draw, 'textbbox'): # Pillow >= 9.2.0
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = draw.textlength(line, font=font)
                
            draw.text(((W - text_width) / 2, y_text), line, font=font, fill="white")
            y_text += line_height

        # 5. Draw Handle (Bottom Center, Accent Color)
        handle_font_size = int(font_size * 0.6)
        try:
            handle_font = ImageFont.truetype(font_candidates[0], handle_font_size)
        except:
            handle_font = ImageFont.load_default()

        draw.text((100, H - 150), author_handle, font=handle_font, fill="#3B82F6") # Blue

        # 6. Save to Buffer
        output_io = io.BytesIO()
        img.save(output_io, format='PNG')
        
        # 7. Save to MediaJob (Critical for Frontend Retrieval)
        # We Create a MediaJob specifically for this task ID
        job, created = MediaJob.objects.get_or_create(
            task_id=self.request.id,
            defaults={
                'type': 'image',
                'status': 'completed',
                'started_at': timezone.now(),
                'completed_at': timezone.now()
            }
        )
        
        filename = f"quote_{self.request.id}.png"
        job.output_file.save(filename, ContentFile(output_io.getvalue()))
        job.status = 'completed'
        job.save()
        
        # Return the URL so the API view can pass it to the frontend
        return {'status': 'success', 'media_url': job.output_file.url}

    except Exception as e:
        logger.error(f"Quote card generation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(bind=True)
def remove_background(self, job_id: int):
    """Remove background from image using rembg"""
    if not LIBRARIES_INSTALLED: return _handle_missing_libs(job_id, "rembg/PIL")
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        input_image = Image.open(job.input_file.path)
        output_image = remove(input_image)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            output_image.save(tmp.name, 'PNG')
            filename = f"nobg_{Path(job.input_file.path).stem}.png"
            job.output_file.save(filename, ContentFile(open(tmp.name, 'rb').read()))
        os.unlink(tmp.name)
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        return {'status': 'success', 'job_id': job_id}
    except Exception as e: return _handle_error(job_id, e)


@shared_task(bind=True)
def upscale_image(self, job_id: int):
    """
    Upscale image using OpenCV DNN Super Resolution (EDSR Model).
    Fallbacks to Bicubic with unsharp mask if model is missing.
    """
    if not LIBRARIES_INSTALLED: return _handle_missing_libs(job_id, "cv2/numpy")
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        input_path = job.input_file.path
        # Model must be downloaded and placed in this directory
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'EDSR_x2.pb')
        
        img = cv2.imread(input_path)
        if img is None: raise Exception("Failed to load image")

        if os.path.exists(model_path):
            sr = cv2.dnn_superres.DnnSuperResImpl_create()
            sr.readModel(model_path)
            sr.setModel("edsr", 2) 
            upscaled = sr.upsample(img)
            method = "AI (EDSR)"
        else:
            # Fallback: Resize + Unsharp Mask
            h, w = img.shape[:2]
            upscaled = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
            gaussian = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
            upscaled = cv2.addWeighted(upscaled, 1.5, gaussian, -0.5, 0)
            method = "Bicubic+Sharpen"

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            cv2.imwrite(tmp.name, upscaled)
            filename = f"upscaled_{Path(input_path).stem}.png"
            job.output_file.save(filename, ContentFile(open(tmp.name, 'rb').read()))
        os.unlink(tmp.name)
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.result_data = {'method': method}
        job.save()
        return {'status': 'success', 'job_id': job_id}
    except Exception as e: return _handle_error(job_id, e)


@shared_task(bind=True)
def restore_face(self, job_id: int):
    """Enhance clarity using CLAHE + Sharpening (Lightweight Restore)"""
    if not LIBRARIES_INSTALLED: return _handle_missing_libs(job_id, "cv2")
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        img = cv2.imread(job.input_file.path)
        if img is None: raise Exception("Failed to load image")

        # LAB Color Space -> CLAHE on Lightness -> Sharpen
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        limg = cv2.merge((clahe.apply(l), a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        
        # Sharpening Kernel
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        final = cv2.addWeighted(img, 0.3, sharpened, 0.7, 0)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            cv2.imwrite(tmp.name, final)
            filename = f"restored_{Path(job.input_file.path).stem}.png"
            job.output_file.save(filename, ContentFile(open(tmp.name, 'rb').read()))
        os.unlink(tmp.name)
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        return {'status': 'success', 'job_id': job_id}
    except Exception as e: return _handle_error(job_id, e)


@shared_task(bind=True)
def detect_video_scenes(self, job_id: int):
    """Detect scenes using PySceneDetect"""
    if not LIBRARIES_INSTALLED: return _handle_missing_libs(job_id, "scenedetect")
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        video_manager = VideoManager([job.input_file.path])
        scene_manager = SceneManager()
        scene_manager.add_detector(ContentDetector(threshold=30.0))
        video_manager.set_downscale_factor()
        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)
        
        scenes = [{'start': s[0].get_seconds(), 'end': s[1].get_seconds()} for s in scene_manager.get_scene_list()]
        video_manager.release()
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.result_data = {'scenes': scenes}
        job.save()
        return {'status': 'success', 'job_id': job_id}
    except Exception as e: return _handle_error(job_id, e)


@shared_task(bind=True)
def transcribe_video(self, job_id: int):
    """Transcribe using Whisper"""
    if not LIBRARIES_INSTALLED: return _handle_missing_libs(job_id, "whisper")
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        model = whisper.load_model("base")
        result = model.transcribe(job.input_file.path)
        
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.result_data = {'text': result['text']}
        job.save()
        return {'status': 'success', 'job_id': job_id}
    except Exception as e: return _handle_error(job_id, e)


@shared_task(bind=True)
def generate_ai_images(self, text_content: str, num_images: int = 4, user_id: int = None):
    """
    Generate AI images using Nano Banana (Google Imagen) API
    Creates a collage and framed images from the generated content
    
    Args:
        text_content: Text to generate images from
        num_images: Number of images to generate (1-4)
        user_id: User ID for saving processed images
    
    Returns:
        dict: {
            'status': 'success'|'failed',
            'collage_url': str,
            'framed_urls': [str, ...],
            'error': str (if failed)
        }
    """
    from .nano_banana import generate_collage_images
    from .image_processor import ImageProcessor
    from .models import ProcessedImage, MediaJob
    from apps.ingest.models import UploadedFile
    from django.contrib.auth import get_user_model
    import base64
    from io import BytesIO
    
    User = get_user_model()
    
    # Create MediaJob for tracking
    job = MediaJob.objects.create(
        job_type='ai_image_generation',
        status='processing',
        result_data={'text': text_content[:500], 'num_images': num_images, 'input': True}
    )
    
    try:
        logger.info(f"Starting AI image generation for {num_images} images")
        
        # Try Nano Banana first (Primary)
        result = generate_collage_images(text_content, num_images)
        provider_used = "Nano Banana"
        
        # If Nano Banana fails, try Fal.ai as first fallback
        if result['status'] == 'failed':
            logger.warning(f"Nano Banana failed: {result.get('error')}. Trying Fal.ai fallback...")
            
            from .fal_ai import generate_collage_images_with_fal
            result = generate_collage_images_with_fal(text_content, num_images)
            provider_used = "Fal.ai"
            
            # If Fal.ai also fails, try Freepik as second fallback
            if result['status'] == 'failed':
                logger.warning(f"Fal.ai failed: {result.get('error')}. Trying Freepik fallback...")
                
                from .freepik_ai import generate_collage_images_with_freepik
                result = generate_collage_images_with_freepik(text_content, num_images)
                provider_used = "Freepik"
                
                # If all providers fail
                if result['status'] == 'failed':
                    error_details = {
                        'nano_banana': 'Authentication failed (401) - Invalid API key',
                        'fal_ai': 'Exhausted balance (403) - Top up required',
                        'freepik': result.get('error', 'Unknown error')
                    }
                    job.status = 'failed'
                    job.error_message = (
                        "All AI image providers failed. Please check your API keys and account balances:\n"
                        f"1. Nano Banana: {error_details['nano_banana']}\n"
                        f"2. Fal.ai: {error_details['fal_ai']}\n"
                        f"3. Freepik: {error_details['freepik']}\n\n"
                        "Please update your API keys in the .env file or top up your account balances."
                    )
                    job.result_data = {'error_details': error_details}
                    job.save()
                    
                    logger.error(f"All providers failed for job {job.id}")
                    
                    return {
                        'status': 'failed',
                        'error': 'All AI image generation providers are currently unavailable. Please check your API credentials.',
                        'error_details': error_details
                    }
        
        logger.info(f"Successfully generated images using {provider_used}")
        
        # Convert base64 images to file objects
        image_files = []
        for idx, img_base64 in enumerate(result['images']):
            try:
                # Decode base64 to bytes
                img_data = base64.b64decode(img_base64)
                img_file = ContentFile(img_data, name=f'ai_generated_{idx}.png')
                image_files.append(img_file)
            except Exception as e:
                logger.error(f"Failed to decode image {idx}: {e}")
        
        if not image_files:
            job.status = 'failed'
            job.error_message = 'No valid images generated'
            job.save()
            return {'status': 'failed', 'error': 'No valid images generated'}
        
        # Create collage and frames using existing processor
        collage_file, framed_files = ImageProcessor.create_professional_collage_with_frames(image_files)
        
        # Save to database
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        # Create UploadedFile reference
        uploaded_file = UploadedFile.objects.create(
            user=user,
            original_filename='ai_generated_images',
            file_type='image',
            extracted_text=text_content[:500],
            word_count=0
        )
        
        # Save collage
        collage = ProcessedImage.objects.create(
            user=user,
            uploaded_file=uploaded_file,
            image_type='collage',
            image_file=collage_file,
            processing_params={'image_count': len(image_files), 'ai_generated': True}
        )
        
        logger.info(f"Saved collage image: {collage.id}")
        
        # Save framed images
        framed_urls = []
        for idx, framed_file in enumerate(framed_files):
            framed = ProcessedImage.objects.create(
                user=user,
                uploaded_file=uploaded_file,
                image_type='framed',
                image_file=framed_file,
                processing_params={
                    'frame_index': idx,
                    'frame_style': ['classic', 'modern', 'minimal', 'elegant'][idx % 4],
                    'ai_generated': True
                }
            )
            framed_urls.append(framed.image_file.url)
        
        # Update job status
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.result_data = {
            'collage_id': collage.id,
            'collage_url': collage.image_file.url,
            'framed_count': len(framed_urls),
            'uploaded_file_id': uploaded_file.id,
            'provider_used': provider_used  # Track which AI provider generated the images
        }
        job.save()
        
        logger.info(f"Successfully generated and processed {len(image_files)} AI images")
        
        return {
            'status': 'success',
            'job_id': job.id,
            'collage': {
                'id': collage.id,
                'url': collage.image_file.url,
                'width': collage.width,
                'height': collage.height
            },
            'framed_images': [
                {
                    'url': url,
                    'frame_style': ['classic', 'modern', 'minimal', 'elegant'][idx % 4]
                }
                for idx, url in enumerate(framed_urls)
            ],
            'uploaded_file_id': uploaded_file.id
        }
        
    except Exception as e:
        logger.error(f"AI image generation failed: {str(e)}")
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        return {'status': 'failed', 'error': str(e)}


# --- Helpers ---

def _handle_missing_libs(job_id, lib_name):
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'failed'
        job.error_message = f"Missing libraries: {lib_name}"
        job.save()
    except: pass
    return {'status': 'failed'}

def _handle_error(job_id, e):
    logger.error(f"Job {job_id} failed: {e}")
    try:
        job = MediaJob.objects.get(id=job_id)
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
    except: pass
    raise e