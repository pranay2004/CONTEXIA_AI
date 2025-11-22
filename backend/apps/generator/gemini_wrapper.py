"""
Gemini API wrapper with Deep Context Chaining
Splits generation into Blog -> Socials for maximum quality.
Optimized for production with retry logic, robust JSON parsing, and parallel execution.
"""
import os
import json
import logging
import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import google.generativeai as genai
from django.conf import settings
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log
)
from google.api_core import exceptions as google_exceptions

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiChainedGenerator:
    """
    Orchestrates a multi-step generation workflow:
    1. Research & Authoring (Long-form Blog)
    2. Strategic Repurposing (Social Media Assets)
    """
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    def _load_prompt(self, name: str) -> str:
        """Load specialist prompt from text file"""
        try:
            path = os.path.join(
                os.path.dirname(__file__),
                'prompts',
                'specialist',
                f'{name}.txt'
            )
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt '{name}': {str(e)}")
            return ""

    @retry(
        retry=retry_if_exception_type((
            google_exceptions.ResourceExhausted,
            google_exceptions.ServiceUnavailable,
            google_exceptions.InternalServerError,
            google_exceptions.Aborted
        )),
        stop=stop_after_attempt(2),  # Reduced from 3 to 2 retries
        wait=wait_exponential(multiplier=1, min=2, max=10),  # Faster retry timing
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _execute_gemini_request(self, prompt: str) -> Any:
        return self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=4096,  # Reduced from 8192 for faster generation
            )
        )

    def generate_content(self, 
                        source_text: str,
                        trend_snippets: List[Dict],
                        topic: str = "",
                        platforms: List[str] = None) -> Dict:
        """
        Execute the Deep Context Chain with parallel generation for speed optimization
        """
        results = {}
        
        # 0. Prepare Context
        trends_context = "\n".join([
            f"- [{t.get('source', 'Trend')}] {t.get('title', 'Untitled')}: {t.get('snippet', '')[:200]}" 
            for t in trend_snippets[:5]
        ])
        combined_context = f"USER SOURCE: {source_text[:3000]}\n\nTRENDS: {trends_context}"
        
        # --- PARALLEL GENERATION: Blog + Socials at the same time ---
        logger.info(f"Starting parallel generation for topic '{topic}'...")
        
        # Prepare both prompts
        blog_prompt_template = self._load_prompt('blog_writer')
        if not blog_prompt_template:
            blog_prompt_template = "Write a detailed blog post about {topic} incorporating these trends: {trend_context}. Return JSON with title and html_content."
        blog_prompt = blog_prompt_template.format(
            topic=topic,
            trend_context=combined_context,
            word_count=1200
        )
        
        social_prompt_template = self._load_prompt('social_repurposer')
        if not social_prompt_template:
            social_prompt_template = "Generate LinkedIn post and Twitter thread based on: {source_text}. Return JSON."
        # For social, use source text since we're generating in parallel
        social_prompt = social_prompt_template.format(
            blog_content=source_text[:15000],
            trend_context=trends_context
        )
        
        # Execute both generations in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_blog = executor.submit(self._generate_with_retry, blog_prompt, "blog")
            future_social = executor.submit(self._generate_with_retry, social_prompt, "social")
            
            # Wait for both to complete
            blog_data = future_blog.result()
            social_data = future_social.result()
        
        # Merge results
        results['long_blog'] = blog_data
        results.update(social_data)
        
        # Add Metadata
        results['meta'] = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'model': "gemini-1.5-flash (Parallel)",
            'strategy': "Parallel Deep Context Chaining",
            'topic': topic
        }
        
        return results
    
    def _generate_with_retry(self, prompt: str, generation_type: str) -> Dict:
        """
        Execute a single generation with error handling
        """
        try:
            response = self._execute_gemini_request(prompt)
            data = self._safe_json(response.text)
            logger.info(f"{generation_type.capitalize()} generation completed successfully")
            return data
        except Exception as e:
            logger.error(f"{generation_type.capitalize()} generation failed: {e}")
            # Return safe fallback data
            if generation_type == "blog":
                return {'title': 'Generation Error', 'html_content': '<p>Could not generate blog content.</p>'}
            else:
                return {'linkedin': {}, 'twitter_thread': [], 'threads_post': ""}
    
    def _safe_json(self, text: str) -> Dict:
        """Clean markdown code blocks and parse JSON"""
        try:
            cleaned = text.strip()
            if cleaned.startswith('```json'): cleaned = cleaned[7:]
            elif cleaned.startswith('```'): cleaned = cleaned[3:]
            if cleaned.endswith('```'): cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except json.JSONDecodeError:
            logger.error("JSON Parse Error in generation step.")
            return {}

# Main Entry Point
def generate_content_with_gemini(source_text: str,
                                 trend_snippets: List[Dict],
                                 topic: str = "",
                                 platforms: List[str] = None,
                                 brand_voice: str = "") -> Dict:
    """
    Main function called by the API view.
    Note: brand_voice is currently not used in the chained prompts but kept for interface compatibility.
    """
    generator = GeminiChainedGenerator()
    return generator.generate_content(source_text, trend_snippets, topic, platforms)

# Helper functions (kept for compatibility)
def extract_topic_from_text(text: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Analyze the following text and extract the main topic or subject in 3-5 words.\nReturn ONLY the topic.\n\nTEXT:\n{text[:1000]}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "General Marketing"

def generate_hooks(topic: str, count: int = 5) -> List[str]:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Generate {count} viral hooks for: {topic}. Return as JSON array of strings."
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith('```json'): text = text[7:]
        if text.startswith('```'): text = text[3:]
        if text.endswith('```'): text = text[:-3]
        return json.loads(text.strip())
    except:
        return []