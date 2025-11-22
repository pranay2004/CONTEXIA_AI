"""
Unified AI wrapper that switches between OpenAI and Gemini
"""
import os
import logging

logger = logging.getLogger(__name__)

AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai').lower()


def generate_content(extracted_text, trend_snippets, platforms):
    """
    Generate content using configured AI provider
    """
    if AI_PROVIDER == 'openai':
        from .openai_wrapper import generate_content_with_openai
        return generate_content_with_openai(extracted_text, trend_snippets, platforms)
    else:
        from .gemini_wrapper import generate_content_with_gemini
        return generate_content_with_gemini(extracted_text, trend_snippets, platforms)


def extract_topic_from_text(text):
    """
    Extract topic using configured AI provider
    """
    if AI_PROVIDER == 'openai':
        from .openai_wrapper import extract_topic_from_text_openai
        return extract_topic_from_text_openai(text)
    else:
        from .gemini_wrapper import extract_topic_from_text as gemini_extract
        return gemini_extract(text)


def generate_hooks(topic, count=5):
    """
    Generate hooks using configured AI provider
    """
    if AI_PROVIDER == 'openai':
        from .openai_wrapper import generate_hooks_openai
        return generate_hooks_openai(topic, count)
    else:
        from .gemini_wrapper import generate_hooks as gemini_hooks
        return gemini_hooks(topic, count)


def get_embeddings(texts):
    """
    Generate embeddings using configured AI provider
    """
    if AI_PROVIDER == 'openai':
        from .openai_wrapper import get_embeddings_openai
        return get_embeddings_openai(texts)
    else:
        # Gemini embeddings
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            
            if isinstance(texts, list):
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=texts,
                    task_type="retrieval_document"
                )
                return result['embedding']
            else:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=texts,
                    task_type="retrieval_query"
                )
                return [result['embedding']]
        except Exception as e:
            logger.error(f"Error with Gemini embeddings: {str(e)}")
            raise
