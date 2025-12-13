import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
import re
import logging
from urllib.parse import urlparse

from schemas.models import JobDescription

logger = logging.getLogger(__name__)


class JobDescriptionLoader:
    """Loader for fetching and parsing job descriptions from URLs"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def load(self, url: str) -> JobDescription:
        """
        Fetch and parse job description from URL.

        Args:
            url: The job posting URL

        Returns:
            JobDescription: Parsed job description data

        Raises:
            ValueError: If URL is invalid or content cannot be parsed
            httpx.HTTPError: If HTTP request fails
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                content = response.text

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise

        # Parse the HTML content
        parsed_data = self._parse_html_content(content, url)

        return JobDescription(
            url=url,
            **parsed_data
        )

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False

    def _parse_html_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content to extract job description components.

        This is a heuristic-based parser that looks for common patterns
        in job posting HTML. May need tuning for specific job boards.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title = self._extract_title(soup, url)

        # Extract text content
        text_content = soup.get_text(separator='\n', strip=True)

        # Parse different sections
        responsibilities = self._extract_responsibilities(text_content)
        requirements = self._extract_requirements(text_content)
        role_summary = self._extract_role_summary(text_content, title)
        company_context = self._extract_company_context(text_content, url)

        return {
            "title": title,
            "responsibilities": responsibilities,
            "requirements": requirements,
            "role_summary": role_summary,
            "company_context": company_context,
        }

    def _extract_title(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract job title from HTML"""
        # Try common title selectors
        title_selectors = [
            'h1',
            '.job-title',
            '.position-title',
            '[data-testid="job-title"]',
            'title'
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:  # Reasonable title length
                    return title

        # Fallback: extract from URL or page title
        page_title = soup.find('title')
        if page_title:
            title_text = page_title.get_text(strip=True)
            # Try to extract job title from page title
            # Common patterns: "Job Title | Company" or "Company - Job Title"
            if '|' in title_text:
                parts = title_text.split('|')
                title = parts[0].strip()
            elif '-' in title_text:
                parts = title_text.split('-')
                title = parts[-1].strip()
            else:
                title = title_text

            if len(title) > 5:
                return title

        return None

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract responsibilities from text content"""
        responsibilities = []

        # Look for responsibility sections
        resp_patterns = [
            r'Responsibilities?:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'What you\'?ll do:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Role responsibilities:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Key responsibilities:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
        ]

        for pattern in resp_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                items = self._parse_list_items(match)
                responsibilities.extend(items)

        # Remove duplicates and empty items
        responsibilities = list(set(filter(None, responsibilities)))

        return responsibilities[:10]  # Limit to top 10

    def _extract_requirements(self, text: str) -> List[str]:
        """Extract requirements from text content"""
        requirements = []

        # Look for requirements sections
        req_patterns = [
            r'Requirements?:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'What you need:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Qualifications:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Skills required:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'You have:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
        ]

        for pattern in req_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                items = self._parse_list_items(match)
                requirements.extend(items)

        # Remove duplicates and empty items
        requirements = list(set(filter(None, requirements)))

        return requirements[:10]  # Limit to top 10

    def _extract_role_summary(self, text: str, title: Optional[str]) -> str:
        """Extract or generate role summary"""
        # Try to find a summary section
        summary_patterns = [
            r'About the role:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Job summary:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Position summary:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Overview:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
        ]

        for pattern in summary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                summary = match.strip()
                if len(summary) > 50:  # Reasonable summary length
                    return summary

        # Fallback: generate summary from title and first few sentences
        if title:
            # Find the first paragraph after the title
            lines = text.split('\n')
            summary_parts = []

            for line in lines:
                line = line.strip()
                if line and len(line) > 20:
                    summary_parts.append(line)
                    if len(summary_parts) >= 3:  # First 3 substantial lines
                        break

            if summary_parts:
                return f"{title}. {' '.join(summary_parts)}"

        # Final fallback
        return f"This is a {title or 'job'} position requiring specific skills and experience."

    def _extract_company_context(self, text: str, url: str) -> str:
        """Extract company information from text or URL"""
        # Try to find company description
        company_patterns = [
            r'About us:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'About the company:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Who we are:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
            r'Company description:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)',
        ]

        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                context = match.strip()
                if len(context) > 30:  # Reasonable context length
                    return context

        # Extract company from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]

        # Common domain to company name mappings
        domain_hints = {
            'linkedin.com': 'LinkedIn',
            'indeed.com': 'Indeed',
            'glassdoor.com': 'Glassdoor',
            'monster.com': 'Monster',
            'dice.com': 'Dice',
            'ziprecruiter.com': 'ZipRecruiter',
        }

        if domain in domain_hints:
            return f"This position is posted on {domain_hints[domain]}, a leading job platform."

        # Try to extract company name from domain
        company_name = domain.split('.')[0].title()
        return f"This is a position at {company_name}."

    def _parse_list_items(self, text: str) -> List[str]:
        """Parse bullet points or numbered lists from text"""
        items = []

        # Split by common list markers
        lines = text.split('\n')

        for line in lines:
            line = line.strip()

            # Remove bullet points and numbering
            cleaned_line = re.sub(r'^[-\*\•]\s*', '', line)  # Bullet points
            cleaned_line = re.sub(r'^\d+\.?\s*', '', cleaned_line)  # Numbered lists

            # Only keep substantial items
            if len(cleaned_line) > 10 and not cleaned_line.startswith(('http', 'www.')):
                items.append(cleaned_line)

        return items
