"""
OpenAI API Wrapper with Parallel Agentic Streaming
Optimized for "Deep-Work" Quality Content using Dedicated Agents & Templates.
Now powered by TrendMaster V6 Enhanced Master Prompt for market-level content quality.
"""
import os
import logging
import json
import asyncio
import concurrent.futures
import re
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI, OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

# Initialize Clients
aclient = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- MASTER PROMPT LOADER ---
def _load_master_prompt() -> str:
    """
    Load the TrendMaster V6 Enhanced Master Prompt from external file.
    This provides professional copywriting formulas for market-level content.
    """
    try:
        path = os.path.join(
            os.path.dirname(__file__),
            'prompts',
            'master_prompt.txt'
        )
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading master_prompt.txt: {str(e)}")
        logger.warning("Falling back to basic inline prompts")
        return ""

# Load master prompt once at module initialization
MASTER_PROMPT = _load_master_prompt()

def clean_json_response(content: str) -> str:
    """
    Robustly cleans AI response to ensure valid JSON.
    Removes markdown code blocks and whitespace.
    """
    try:
        # Remove markdown code blocks (```json ... ```)
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        return content.strip()
    except Exception as e:
        logger.error(f"JSON cleaning error: {e}")
        return content

# --- STREAMING CLASS (Restored & Upgraded) ---

class ContentStreamer:
    """
    Manages parallel generation streams with Template-Based Prompts.
    """
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.final_content = {
            "long_blog": {"html": "", "title": "", "word_count": 0},
            "linkedin": {"post_text": "", "hashtags": []},
            "x_thread": [],
            "threads": [],
            "youtube": {"title": "", "script": "", "description": ""},
            "short_blog": {"html": "", "title": "", "word_count": 0},
            "email_newsletter": {"subject": "", "preheader": "", "html_body": "", "plain_text": ""},
            "meta": {}
        }

    async def _stream_blog_agent(self, context: str, topic: str):
        """
        The 'Authority' Agent: Generates blog posts using TrendMaster V6 master prompt.
        Follows professional copywriting formulas for maximum engagement and authority.
        """
        # Use master prompt if available, otherwise fallback to basic template
        if MASTER_PROMPT:
            system_prompt = (
                f"{MASTER_PROMPT}\n\n"
                "=============================================================================\n"
                "TASK: Generate a BLOG/ARTICLE following the detailed specifications in the master prompt.\n"
                "Focus on the 'BLOG/ARTICLE (Authority Architecture)' section.\n"
                "=============================================================================\n\n"
                "CRITICAL REQUIREMENTS:\n"
                "1. Apply ALL 10 Commandments (Hook Engineering, Villain Framing, etc.)\n"
                "2. Use the Headline Engineering formula\n"
                "3. Follow the Opening Section structure (200-300 words)\n"
                "4. Structure Main Content with chapter-style H2 headers\n"
                "5. Include Named Frameworks, Proof Stacking, and Visual Elements\n"
                "6. Apply SEO Optimization Checklist\n"
                "7. Output Format: Return ONLY the HTML content (use <h2>, <h3>, <p>, <ul>, <li>, <strong>)\n"
                "8. Do NOT use <html>, <head>, or <body> tags\n"
                "9. Length: 1,800-2,500 words minimum for authority positioning\n"
                "10. Tone: Professional yet conversational, data-backed, contrarian where appropriate\n"
            )
        else:
            # Fallback to original prompt if master prompt fails to load
            system_prompt = (
                "You are an elite SEO Content Writer. Write a blog post following this STRICT template:\n\n"
                "**Title**: Compelling, specific, includes the promise.\n"
                "**Introduction**: Hook + Problem + Promise (What the reader will learn).\n"
                "**Section 1 - Context/Background**: Explain the problem space. Provide stats/insights.\n"
                "**Section 2 - Main Concepts/Framework**: Use <h3> headings for steps (e.g., 'Step 1: Research'). "
                "For EACH step, include: What it is + Why it matters + Example + Action Items.\n"
                "**Section 3 - Tools & Resources**: Tech stack, templates, or playbooks.\n"
                "**Conclusion**: Final takeaway + Short summary of key points.\n"
                "**CTA**: Encouraging next step.\n\n"
                "Format: HTML (<h3>, <p>, <ul>, <li>, <strong>). Do NOT use <html> or <body> tags. "
                "Tone: Professional, authoritative, yet accessible."
            )
        
        user_prompt = f"TOPIC: {topic}\n\nRESEARCH CONTEXT:\n{context}\n\nWrite the full article now:"
        
        try:
            stream = await aclient.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    self.final_content["long_blog"]["html"] += token
                    
                    await self.queue.put({
                        "type": "blog_delta", 
                        "content": token
                    })
            
            # Metadata calculation
            full_html = self.final_content["long_blog"]["html"]
            word_count = len(full_html.split())
            self.final_content["long_blog"]["word_count"] = word_count
            self.final_content["long_blog"]["title"] = f"Guide: {topic}"
            
            await self.queue.put({"type": "blog_done"})
            
        except Exception as e:
            logger.error(f"Blog Agent Failed: {e}")
            await self.queue.put({"type": "error", "message": "Blog generation failed"})

    async def _stream_social_agent(self, context: str):
        """
        The 'Viral' Agent: Generates social assets using TrendMaster V6 master prompt.
        Applies platform-specific engineering blueprints for maximum engagement.
        """
        # Use master prompt if available, otherwise fallback to basic template
        if MASTER_PROMPT:
            system_prompt = (
                f"{MASTER_PROMPT}\n\n"
                "=============================================================================\n"
                "TASK: Generate social media content for ALL PLATFORMS following the master prompt specifications.\n"
                "=============================================================================\n\n"
                "PLATFORMS TO GENERATE:\n"
                "1. LINKEDIN - Use 'LINKEDIN (Authority + Demand Gen Engine)' section\n"
                "2. TWITTER/X THREAD - Use 'TWITTER/X THREAD (Viral Density Engine)' section\n"
                "3. YOUTUBE SCRIPT - Use 'YOUTUBE SCRIPT (Cinematic Performance Blueprint)' section\n"
                "4. EMAIL NEWSLETTER - Use 'EMAIL NEWSLETTER (Inbox-to-Action Pipeline)' section\n\n"
                "CRITICAL REQUIREMENTS:\n"
                "1. Apply ALL 10 Commandments to every platform\n"
                "2. Use platform-specific formulas and structures exactly as specified\n"
                "3. Include psychographic triggers (2-3 per piece)\n"
                "4. ZERO banned words - use power word replacements\n"
                "5. Follow character/length requirements for each platform\n"
                "6. Include specific CTAs (never generic)\n\n"
                "OUTPUT FORMAT - Return strictly valid JSON with these keys:\n"
                "{\n"
                '  "linkedin": {"post_text": "...", "hashtags": [...], "cta": "..."},\n'
                '  "x_thread": ["tweet1", "tweet2", ...],\n'
                '  "youtube": {"title": "...", "script": "...", "description": "..."},\n'
                '  "email_newsletter": {"subject": "...", "preheader": "...", "html_body": "...", "plain_text": "..."}\n'
                "}"
            )
        else:
            # Fallback to original prompt if master prompt fails to load
            system_prompt = (
                "You are a Viral Social Media Strategist. Generate content adhering to these specific templates.\n"
                "Return strictly valid JSON with keys: 'linkedin', 'x_thread', 'threads_post', 'youtube', 'email_newsletter'.\n\n"
                
                "1. **LINKEDIN** (Professional & Storytelling):\n"
                "- **Hook** (1-2 lines): Bold insight, question, or surprising fact.\n"
                "- **Context** (2-4 lines): Describe the situation/problem ('Last week...').\n"
                "- **Insight/Solution** (3-6 lines): What changed or was learned.\n"
                "- **Takeaway** (1-3 lines): Clear learnable outcome.\n"
                "- **CTA**: Engaging question.\n"
                "- **Hashtags**: 6-10 relevant tags.\n"
                "- **Keys**: post_text, hashtags, cta.\n\n"
                
                "2. **X/TWITTER THREAD** (Concise & Punchy):\n"
                "- Tweet 1: Hook + Value (e.g., 'Consistency beats talent').\n"
                "- Tweets 2-N: The Lesson/Steps (One main point per tweet). Use arrows (→) and short sentences.\n"
                "- Final Tweet: Summary + CTA (Follow/Retweet).\n\n"
                
                "4. **EMAIL NEWSLETTER** (Professional Format):\n"
                "- **Subject**: Compelling subject line (40-60 chars).\n"
                "- **Preheader**: Supporting text (40-100 chars).\n"
                "- **HTML Body**: Greeting + Hook + 3-5 key insights with <h2> headings + CTA.\n"
                "- **Plain Text**: Text-only version.\n"
                "- Use inline CSS, 600px width, professional styling.\n\n"
                
                "3. **YOUTUBE SCRIPT** (Engaging Video Structure):\n"
                "- **Intro** (10-15s): Hook question + Self-intro + Purpose.\n"
                "- **Problem/Story** (30-60s): The scenario and why it matters.\n"
                "- **Main Content** (3-6 points): Steps/Framework. Each part needs Explanation + Example.\n"
                "- **Key Takeaways** (10-20s).\n"
                "- **CTA** (10-15s): Subscribe/Comment.\n"
                "- Include [VISUAL CUE] and [SOUND EFFECT] notes in brackets."
            )
        
        user_prompt = f"CONTEXT:\n{context}\n\nGenerate the social media pack JSON:"
        
        try:
            response = await aclient.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content_str = clean_json_response(response.choices[0].message.content)
            data = json.loads(content_str)
            
            # Update state
            self.final_content["linkedin"] = data.get("linkedin", {"post_text": "", "hashtags": []})
            
            # Handle Twitter keys
            self.final_content["x_thread"] = data.get("x_thread", [])
            if not self.final_content["x_thread"]:
                self.final_content["x_thread"] = data.get("twitter_thread", [])
                
            self.final_content["threads"] = data.get("threads_post", [])
            self.final_content["youtube"] = data.get("youtube", {"title": "", "script": ""})
            self.final_content["email_newsletter"] = data.get("email_newsletter", {
                "subject": "",
                "preheader": "",
                "html_body": "",
                "plain_text": ""
            })
            
            await self.queue.put({
                "type": "social_complete",
                "data": {
                    "linkedin": self.final_content["linkedin"],
                    "x_thread": self.final_content["x_thread"],
                    "threads": self.final_content["threads"],
                    "youtube": self.final_content["youtube"],
                    "email_newsletter": self.final_content["email_newsletter"]
                }
            })
            
        except Exception as e:
            logger.error(f"Social Agent Failed: {e}")

    async def generate_parallel_stream(self, extracted_text, trend_snippets, topic) -> AsyncGenerator[str, None]:
        """Main entry point for the view."""
        trends_context = "\n".join([f"- {t['title']}: {t['snippet'][:200]}" for t in trend_snippets])
        full_context = f"SOURCE MATERIAL:\n{extracted_text[:4000]}\n\nTRENDING INSIGHTS:\n{trends_context}"
        
        tasks = [
            asyncio.create_task(self._stream_blog_agent(full_context, topic)),
            asyncio.create_task(self._stream_social_agent(full_context))
        ]
        
        active_agents = 2 
        
        while active_agents > 0:
            item = await self.queue.get()
            
            if item["type"] in ["blog_done", "social_complete", "error"]:
                active_agents -= 1
                if item["type"] == "social_complete":
                    yield f"data: {json.dumps(item)}\n\n"
            else:
                yield f"data: {json.dumps(item)}\n\n"
                
            self.queue.task_done()

        self.final_content["short_blog"] = self.final_content["long_blog"] 
        
        yield f"data: {json.dumps({'type': 'stream_done', 'final_db_data': self.final_content})}\n\n"


# --- SYNCHRONOUS FUNCTIONS (For Celery Tasks) ---

def generate_content_with_openai(extracted_text: str, trend_snippets: List[Dict], platforms: List[str], brand_voice: str = "") -> Dict:
    """
    Generate content using a Multi-Agent Architecture (Synchronous wrapper for Celery).
    Injects Brand Voice settings if provided.
    """
    
    # 1. Prepare Context
    trends_context = "\n".join([
        f"- [{t.get('source', 'Trend')}] {t.get('title', 'Untitled')}: {t.get('snippet', '')[:300]}" 
        for t in trend_snippets[:10]
    ])
    
    full_input_text = f"CORE CONTENT:\n{extracted_text[:3000]}\n\nMARKET TRENDS:\n{trends_context}"
    
    # --- PREPARE BRAND VOICE INSTRUCTION ---
    brand_instruction = ""
    if brand_voice:
        brand_instruction = (
            "\n\n### CRITICAL: BRAND VOICE INSTRUCTIONS ###\n"
            f"You MUST adhere to the following tone, style, and directives:\n{brand_voice}\n"
            "Ignore any default generic AI tone. Sound like THIS brand.\n"
        )

    # --- AGENT 1: The Editorial Director (Blog) ---
    def run_blog_agent():
        try:
            if MASTER_PROMPT:
                system_prompt = (
                    f"{MASTER_PROMPT}\n\n"
                    "=============================================================================\n"
                    "TASK: Generate a BLOG/ARTICLE following the TrendMaster V6 specifications.\n"
                    "=============================================================================\n\n"
                    "Apply the 'BLOG/ARTICLE (Authority Architecture)' blueprint:\n"
                    "- Use Headline Engineering formula\n"
                    "- Follow Opening Section structure\n"
                    "- Apply all 10 Commandments\n"
                    "- Include Named Frameworks and Proof Stacking\n"
                    "- SEO optimization required\n"
                    f"{brand_instruction}"
                    "\n\nReturn JSON with keys: 'title', 'html_content'."
                )
            else:
                system_prompt = (
                    "You are an elite SEO Content Writer. Write a definitive, deep-dive article (1,800+ words) "
                    "following this STRICT template:\n\n"
                    "Title: Compelling, specific, includes the promise.\n"
                    "Introduction: Hook + Problem + Promise (What the reader will learn).\n"
                    "Section 1 - Context/Background: Explain the problem space. Provide stats/insights.\n"
                    "Section 2 - Main Concepts/Framework: Use <h3> headings for steps. "
                    "For EACH step, include: What it is + Why it matters + Example + Action Items.\n"
                    "Section 3 - Tools & Resources: Tech stack, templates, or playbooks.\n"
                    "Conclusion: Final takeaway + Short summary of key points.\n"
                    "CTA: Encouraging next step.\n\n"
                    "Format: HTML (<h3>, <p>, <ul>, <li>, <strong>). Do NOT use <html> or <body> tags. "
                    "Tone: Professional, authoritative, yet accessible."
                    f"{brand_instruction}"
                    "\n\nReturn JSON with keys: 'title', 'html_content'."
                )
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Write the blog post based on:\n\n{full_input_text}\n\nReturn JSON only."}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000
            )
            content = clean_json_response(response.choices[0].message.content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"Blog Agent failed: {e}")
            return {'title': 'Generation Error', 'html_content': '<p>Could not generate blog content.</p>'}

    # --- AGENT 2: The YouTube Producer (Script) ---
    def run_youtube_agent():
        try:
            if MASTER_PROMPT:
                system_prompt = (
                    f"{MASTER_PROMPT}\n\n"
                    "=============================================================================\n"
                    "TASK: Generate YOUTUBE SCRIPT following TrendMaster V6 specifications.\n"
                    "=============================================================================\n\n"
                    "Apply the 'YOUTUBE SCRIPT (Cinematic Performance Blueprint)' section:\n"
                    "- Use Cold Open pattern (0:00-0:03)\n"
                    "- Follow Chapter-Based Structure\n"
                    "- Include Retention Mechanisms every 45-60 seconds\n"
                    "- Add [VISUAL], [AUDIO], and [RETENTION HOOK] cues\n"
                    "- Apply all 10 Commandments\n"
                    f"{brand_instruction}"
                    "\n\nReturn JSON with keys: 'title', 'script', 'description'."
                )
            else:
                system_prompt = (
                    "You are a YouTube Scriptwriter for channels like MrBeast or Ali Abdaal. "
                    "Write a FULL 10-minute video script (approx 1,500 words) using this Engaging Structure:\n\n"
                    "1. **INTRO (10-15 sec)**: Hook question / bold statement + Introduce self & purpose.\n"
                    "2. **STORY/PROBLEM (30-60 sec)**: Explain the scenario & why it matters.\n"
                    "3. **MAIN CONTENT (3-6 Points)**: Detailed steps/framework. Each part includes Explanation + Example.\n"
                    "4. **KEY TAKEAWAYS (10-20 sec)**: Rapid summary.\n"
                    "5. **CTA (10-15 sec)**: Subscribe/Like/Comment.\n"
                    "6. **OUTRO**: Offer value or teaser.\n\n"
                    "CRITICAL: You MUST include production notes in brackets like [VISUAL: Stock charts], [SOUND: Cash register], [TEXT OVERLAY]. "
                    f"{brand_instruction}"
                    "\n\nReturn JSON with keys: 'title', 'script', 'description'."
                )
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Write the viral script based on:\n\n{full_input_text}\n\nReturn JSON only."}
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
                max_tokens=4000
            )
            content = clean_json_response(response.choices[0].message.content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"YouTube Agent failed: {e}")
            return {'title': '', 'script': 'Error generating script.', 'description': ''}

    # --- AGENT 3: The Social Media Ghostwriter (LinkedIn/Twitter) ---
    def run_social_agent():
        try:
            if MASTER_PROMPT:
                system_prompt = (
                    f"{MASTER_PROMPT}\n\n"
                    "=============================================================================\n"
                    "TASK: Generate LINKEDIN and TWITTER content following TrendMaster V6 specifications.\n"
                    "=============================================================================\n\n"
                    "PLATFORMS:\n"
                    "1. LINKEDIN - Apply 'LINKEDIN (Authority + Demand Gen Engine)' blueprint\n"
                    "2. TWITTER - Apply 'TWITTER/X THREAD (Viral Density Engine)' blueprint\n\n"
                    "REQUIREMENTS:\n"
                    "- Use ALL 10 Commandments\n"
                    "- Apply Hook Formulas specified for each platform\n"
                    "- Include psychographic triggers\n"
                    "- Zero banned words\n"
                    "- Specific CTAs (never generic)\n"
                    f"{brand_instruction}"
                    "\n\nReturn JSON: {'linkedin': {'post_text': '...', 'hashtags': [...], 'cta': '...'}, 'twitter_thread': [...]}"
                )
            else:
                system_prompt = (
                    "You are a specialized Social Media Ghostwriter. Generate high-engagement text. "
                    "Return strictly valid JSON with keys: 'linkedin', 'twitter_thread'.\n\n"
                    
                    "1. **LINKEDIN POST** (Professional & Storytelling):\n"
                    "   - Hook (1-2 lines): Bold insight or surprising fact.\n"
                    "   - Context (2-4 lines): Describe situation/problem.\n"
                    "   - Insight/Solution (3-6 lines): What changed/learned.\n"
                    "   - Takeaway (1-3 lines): Clear learnable outcome.\n"
                    "   - CTA: Question for engagement.\n"
                    "   - Hashtags: 6-10 relevant tags.\n"
                    "   - Keys needed: 'post_text', 'hashtags', 'cta'.\n\n"
                    
                    "2. **TWITTER THREAD** (Concise & Punchy):\n"
                    "   - 10-15 Tweets total.\n"
                    "   - Tweet 1: Hook + Value (e.g. 'Consistency beats talent').\n"
                    "   - Body: Step-by-step breakdown. One main point per tweet.\n"
                    "   - Format: Use emojis and arrows (->) for readability.\n"
                    "   - Final Tweet: Summary + CTA.\n"
                    "   - Return as array of strings."
                    f"{brand_instruction}"
                )
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate the social posts based on:\n\n{full_input_text}\n\nReturn JSON only."}
                ],
                response_format={"type": "json_object"},
                temperature=0.85,
                max_tokens=3000
            )
            
            content_str = clean_json_response(response.choices[0].message.content)
            return json.loads(content_str)
            
        except Exception as e:
            logger.error(f"Social Agent failed: {e}")
            return {
                'linkedin': {'post_text': '', 'hashtags': []}, 
                'twitter_thread': []
            }

    # --- AGENT 4: The Email Marketing Specialist (Newsletter) ---
    def run_email_agent():
        try:
            if MASTER_PROMPT:
                system_prompt = (
                    f"{MASTER_PROMPT}\n\n"
                    "=============================================================================\n"
                    "TASK: Generate EMAIL NEWSLETTER following TrendMaster V6 specifications.\n"
                    "=============================================================================\n\n"
                    "Apply the 'EMAIL NEWSLETTER (Inbox-to-Action Pipeline)' blueprint:\n"
                    "- Subject Line formulas (40-50 chars)\n"
                    "- Preheader technique\n"
                    "- Email Body Structure with Hook + Value Core + CTA\n"
                    "- Design Specifications (600px, inline CSS)\n"
                    "- Apply all 10 Commandments\n"
                    f"{brand_instruction}"
                    "\n\nReturn JSON with keys: 'subject', 'preheader', 'html_body', 'plain_text'."
                )
            else:
                system_prompt = (
                    "You are an expert Email Marketing Copywriter. Create a professional, engaging email newsletter "
                    "using proven email marketing best practices.\n\n"
                    "Structure:\n"
                    "1. **SUBJECT LINE**: Compelling, curiosity-driven, 40-60 characters. Promise value.\n"
                    "2. **PREHEADER**: Supporting text that complements subject (40-100 chars).\n"
                    "3. **EMAIL BODY** (HTML Format):\n"
                    "   - Personalized greeting: 'Hi there,' or 'Hey [Name],'\n"
                    "   - Hook paragraph: Start with a relatable problem or question\n"
                    "   - Main content: 3-5 key insights or tips. Use <h2> for sections.\n"
                    "   - Each section should have: Clear headline + 2-3 paragraphs + bullet points if applicable\n"
                    "   - Visual breaks: Use horizontal rules <hr> between sections\n"
                    "   - CTA Button: Include a clear call-to-action in a styled button\n"
                    "   - Footer: Include unsubscribe link and company info placeholder\n"
                    "4. **PLAIN TEXT VERSION**: Text-only version of the email for email clients that don't support HTML\n\n"
                    "Styling Guidelines:\n"
                    "- Use inline CSS styles for email compatibility\n"
                    "- Keep width to 600px max\n"
                    "- Use safe fonts: Arial, Helvetica, sans-serif\n"
                    "- Include responsive meta tags\n"
                    "- Professional color scheme (primary: #4F46E5, text: #1F2937)\n"
                    f"{brand_instruction}"
                    "\n\nReturn JSON with keys: 'subject', 'preheader', 'html_body', 'plain_text'."
                )
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create an email newsletter based on:\n\n{full_input_text}\n\nReturn JSON only."}
                ],
                response_format={"type": "json_object"},
                temperature=0.75,
                max_tokens=3500
            )
            content = clean_json_response(response.choices[0].message.content)
            return json.loads(content)
        except Exception as e:
            logger.error(f"Email Agent failed: {e}")
            return {
                'subject': 'Newsletter Update',
                'preheader': 'Your latest insights inside',
                'html_body': '<p>Error generating email content.</p>',
                'plain_text': 'Error generating email content.'
            }

    # --- EXECUTE PARALLEL AGENTS ---
    logger.info("Launching Multi-Agent Generation Grid...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        future_blog = executor.submit(run_blog_agent)
        future_youtube = executor.submit(run_youtube_agent)
        future_social = executor.submit(run_social_agent)
        future_email = executor.submit(run_email_agent)
        
        # Gather results
        blog_data = future_blog.result()
        youtube_data = future_youtube.result()
        social_data = future_social.result()
        email_data = future_email.result()
    
    # --- MERGE RESULTS ---
    
    # 1. Safely extract Twitter Thread
    twitter_thread = social_data.get('twitter_thread', [])
    if not twitter_thread:
        # Try fallbacks
        twitter_thread = social_data.get('x_thread', [])
        
    # 2. Safely extract LinkedIn
    linkedin_data = social_data.get('linkedin', {})
    if not linkedin_data.get('post_text'):
        # Try fallbacks
        linkedin_data['post_text'] = linkedin_data.get('text') or linkedin_data.get('content') or ''

    result = {
        'long_blog': blog_data,
        'youtube': youtube_data,
        'linkedin': linkedin_data,
        'twitter_thread': twitter_thread,
        'email_newsletter': email_data,
        'meta': {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'model': 'gpt-4o (Multi-Agent)',
            'strategy': 'Dedicated Agents',
        }
    }
    
    logger.info("Multi-Agent generation completed successfully")
    return result


# --- Synchronous Helper Functions (GPT-4o) ---

def extract_topic_from_text_openai(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract the main topic in 2-4 words. Be specific."},
                {"role": "user", "content": text[:1000]}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except:
        return "General Industry Trends"

def generate_hooks_openai(topic, count=5):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Generate {count} viral hooks. Styles: Contrarian, Story, Data-driven. Return JSON array."},
                {"role": "user", "content": topic}
            ],
            response_format={"type": "json_object"}
        )
        data = json.loads(clean_json_response(response.choices[0].message.content))
        return data.get("hooks", [])
    except:
        return []

def get_embeddings_openai(texts):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-large", 
            input=texts if isinstance(texts, list) else [texts],
            dimensions=3072
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        logger.error(f"Embedding Error: {e}")
        return []