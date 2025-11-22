"""
Robust "Search-First" Web Scrapers
Uses DuckDuckGo to bypass blog index pagination and find relevant trends dynamically.
"""
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from duckduckgo_search import DDGS
from readability import Document
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class BaseScraper:
    """Base class using DDGS for discovery and requests for extraction"""
    
    def __init__(self):
        self.ddgs = DDGS()
        # Mimic a real browser to avoid 403 blocks on extraction
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }
    
    def search_domain(self, domain: str, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search a specific domain for recent articles instead of scraping index pages.
        This bypasses complex pagination and bot protection on listing pages.
        """
        try:
            # Construct a site-specific query
            search_query = f"site:{domain} {query}"
            results = self.ddgs.text(search_query, max_results=max_results)
            return results if results else []
        except Exception as e:
            logger.error(f"Search failed for {domain}: {e}")
            return []

    def fetch_and_parse(self, url: str) -> Optional[Dict]:
        """Fetch article content using readability for clean extraction"""
        try:
            # Add random delay to be polite
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            # Use Readability to strip sidebars/ads automatically
            doc = Document(response.text)
            title = doc.title()
            clean_html = doc.summary()
            
            # Convert HTML to clean text
            soup = BeautifulSoup(clean_html, 'html.parser')
            text = soup.get_text(separator='\n\n').strip()
            
            if len(text) < 500:  # Skip thin content/login walls
                return None
                
            return {
                'title': title,
                'full_text': text,
                'snippet': text[:500].replace('\n', ' ') + "..."
            }
        except Exception as e:
            logger.warning(f"Failed to parse {url}: {e}")
            return None

    def scrape(self, topic: str = "social media trends 2024") -> List[Dict]:
        raise NotImplementedError


class SproutSocialScraper(BaseScraper):
    def scrape(self, topic: str = "social media marketing trends") -> List[Dict]:
        logger.info(f"Searching Sprout Social for: {topic}")
        domain = "sproutsocial.com/insights"
        
        # Search for relevant articles
        search_results = self.search_domain(domain, topic, max_results=5)
        articles = []
        
        for res in search_results:
            url = res.get('href')
            if not url: continue
            
            data = self.fetch_and_parse(url)
            if data:
                articles.append({
                    'source': 'sprout_social',
                    'title': data['title'],
                    'url': url,
                    'snippet': data['snippet'],
                    'full_text': data['full_text'],
                    'published_date': datetime.now(), # DDGS doesn't always give date, assume recent due to query
                    'tags': ['Marketing', 'Trends']
                })
        
        return articles


class LaterBlogScraper(BaseScraper):
    def scrape(self, topic: str = "instagram tiktok trends") -> List[Dict]:
        logger.info(f"Searching Later Blog for: {topic}")
        domain = "later.com/blog"
        
        search_results = self.search_domain(domain, topic, max_results=5)
        articles = []
        
        for res in search_results:
            url = res.get('href')
            if not url: continue
            
            data = self.fetch_and_parse(url)
            if data:
                articles.append({
                    'source': 'later',
                    'title': data['title'],
                    'url': url,
                    'snippet': data['snippet'],
                    'full_text': data['full_text'],
                    'published_date': datetime.now(),
                    'tags': ['Social Media', 'Instagram']
                })
        
        return articles


class SocialMediaExaminerScraper(BaseScraper):
    def scrape(self, topic: str = "social media updates") -> List[Dict]:
        logger.info(f"Searching SM Examiner for: {topic}")
        domain = "socialmediaexaminer.com"
        
        search_results = self.search_domain(domain, topic, max_results=5)
        articles = []
        
        for res in search_results:
            url = res.get('href')
            if not url: continue
            
            data = self.fetch_and_parse(url)
            if data:
                articles.append({
                    'source': 'social_media_examiner',
                    'title': data['title'],
                    'url': url,
                    'snippet': data['snippet'],
                    'full_text': data['full_text'],
                    'published_date': datetime.now(),
                    'tags': ['News', 'Updates']
                })
        
        return articles


def get_scraper(source: str) -> BaseScraper:
    scrapers = {
        'sprout_social': SproutSocialScraper,
        'later': LaterBlogScraper,
        'social_media_examiner': SocialMediaExaminerScraper,
    }
    return scrapers.get(source, SproutSocialScraper)()