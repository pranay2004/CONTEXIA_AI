"""
AI-Powered Best Time Recommendations
Using GPT-4o-mini for historical analysis
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q
import openai
from django.conf import settings

from apps.social.models import (
    SocialAccount,
    ScheduledPost,
    PublishedPostAnalytics,
    PostingSchedule
)

logger = logging.getLogger(__name__)

# Initialize OpenAI
openai.api_key = settings.OPENAI_API_KEY


class BestTimeAnalyzer:
    """Analyze historical performance to recommend optimal posting times"""
    
    def __init__(self, social_account: SocialAccount):
        self.social_account = social_account
        self.platform = social_account.platform
    
    def analyze_and_generate_recommendations(self, lookback_days: int = 90) -> List[Dict]:
        """
        Analyze historical data and generate posting time recommendations
        
        Args:
            lookback_days: Number of days to look back for analysis
            
        Returns:
            List of recommended time slots with confidence scores
        """
        # Get historical data
        historical_data = self._get_historical_data(lookback_days)
        
        if not historical_data['posts']:
            logger.info(f"No historical data for account {self.social_account.id}, using platform defaults")
            return self._get_platform_defaults()
        
        # Analyze with GPT-4o-mini
        recommendations = self._analyze_with_ai(historical_data)
        
        # Save recommendations to database
        self._save_recommendations(recommendations)
        
        return recommendations
    
    def _get_historical_data(self, lookback_days: int) -> Dict:
        """Fetch historical post performance data"""
        since = timezone.now() - timedelta(days=lookback_days)
        
        # Get published posts with analytics
        posts = ScheduledPost.objects.filter(
            social_account=self.social_account,
            status='published',
            scheduled_time__gte=since
        ).select_related('publishedpostanalytics')
        
        # Aggregate by time slots
        time_slot_data = {}
        for post in posts:
            try:
                analytics = post.publishedpostanalytics
                
                # Extract time info
                post_time = post.scheduled_time
                weekday = post_time.weekday()  # 0 = Monday, 6 = Sunday
                hour = post_time.hour
                
                key = f"{weekday}_{hour}"
                
                if key not in time_slot_data:
                    time_slot_data[key] = {
                        'weekday': weekday,
                        'hour': hour,
                        'posts': 0,
                        'total_engagement': 0,
                        'total_impressions': 0,
                        'total_reach': 0,
                        'engagement_rates': [],
                    }
                
                slot = time_slot_data[key]
                slot['posts'] += 1
                slot['total_engagement'] += (analytics.likes + analytics.comments + analytics.shares)
                slot['total_impressions'] += analytics.impressions
                slot['total_reach'] += analytics.reach
                
                # Parse engagement rate (stored as string percentage)
                try:
                    eng_rate = float(analytics.engagement_rate.rstrip('%'))
                    slot['engagement_rates'].append(eng_rate)
                except:
                    pass
                    
            except PublishedPostAnalytics.DoesNotExist:
                continue
        
        # Calculate averages
        for key, slot in time_slot_data.items():
            if slot['posts'] > 0:
                slot['avg_engagement'] = slot['total_engagement'] / slot['posts']
                slot['avg_impressions'] = slot['total_impressions'] / slot['posts']
                slot['avg_reach'] = slot['total_reach'] / slot['posts']
                if slot['engagement_rates']:
                    slot['avg_engagement_rate'] = sum(slot['engagement_rates']) / len(slot['engagement_rates'])
                else:
                    slot['avg_engagement_rate'] = 0
        
        return {
            'total_posts': posts.count(),
            'posts': list(posts.values()),
            'time_slots': time_slot_data,
            'platform': self.platform,
            'lookback_days': lookback_days,
        }
    
    def _analyze_with_ai(self, historical_data: Dict) -> List[Dict]:
        """Use GPT-4o-mini to analyze data and recommend optimal times"""
        
        # Prepare summary for AI
        time_slots_summary = []
        for key, slot in historical_data['time_slots'].items():
            weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            time_slots_summary.append({
                'day': weekday_names[slot['weekday']],
                'hour': slot['hour'],
                'posts_count': slot['posts'],
                'avg_engagement': round(slot['avg_engagement'], 2),
                'avg_engagement_rate': round(slot['avg_engagement_rate'], 2),
                'avg_impressions': round(slot['avg_impressions'], 2),
                'avg_reach': round(slot['avg_reach'], 2),
            })
        
        # Sort by engagement rate
        time_slots_summary.sort(key=lambda x: x['avg_engagement_rate'], reverse=True)
        
        # Create prompt for GPT-4o-mini
        prompt = f"""Analyze this social media posting data for {historical_data['platform']} and recommend the best 5-7 time slots for posting.

Historical Data ({historical_data['lookback_days']} days, {historical_data['total_posts']} posts):

Top Performing Time Slots:
{self._format_time_slots_for_prompt(time_slots_summary[:15])}

Platform: {historical_data['platform']}

Based on this data, recommend 5-7 optimal posting times with:
1. Day of week and hour (in 24h format)
2. Confidence score (0-100)
3. Brief reasoning (max 2 sentences)

Consider:
- Engagement rates and reach
- Posting frequency (more data = higher confidence)
- Platform-specific best practices
- Audience behavior patterns

Format your response as a JSON array with this structure:
[
  {{
    "weekday": 0-6 (0=Monday, 6=Sunday),
    "hour": 0-23,
    "confidence_score": 0-100,
    "reasoning": "explanation"
  }}
]

Only return the JSON array, no other text."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media analytics expert specializing in optimal posting time recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            
            # Parse AI response
            import json
            ai_response = response.choices[0].message.content.strip()
            
            # Extract JSON from response (in case AI adds extra text)
            json_start = ai_response.find('[')
            json_end = ai_response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                ai_response = ai_response[json_start:json_end]
            
            recommendations = json.loads(ai_response)
            
            logger.info(f"Generated {len(recommendations)} recommendations using GPT-4o-mini")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fallback to top performing time slots
            return self._fallback_recommendations(time_slots_summary)
    
    def _format_time_slots_for_prompt(self, slots: List[Dict]) -> str:
        """Format time slots data for AI prompt"""
        lines = []
        for slot in slots:
            lines.append(
                f"- {slot['day']} at {slot['hour']:02d}:00: "
                f"{slot['posts_count']} posts, "
                f"{slot['avg_engagement_rate']:.1f}% engagement rate, "
                f"{slot['avg_engagement']:.0f} avg interactions"
            )
        return '\n'.join(lines)
    
    def _fallback_recommendations(self, time_slots_summary: List[Dict]) -> List[Dict]:
        """Fallback recommendations based on top performing slots"""
        recommendations = []
        
        # Take top 5-7 slots
        for slot in time_slots_summary[:7]:
            weekday_map = {
                'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                'Friday': 4, 'Saturday': 5, 'Sunday': 6
            }
            
            # Calculate confidence based on sample size
            confidence = min(100, slot['posts_count'] * 10 + 50)
            
            recommendations.append({
                'weekday': weekday_map.get(slot['day'], 0),
                'hour': slot['hour'],
                'confidence_score': confidence,
                'reasoning': f"Based on {slot['posts_count']} posts with {slot['avg_engagement_rate']:.1f}% engagement rate"
            })
        
        return recommendations
    
    def _get_platform_defaults(self) -> List[Dict]:
        """Return platform-specific default best times when no historical data"""
        
        defaults = {
            'linkedin': [
                {'weekday': 1, 'hour': 8, 'confidence_score': 60, 'reasoning': 'LinkedIn best practice: Tuesday morning before work'},
                {'weekday': 2, 'hour': 12, 'confidence_score': 60, 'reasoning': 'LinkedIn best practice: Wednesday lunch hour'},
                {'weekday': 3, 'hour': 9, 'confidence_score': 60, 'reasoning': 'LinkedIn best practice: Thursday morning'},
                {'weekday': 1, 'hour': 17, 'confidence_score': 55, 'reasoning': 'LinkedIn best practice: Tuesday after work'},
                {'weekday': 4, 'hour': 8, 'confidence_score': 55, 'reasoning': 'LinkedIn best practice: Friday morning'},
            ],
            'twitter': [
                {'weekday': 2, 'hour': 9, 'confidence_score': 60, 'reasoning': 'Twitter best practice: Wednesday morning commute'},
                {'weekday': 1, 'hour': 12, 'confidence_score': 60, 'reasoning': 'Twitter best practice: Tuesday lunch'},
                {'weekday': 4, 'hour': 11, 'confidence_score': 60, 'reasoning': 'Twitter best practice: Friday late morning'},
                {'weekday': 3, 'hour': 15, 'confidence_score': 55, 'reasoning': 'Twitter best practice: Thursday afternoon'},
                {'weekday': 6, 'hour': 13, 'confidence_score': 55, 'reasoning': 'Twitter best practice: Sunday afternoon'},
            ],
            'facebook': [
                {'weekday': 2, 'hour': 13, 'confidence_score': 60, 'reasoning': 'Facebook best practice: Wednesday afternoon'},
                {'weekday': 3, 'hour': 11, 'confidence_score': 60, 'reasoning': 'Facebook best practice: Thursday late morning'},
                {'weekday': 4, 'hour': 10, 'confidence_score': 60, 'reasoning': 'Facebook best practice: Friday morning'},
                {'weekday': 5, 'hour': 12, 'confidence_score': 55, 'reasoning': 'Facebook best practice: Saturday noon'},
                {'weekday': 6, 'hour': 14, 'confidence_score': 55, 'reasoning': 'Facebook best practice: Sunday afternoon'},
            ],
            'instagram': [
                {'weekday': 2, 'hour': 11, 'confidence_score': 60, 'reasoning': 'Instagram best practice: Wednesday late morning'},
                {'weekday': 4, 'hour': 14, 'confidence_score': 60, 'reasoning': 'Instagram best practice: Friday afternoon'},
                {'weekday': 6, 'hour': 10, 'confidence_score': 60, 'reasoning': 'Instagram best practice: Sunday morning'},
                {'weekday': 1, 'hour': 19, 'confidence_score': 55, 'reasoning': 'Instagram best practice: Tuesday evening'},
                {'weekday': 5, 'hour': 15, 'confidence_score': 55, 'reasoning': 'Instagram best practice: Saturday afternoon'},
            ],
        }
        
        return defaults.get(self.platform, defaults['linkedin'])
    
    def _save_recommendations(self, recommendations: List[Dict]) -> None:
        """Save recommendations to database"""
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Deactivate old recommendations
        PostingSchedule.objects.filter(
            social_account=self.social_account,
            is_active=True
        ).update(is_active=False)
        
        # Create new recommendations
        for rec in recommendations:
            PostingSchedule.objects.create(
                social_account=self.social_account,
                weekday=rec['weekday'],
                hour=rec['hour'],
                minute=0,  # Default to top of hour
                confidence_score=rec['confidence_score'],
                reasoning=rec['reasoning'],
                historical_data={'analyzed_at': timezone.now().isoformat()},
                is_active=True,
            )
        
        logger.info(f"Saved {len(recommendations)} recommendations for account {self.social_account.id}")


def generate_recommendations_for_account(social_account_id: int, lookback_days: int = 90) -> List[Dict]:
    """
    Generate best time recommendations for a social account
    
    Args:
        social_account_id: SocialAccount ID
        lookback_days: Days of historical data to analyze
        
    Returns:
        List of time slot recommendations
    """
    try:
        account = SocialAccount.objects.get(id=social_account_id)
        analyzer = BestTimeAnalyzer(account)
        return analyzer.analyze_and_generate_recommendations(lookback_days)
    except SocialAccount.DoesNotExist:
        logger.error(f"Social account {social_account_id} not found")
        return []
