"""
AI-Powered Design Analyzer
Analyzes content and generates innovative design specifications for frames and collages
"""
import logging
import openai
from django.conf import settings
import json
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

openai.api_key = settings.OPENAI_API_KEY


class DesignAnalyzer:
    """Analyzes content and generates context-aware design specifications"""
    
    # Design themes based on content analysis
    DESIGN_THEMES = {
        'tech': {
            'colors': ['#0066FF', '#00D4FF', '#6366F1', '#8B5CF6'],
            'frame_style': 'futuristic',
            'layout': 'geometric',
            'effects': ['glow', 'gradient', 'tech_grid']
        },
        'business': {
            'colors': ['#1E40AF', '#065F46', '#7C3AED', '#DC2626'],
            'frame_style': 'professional',
            'layout': 'balanced',
            'effects': ['shadow', 'subtle_gradient']
        },
        'creative': {
            'colors': ['#F59E0B', '#EC4899', '#8B5CF6', '#10B981'],
            'frame_style': 'artistic',
            'layout': 'dynamic',
            'effects': ['splash', 'artistic_border', 'texture']
        },
        'luxury': {
            'colors': ['#92400E', '#78350F', '#1F2937', '#CA8A04'],
            'frame_style': 'elegant',
            'layout': 'refined',
            'effects': ['gold_accent', 'marble', 'emboss']
        },
        'health': {
            'colors': ['#059669', '#14B8A6', '#06B6D4', '#10B981'],
            'frame_style': 'clean',
            'layout': 'organic',
            'effects': ['soft_shadow', 'nature_gradient']
        },
        'education': {
            'colors': ['#2563EB', '#7C3AED', '#059669', '#DC2626'],
            'frame_style': 'structured',
            'layout': 'orderly',
            'effects': ['notebook', 'clean_lines']
        },
        'entertainment': {
            'colors': ['#DC2626', '#F59E0B', '#8B5CF6', '#EC4899'],
            'frame_style': 'bold',
            'layout': 'energetic',
            'effects': ['neon', 'spotlight', 'vibrant_gradient']
        },
        'finance': {
            'colors': ['#065F46', '#1E40AF', '#78350F', '#1F2937'],
            'frame_style': 'trustworthy',
            'layout': 'stable',
            'effects': ['professional_gradient', 'clean_border']
        }
    }
    
    @staticmethod
    def analyze_content(text: str) -> Dict:
        """
        Analyze content using AI to determine themes, mood, and design preferences
        
        Args:
            text: Content text to analyze
            
        Returns:
            Dict with analysis results and design specifications
        """
        try:
            # Truncate text if too long
            analysis_text = text[:3000] if len(text) > 3000 else text
            
            prompt = f"""Analyze this content and provide design recommendations for image frames and collages.

Content:
{analysis_text}

Provide a JSON response with:
1. primary_theme: One of [tech, business, creative, luxury, health, education, entertainment, finance]
2. mood: One of [professional, energetic, calm, bold, elegant, modern, playful, serious]
3. color_scheme: Description of ideal colors (warm, cool, vibrant, muted, etc.)
4. industry: The industry or field this content relates to
5. design_style: One of [minimal, maximalist, geometric, organic, industrial, artistic]
6. key_concepts: List of 3-5 key themes from the content
7. visual_metaphors: 2-3 visual metaphors that could represent this content

Return only valid JSON, no other text."""

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a design expert who analyzes content and recommends visual design specifications. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = json.loads(result_text)
            
            logger.info(f"Content analysis complete: {analysis.get('primary_theme', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            # Return default analysis
            return {
                'primary_theme': 'business',
                'mood': 'professional',
                'color_scheme': 'balanced',
                'industry': 'general',
                'design_style': 'minimal',
                'key_concepts': ['content', 'information', 'communication'],
                'visual_metaphors': ['connection', 'growth']
            }
    
    @staticmethod
    def generate_design_specs(analysis: Dict, num_images: int) -> Dict:
        """
        Generate specific design specifications based on content analysis
        
        Args:
            analysis: Content analysis results
            num_images: Number of images to design for
            
        Returns:
            Dict with detailed design specifications
        """
        theme = analysis.get('primary_theme', 'business')
        theme_config = DesignAnalyzer.DESIGN_THEMES.get(theme, DesignAnalyzer.DESIGN_THEMES['business'])
        
        # Generate frame specifications for each image
        frame_specs = []
        for i in range(num_images):
            spec = {
                'color': theme_config['colors'][i % len(theme_config['colors'])],
                'style': theme_config['frame_style'],
                'width': 50 if theme_config['frame_style'] in ['elegant', 'luxury'] else 40,
                'effects': theme_config['effects'][i % len(theme_config['effects'])],
                'border_style': DesignAnalyzer._get_border_style(theme_config['frame_style']),
                'gradient': DesignAnalyzer._get_gradient_colors(theme_config['colors'], i)
            }
            frame_specs.append(spec)
        
        # Generate collage specifications
        collage_spec = {
            'layout': theme_config['layout'],
            'background_color': DesignAnalyzer._get_background_color(theme, analysis.get('mood', 'professional')),
            'spacing': 25 if theme == 'luxury' else 20,
            'border_radius': 15 if analysis.get('design_style') in ['modern', 'minimal'] else 0,
            'overlay_effect': theme_config['effects'][0],
            'header_design': {
                'show': True,
                'text': analysis.get('key_concepts', [])[0] if analysis.get('key_concepts') else None,
                'color': theme_config['colors'][0]
            }
        }
        
        return {
            'theme': theme,
            'mood': analysis.get('mood', 'professional'),
            'frame_specs': frame_specs,
            'collage_spec': collage_spec,
            'key_concepts': analysis.get('key_concepts', []),
            'visual_metaphors': analysis.get('visual_metaphors', [])
        }
    
    @staticmethod
    def _get_border_style(frame_style: str) -> str:
        """Get border style based on frame style"""
        style_map = {
            'futuristic': 'double_line',
            'professional': 'solid',
            'artistic': 'brushstroke',
            'elegant': 'ornate',
            'clean': 'thin',
            'structured': 'grid',
            'bold': 'thick',
            'trustworthy': 'solid_shadow'
        }
        return style_map.get(frame_style, 'solid')
    
    @staticmethod
    def _get_gradient_colors(colors: List[str], index: int) -> Tuple[str, str]:
        """Generate gradient color pair"""
        primary = colors[index % len(colors)]
        secondary = colors[(index + 1) % len(colors)]
        return (primary, secondary)
    
    @staticmethod
    def _get_background_color(theme: str, mood: str) -> str:
        """Get background color based on theme and mood"""
        if mood in ['calm', 'professional', 'elegant']:
            base_colors = {
                'tech': '#F0F9FF',
                'business': '#F8FAFC',
                'creative': '#FFF7ED',
                'luxury': '#FAFAF9',
                'health': '#F0FDF4',
                'education': '#EFF6FF',
                'entertainment': '#FEF2F2',
                'finance': '#ECFDF5'
            }
        else:  # energetic, bold, playful
            base_colors = {
                'tech': '#DBEAFE',
                'business': '#E0E7FF',
                'creative': '#FED7AA',
                'luxury': '#E7E5E4',
                'health': '#D1FAE5',
                'education': '#DBEAFE',
                'entertainment': '#FEE2E2',
                'finance': '#D1FAE5'
            }
        
        return base_colors.get(theme, '#F8FAFC')
    
    @staticmethod
    def generate_collage_prompt(analysis: Dict) -> str:
        """
        Generate a descriptive prompt for AI-based collage generation
        
        Args:
            analysis: Content analysis results
            
        Returns:
            Descriptive prompt for the collage design
        """
        theme = analysis.get('primary_theme', 'business')
        mood = analysis.get('mood', 'professional')
        concepts = analysis.get('key_concepts', [])
        metaphors = analysis.get('visual_metaphors', [])
        
        prompt_parts = [
            f"Create a {mood} and {theme}-themed visual design",
            f"incorporating these concepts: {', '.join(concepts[:3])}",
        ]
        
        if metaphors:
            prompt_parts.append(f"using visual metaphors of {' and '.join(metaphors[:2])}")
        
        return '. '.join(prompt_parts)
