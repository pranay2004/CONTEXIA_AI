import logging
import os
import json
from django.conf import settings
from apps.ingest.models import GeneratedContent 
from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class UserPatternAnalyzer:
    def __init__(self, user):
        self.user = user
        self.history = GeneratedContent.objects.filter(user=user).order_by('-created_at')[:10]
        # Use Gemini by default as it's the free engine for this project
        self.ai_provider = 'gemini' 

    def analyze_brand_voice(self, text_samples: str):
        """
        Analyzes text to extract a Voice Persona and DNA Metrics.
        """
        if not text_samples or len(text_samples) < 100:
             return {"error": "Insufficient text. Please provide at least 100 words."}

        system_prompt = """
        You are a Computational Linguist. Analyze the provided text samples to create a "Voice Fingerprint".
        
        Return a JSON object with:
        1. "system_instruction": A strict instruction for an LLM to mimic this style (e.g. "Write in short, punchy sentences. Use satire. Avoid emojis.").
        2. "voice_name": A 3-word creative name for this style (e.g. "Witty Tech Founder").
        3. "metrics": A dictionary of 0-100 scores for:
           - "formality" (0=Slang, 100=Academic)
           - "warmth" (0=Cold/Direct, 100=Empathetic)
           - "emoji_usage" (0=None, 100=Heavy)
        4. "keywords": A list of 5 characteristic words/phrases used.
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini", # Fast and sufficient for analysis
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"SAMPLES:\n{text_samples[:5000]}"}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Voice Analysis Failed: {e}")
            return {
                "voice_name": "Standard Professional",
                "system_instruction": "Write in a clear, professional tone.",
                "metrics": {"formality": 80, "warmth": 50, "emoji_usage": 10},
                "keywords": []
            }

    def analyze_from_file(self, text_content: str):
        """
        Analyze raw text from an uploaded file to build a robust Voice Persona.
        """
        if not text_content or len(text_content) < 100:
            return {
                "voice_name": "Insufficient Data",
                "system_instruction": "Please upload a document with at least 100 words."
            }

        return self._analyze_with_gemini(text_content, mode="deep_analysis")

    def _analyze_with_gemini(self, text, mode="simple"):
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if mode == "deep_analysis":
            # PROMPT FOR VOICE CLONING
            prompt = f"""
            Act as a Computational Linguist. Analyze the following text samples from a creator.
            
            TEXT SAMPLES:
            {text[:10000]}
            
            TASK:
            Construct a "System Persona Instruction" that I can feed into an AI to make it write EXACTLY like this person.
            
            Analyze:
            1. Sentence structure (Short/Long, Complex/Simple)
            2. Vocabulary (Academic, Slang, Jargon-heavy, Simple)
            3. Tone (Authoritative, Humble, Sarcastic, Cheerful)
            4. Formatting quirks (Bullet points, Emojis, lower_case)
            
            Return VALID JSON:
            {{
                "voice_name": "A short 3-word name for this style (e.g. 'Punchy Tech Thought-Leader')",
                "system_instruction": "Write in short, staccato sentences. Use widely accessible vocabulary but deep technical concepts. Never use emojis. Use '--' for breaks...",
                "key_characteristics": ["Short sentences", "No emojis", "Direct tone"]
            }}
            """
        else:
            # Simple analysis for dashboard stats
            prompt = f"""
            Analyze these posts. Return valid JSON only: {{ "current_voice": "...", "suggestion": "..." }}
            POSTS: {text[:5000]}
            """

        try:
            response = model.generate_content(prompt)
            cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_text)
        except Exception as e:
            logger.error(f"Gemini Analysis Failed: {e}")
            return {
                "voice_name": "Analysis Error", 
                "system_instruction": "Standard professional tone."
            }