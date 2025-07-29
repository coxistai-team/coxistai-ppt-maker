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
        
        IMPORTANT: You must respond with ONLY a valid JSON array. Do not include any other text, explanations, or markdown formatting.
        
        Format the response as a JSON array with each slide containing:
        - title: The slide title (string)
        - content: Main content points as an array of strings
        - description: Brief description of the slide's purpose (string)
        
        Example format:
        [
          {{
            "title": "Introduction",
            "content": ["Point 1", "Point 2", "Point 3"],
            "description": "Overview of the topic"
          }},
          {{
            "title": "Key Concepts",
            "content": ["Concept 1", "Concept 2", "Concept 3"],
            "description": "Main concepts to understand"
          }}
        ]
        
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
            
            logger.info(f"Raw AI response: {content[:200]}...")  # Log first 200 chars
            
            # Parse the JSON response
            try:
                slides_data = json.loads(content)
                if isinstance(slides_data, list):
                    logger.info(f"Successfully generated {len(slides_data)} slides")
                    return slides_data
                else:
                    logger.error(f"AI response is not a list, got: {type(slides_data)}")
                    logger.error(f"Response content: {content}")
                    return create_fallback_slides(topic, num_slides, content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Raw content: {content}")
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
    
    # Try to extract useful content from AI response if available
    extracted_content = []
    if ai_content:
        # Try to extract bullet points or key phrases
        lines = ai_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10 and not line.startswith('```'):
                # Remove markdown formatting
                line = line.replace('*', '').replace('**', '').replace('#', '')
                if line:
                    extracted_content.append(line)
    
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
        if extracted_content and i - 1 < len(extracted_content):
            # Use extracted content if available
            content_point = extracted_content[i - 1]
            slides.append({
                "title": f"Key Point {i}",
                "content": [
                    content_point,
                    "Supporting information and details",
                    "Relevant examples and applications"
                ],
                "description": f"Key point {i} discussion"
            })
        else:
            # Use generic content
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

def create_enhanced_powerpoint(slides_data: List[Dict[str, Any]], topic: str) -> Optional[str]:
    """
    Create an enhanced PowerPoint presentation from rich frontend slide data
    
    Args:
        slides_data: List of slide data with elements, backgrounds, and styling
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
            # Check if this is rich frontend data or basic AI data
            if 'elements' in slide_data and 'background' in slide_data:
                # Rich frontend data - use enhanced creation
                slide = create_enhanced_slide(prs, slide_data, i)
            else:
                # Basic AI data - use simple creation
                slide = create_basic_slide(prs, slide_data, i, topic)
        
        # Save the presentation
        filename = f"presentation_{topic.replace(' ', '_').lower()}_{int(time.time())}.pptx"
        filepath = os.path.join("generated_ppts", filename)
        
        # Ensure directory exists
        os.makedirs("generated_ppts", exist_ok=True)
        
        prs.save(filepath)
        logger.info(f"Enhanced PowerPoint created successfully: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error creating enhanced PowerPoint: {str(e)}")
        return None

def create_enhanced_slide(prs, slide_data: Dict[str, Any], slide_index: int):
    """
    Create an enhanced slide with rich styling, backgrounds, and elements
    
    Args:
        prs: Presentation object
        slide_data: Rich slide data with elements and background
        slide_index: Index of the slide
    """
    # Use blank layout for maximum customization
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)
    
    # Set background
    background = slide_data.get('background', {})
    if background.get('type') == 'gradient':
        # Create gradient background
        gradient = background.get('gradient', '')
        if 'blue' in gradient or 'purple' in gradient:
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor(59, 130, 246)  # Blue
        elif 'green' in gradient:
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor(34, 197, 94)  # Green
        elif 'red' in gradient or 'pink' in gradient:
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor(239, 68, 68)  # Red
        else:
            # Default gradient
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor(15, 23, 42)  # Slate
    else:
        # Solid background
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor(15, 23, 42)  # Dark slate
    
    # Add elements
    elements = slide_data.get('elements', [])
    for element in elements:
        element_type = element.get('type', 'text')
        content = element.get('content', '')
        position = element.get('position', {})
        style = element.get('style', {})
        
        if element_type == 'title':
            # Add title text box
            left = Inches(position.get('left', 50) / 100)
            top = Inches(position.get('top', 50) / 100)
            width = Inches(position.get('width', 800) / 100)
            height = Inches(position.get('height', 100) / 100)
            
            textbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = textbox.text_frame
            text_frame.text = content
            
            # Style the title
            paragraph = text_frame.paragraphs[0]
            paragraph.font.size = Pt(style.get('font_size', 32))
            paragraph.font.bold = style.get('font_weight') == 'bold'
            paragraph.font.color.rgb = RGBColor(255, 255, 255)  # White text
            paragraph.alignment = PP_ALIGN.CENTER
            
        elif element_type == 'text':
            # Add content text box
            left = Inches(position.get('left', 100) / 100)
            top = Inches(position.get('top', 150) / 100)
            width = Inches(position.get('width', 700) / 100)
            height = Inches(position.get('height', 50) / 100)
            
            textbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = textbox.text_frame
            text_frame.text = content
            
            # Style the text
            paragraph = text_frame.paragraphs[0]
            paragraph.font.size = Pt(style.get('font_size', 18))
            paragraph.font.color.rgb = RGBColor(255, 255, 255)  # White text
            paragraph.alignment = PP_ALIGN.LEFT
            
        elif element_type == 'bullet_list':
            # Add bullet list
            items = element.get('items', [])
            if items:
                left = Inches(position.get('left', 100) / 100)
                top = Inches(position.get('top', 150) / 100)
                width = Inches(position.get('width', 700) / 100)
                height = Inches(position.get('height', 200) / 100)
                
                textbox = slide.shapes.add_textbox(left, top, width, height)
                text_frame = textbox.text_frame
                
                for i, item in enumerate(items):
                    if i == 0:
                        p = text_frame.paragraphs[0]
                    else:
                        p = text_frame.add_paragraph()
                    p.text = f"• {item}"
                    p.font.size = Pt(style.get('font_size', 18))
                    p.font.color.rgb = RGBColor(255, 255, 255)  # White text
                    p.level = 0
                    
        elif element_type == 'image':
            # Add image if src is available
            src = element.get('src', '')
            if src and src.startswith('http'):
                try:
                    left = Inches(position.get('left', 50) / 100)
                    top = Inches(position.get('top', 50) / 100)
                    width = Inches(position.get('width', 400) / 100)
                    height = Inches(position.get('height', 300) / 100)
                    
                    # Download and add image
                    response = requests.get(src, timeout=10)
                    if response.status_code == 200:
                        img_path = f"temp_img_{slide_index}_{hash(src)}.jpg"
                        with open(img_path, 'wb') as f:
                            f.write(response.content)
                        
                        slide.shapes.add_picture(img_path, left, top, width, height)
                        
                        # Clean up temp file
                        os.remove(img_path)
                except Exception as e:
                    logger.warning(f"Could not add image {src}: {str(e)}")
    
    return slide

def create_basic_slide(prs, slide_data: Dict[str, Any], slide_index: int, topic: str):
    """
    Create a basic slide from AI-generated content
    
    Args:
        prs: Presentation object
        slide_data: Basic slide data with title and content
        slide_index: Index of the slide
        topic: Presentation topic
    """
    if slide_index == 0:
        # Title slide
        slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(slide_layout)
        
        # Set title
        title = slide.shapes.title
        title.text = slide_data.get("title", f"Slide {slide_index+1}")
        
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
        title.text = slide_data.get("title", f"Slide {slide_index+1}")
        
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
    
    return slide 