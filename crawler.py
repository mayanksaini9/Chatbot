import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Optional

class WebsiteCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def crawl(self, url: str) -> Optional[Dict[str, str]]:
        """
        Crawl a website and extract meaningful content.

        Args:
            url: The website URL to crawl

        Returns:
            Dictionary containing title and content, or None if failed
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                raise ValueError("Invalid URL format")

            # Make request
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_content(soup, url)

            if not content.strip():
                return None

            return {
                'title': title,
                'content': content,
                'url': url
            }

        except requests.RequestException as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Error crawling website: {str(e)}")

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme)
        except:
            return False

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return "Untitled Page"

    def _extract_content(self, soup: BeautifulSoup, base_url: str) -> str:
        """
        Extract meaningful content from the webpage, removing irrelevant sections.
        """
        # Remove unwanted elements
        self._remove_unwanted_elements(soup)

        # Extract text from remaining elements
        content_parts = []

        # Try to find main content areas
        main_content = self._find_main_content(soup)
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            if text:
                content_parts.append(text)

        # If no main content found, extract from body
        if not content_parts:
            body = soup.find('body')
            if body:
                text = body.get_text(separator=' ', strip=True)
                content_parts.append(text)

        # Clean and normalize text
        content = ' '.join(content_parts)
        content = self._clean_text(content)

        return content

    def _remove_unwanted_elements(self, soup: BeautifulSoup):
        """Remove headers, footers, navigation, ads, etc."""
        # Common selectors for unwanted content
        unwanted_selectors = [
            'header', 'footer', 'nav', 'aside',
            '.header', '.footer', '.navigation', '.nav',
            '.sidebar', '.advertisement', '.ads', '.ad',
            '.menu', '.navbar', '.footer-links',
            'script', 'style', 'noscript',
            '.social-share', '.share-buttons',
            '.cookie-banner', '.popup', '.modal'
        ]

        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

    def _find_main_content(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Try to find the main content area."""
        # Common main content selectors
        main_selectors = [
            'main', 'article', '.main-content', '.content',
            '.post-content', '.entry-content', '#main',
            '#content', '.article-body', '.post-body'
        ]

        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                return main_content

        return None

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove very short lines (likely navigation or menus)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Keep lines longer than 20 characters
                cleaned_lines.append(line)

        text = ' '.join(cleaned_lines)

        # Remove excessive punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        return text.strip()
