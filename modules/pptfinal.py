"""
AI Content Generation and PowerPoint Creation Module
Handles AI-powered content generation and PowerPoint file creation
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import logging

logger = logging.getLogger(__name__)

# Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

def generate_ai_content(topic: str, num_slides: int, api_key: str) -> Optional[List[Dict[str, Any]]]:
    """
    Generate AI-powered presentation content using OpenRouter API
    
    Args:
        topic: The presentation topic
        num_slides: Number of slides to generate
        api_key: OpenRouter API key
        
    Returns:
        List of slide content dictionaries or None if failed
    """
    if not api_key:
        logger.error("No OpenRouter API key provided")
        return None
    
    try:
        # Create a comprehensive prompt for presentation generation
        prompt = f"""
        Create a professional presentation about "{topic}" with {num_slides} slides.
        
        For each slide, provide:
        1. A clear, engaging title
        2. Key points or bullet points (3-5 points per slide)
        3. A brief description of what should be included
        
        Format the response as a JSON array with each slide containing:
        - title: The slide title
        - content: Main content points as an array of strings
        - description: Brief description of the slide's purpose
        
        Make the content informative, engaging, and well-structured.
        Focus on the most important aspects of {topic}.
        """
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://coxist-ai.com",
            "X-Title": "AI Presentation Generator"
        }
        
        data = {
            "model": DEFAULT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert presentation creator. Generate clear, engaging, and professional presentation content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        logger.info(f"Generating AI content for topic: {topic}")
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parse the JSON response
            try:
                slides_data = json.loads(content)
                if isinstance(slides_data, list):
                    logger.info(f"Successfully generated {len(slides_data)} slides")
                    return slides_data
                else:
                    logger.error("AI response is not a list")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                # Fallback: create basic slides from the text
                return create_fallback_slides(topic, num_slides, content)
        else:
            logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
            return create_fallback_slides(topic, num_slides)
            
    except Exception as e:
        logger.error(f"Error generating AI content: {str(e)}")
        return create_fallback_slides(topic, num_slides)

def create_fallback_slides(topic: str, num_slides: int, ai_content: str = "") -> List[Dict[str, Any]]:
    """
    Create fallback slides when AI generation fails
    
    Args:
        topic: The presentation topic
        num_slides: Number of slides to create
        ai_content: Any AI content that was generated
        
    Returns:
        List of basic slide content
    """
    slides = []
    
    # Title slide
    slides.append({
        "title": f"Introduction to {topic}",
        "content": [
            f"Welcome to our presentation on {topic}",
            "We'll explore key concepts and insights",
            "Let's dive into the details"
        ],
        "description": "Introduction and overview"
    })
    
    # Content slides
    for i in range(1, num_slides - 1):
        slides.append({
            "title": f"Key Point {i}",
            "content": [
                f"Important aspect {i} of {topic}",
                "Supporting information and details",
                "Relevant examples and applications"
            ],
            "description": f"Key point {i} discussion"
        })
    
    # Conclusion slide
    slides.append({
        "title": "Summary and Next Steps",
        "content": [
            f"Key takeaways about {topic}",
            "Important conclusions",
            "Recommended next steps"
        ],
        "description": "Summary and conclusion"
    })
    
    return slides

def create_powerpoint(slides_data: List[Dict[str, Any]], topic: str) -> Optional[str]:
    """
    Create a PowerPoint presentation from slide data
    
    Args:
        slides_data: List of slide content dictionaries
        topic: The presentation topic
        
    Returns:
        Path to the created PowerPoint file or None if failed
    """
    try:
        # Create presentation
        prs = Presentation()
        
        # Set slide size to 16:9
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)
        
        for i, slide_data in enumerate(slides_data):
            # Choose layout based on slide number
            if i == 0:
                # Title slide
                slide_layout = prs.slide_layouts[0]  # Title slide layout
                slide = prs.slides.add_slide(slide_layout)
                
                # Set title
                title = slide.shapes.title
                title.text = slide_data.get("title", f"Slide {i+1}")
                
                # Set subtitle if available
                if slide.shapes.placeholders:
                    subtitle = slide.shapes.placeholders[1]
                    subtitle.text = f"AI Generated Presentation\n{topic}"
                    
            else:
                # Content slide
                slide_layout = prs.slide_layouts[1]  # Title and content layout
                slide = prs.slides.add_slide(slide_layout)
                
                # Set title
                title = slide.shapes.title
                title.text = slide_data.get("title", f"Slide {i+1}")
                
                # Add content
                content = slide_data.get("content", [])
                if content and slide.shapes.placeholders:
                    content_placeholder = slide.shapes.placeholders[1]
                    text_frame = content_placeholder.text_frame
                    text_frame.clear()
                    
                    for j, point in enumerate(content):
                        if j == 0:
                            p = text_frame.paragraphs[0]
                        else:
                            p = text_frame.add_paragraph()
                        p.text = point
                        p.level = 0  # Top level bullet
        
        # Save the presentation
        filename = f"presentation_{topic.replace(' ', '_').lower()}_{int(time.time())}.pptx"
        filepath = os.path.join("generated_ppts", filename)
        
        # Ensure directory exists
        os.makedirs("generated_ppts", exist_ok=True)
        
        prs.save(filepath)
        logger.info(f"PowerPoint created successfully: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error creating PowerPoint: {str(e)}")
        return None

def enhance_slide_design(slide, slide_data: Dict[str, Any]):
    """
    Enhance slide design with better formatting and styling
    
    Args:
        slide: The slide object to enhance
        slide_data: Data for the slide
    """
    try:
        # Set title formatting
        if slide.shapes.title:
            title = slide.shapes.title
            title.text_frame.paragraphs[0].font.size = Pt(44)
            title.text_frame.paragraphs[0].font.bold = True
            title.text_frame.paragraphs[0].font.color.rgb = RGBColor(31, 73, 125)
        
        # Set content formatting
        for shape in slide.shapes:
            if hasattr(shape, 'text_frame'):
                for paragraph in shape.text_frame.paragraphs:
                    if paragraph.text.strip():
                        paragraph.font.size = Pt(18)
                        paragraph.font.color.rgb = RGBColor(68, 68, 68)
                        
    except Exception as e:
        logger.warning(f"Error enhancing slide design: {str(e)}")

# Import time module for timestamp
import time 