"""
Vector Store using AI Embeddings + Pure Python Similarity
Optimized for compatibility (No Numpy, No Faiss, No C++ required)
"""
import math
import logging
from django.conf import settings
from .models import TrendArticle
from pgvector.django import L2Distance
from apps.generator import ai_wrapper

logger = logging.getLogger(__name__)


class TrendVectorStore:
    def __init__(self):
        self.model_name = "embeddings"

    def generate_embedding(self, text: str) -> list:
        """Generate embedding using configured AI provider"""
        try:
            safe_text = text[:8000] 
            # The wrapper now returns a list of lists (batch ready)
            embeddings = ai_wrapper.get_embeddings([safe_text])
            
            if embeddings and len(embeddings) > 0:
                return embeddings[0] # Return the first vector
            return []
        except Exception as e:
            logger.error(f"Embedding Error: {e}")
            return []

    def cosine_similarity(self, v1: list, v2: list) -> float:
        """Compute cosine similarity between two vectors in pure python"""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)

    def add_article(self, article: TrendArticle) -> bool:
        try:
            combined_text = f"{article.title}\n{article.snippet}\n{article.full_text[:1000]}"
            embedding = self.generate_embedding(combined_text)
            
            if not embedding:
                return False

            article.embedding = embedding
            article.save(update_fields=['embedding'])
            return True
        except Exception as e:
            logger.error(f"Error adding article {article.id}: {e}")
            return False

    def search(self, query: str, k: int = 10):
        """
        Production-ready vector search using PostgreSQL + pgvector.
        Calculates distance inside the DB for maximum speed.
        """
        try:
            # 1. Generate query embedding using AI
            query_embedding = self.generate_embedding(query)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []

            # 2. DB-Native Vector Search (Fast & Scalable)
            # This query calculates the L2 distance (Euclidean) between the query vector
            # and every article's vector in the database using the HNSW index.
            # We fetch 2*k items to allow for re-ranking based on the "viral score" logic below.
            articles = TrendArticle.objects.annotate(
                distance=L2Distance('embedding', query_embedding)
            ).order_by('distance')[:k*2]

            results = []
            for art in articles:
                # 3. Calculate Similarity & Viral Score
                # L2 Distance ranges from 0 (identical) to ~2 (opposite).
                # We convert this to a 0-1 similarity score: 1 / (1 + distance)
                # Note: 'art.distance' is available because we added it in .annotate()
                
                # Handle potential None values if DB extraction failed slightly
                dist_val = art.distance if art.distance is not None else 1.0
                similarity = 1 / (1 + float(dist_val))
                
                # The Viral Score blends semantic relevance (70%) with recency (30%)
                # ensuring users see RELEVANT trends that are also FRESH.
                viral_score = (similarity * 0.7) + (art.recency_factor * 0.3)
                
                results.append({
                    'title': art.title,
                    'url': art.url,
                    'source': art.get_source_display(),
                    'snippet': art.snippet,
                    'viral_score': viral_score,
                    'similarity': similarity
                })
            
            # 4. Final Sort and Return Top K
            # Sort by the calculated viral_score descending
            return sorted(results, key=lambda x: x['viral_score'], reverse=True)[:k]
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            # Fallback: Return empty list so the app doesn't crash, 
            # allowing the generator to proceed without trends if necessary.
            return []

def get_trend_snippets(topic: str, k: int = 10):
    return TrendVectorStore().search(topic, k)