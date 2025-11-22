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