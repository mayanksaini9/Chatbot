"""
Utility functions for the website chatbot application.
"""

import re
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.

    Args:
        url: URL string to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
    except:
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing or replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(' .')
    # Limit length
    return sanitized[:100] if sanitized else 'unnamed'

def format_metadata(metadata: Dict[str, Any]) -> str:
    """
    Format metadata for display.

    Args:
        metadata: Metadata dictionary

    Returns:
        Formatted metadata string
    """
    formatted = []
    if 'source_url' in metadata:
        formatted.append(f"Source: {metadata['source_url']}")
    if 'page_title' in metadata:
        formatted.append(f"Title: {metadata['page_title']}")
    if 'chunk_index' in metadata and 'total_chunks' in metadata:
        formatted.append(f"Chunk: {metadata['chunk_index'] + 1}/{metadata['total_chunks']}")

    return " | ".join(formatted)

def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def count_tokens(text: str) -> int:
    """
    Estimate token count for text (rough approximation).

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters for English text
    return len(text) // 4

def clean_html_text(text: str) -> str:
    """
    Clean HTML entities and extra whitespace from text.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    import html

    # Unescape HTML entities
    text = html.unescape(text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    return text

def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.

    Args:
        url: URL string

    Returns:
        Domain name or None if invalid URL
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None
