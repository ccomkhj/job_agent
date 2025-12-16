import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from schemas.models import JobDescription
from utils.error_handler import (
    AuthenticationError,
    NetworkError,
    handle_job_loading_errors,
)

logger = logging.getLogger(__name__)


class JobDescriptionLoader:
    """Loader for fetching and parsing job descriptions from URLs"""

    # Known job platforms and their characteristics
    SUPPORTED_PLATFORMS = {
        "indeed": {
            "domains": ["indeed.com"],
            "requires_login": False,
            "recommendation": "Excellent - works reliably",
        },
        "glassdoor": {
            "domains": ["glassdoor.com"],
            "requires_login": False,
            "recommendation": "Good - usually works well",
        },
        "linkedin": {
            "domains": ["linkedin.com"],
            "requires_login": True,
            "recommendation": "Requires login - try copying job description instead",
        },
        "monster": {
            "domains": ["monster.com"],
            "requires_login": False,
            "recommendation": "Good - generally works well",
        },
        "dice": {
            "domains": ["dice.com"],
            "requires_login": False,
            "recommendation": "Good - usually works",
        },
        "ziprecruiter": {
            "domains": ["ziprecruiter.com"],
            "requires_login": False,
            "recommendation": "Good - works well",
        },
        "company_careers": {
            "domains": [],  # Too many to list
            "requires_login": False,
            "recommendation": "Excellent - direct from company sites",
        },
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @handle_job_loading_errors
    async def load(self, url: str) -> JobDescription:
        """
        Fetch and parse job description from URL.

        Args:
            url: The job posting URL

        Returns:
            JobDescription: Parsed job description data

        Raises:
            JobAgentError: For various error conditions with appropriate categories
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        async with httpx.AsyncClient(
            timeout=self.timeout, follow_redirects=True
        ) as client:
            response = await client.get(url)

            # Check if we were redirected to a login/auth page
            if self._is_redirected_to_login(response, url):
                platform = self._detect_provider(url)
                error_msg = f"This job posting from {platform} requires login to view. "
                error_msg += "Try one of these alternatives:\n"
                error_msg += "• Copy and paste the job description text directly\n"
                error_msg += "• Use job postings from Indeed, Glassdoor, or company career pages\n"
                error_msg += "• Look for a 'shareable' or public link to the job"
                raise AuthenticationError(error_msg, provider=platform)

            response.raise_for_status()
            content = response.text

        # Parse the HTML content
        parsed_data = self._parse_html_content(content, url)

        return JobDescription(url=url, **parsed_data)

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format and check if it's a job-related URL"""
        try:
            parsed = urlparse(url)
            if not bool(parsed.scheme and parsed.netloc):
                return False

            # Check if it's a reasonable job URL
            url_lower = url.lower()

            # Block obviously non-job URLs
            if any(
                domain in url_lower
                for domain in [
                    "facebook.com",
                    "twitter.com",
                    "instagram.com",
                    "youtube.com",
                ]
            ):
                return False

            # Allow common job platforms and company career pages
            return True

        except:
            return False

    def _detect_provider(self, url: str) -> Optional[str]:
        """Detect the job board/provider from URL with detailed information"""
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()

        for platform, info in self.SUPPORTED_PLATFORMS.items():
            if platform == "company_careers":
                # Check for common company career page patterns
                if any(
                    pattern in url_lower
                    for pattern in ["careers", "jobs", "join", "work-at"]
                ):
                    return "Company Career Page"
            elif any(domain_part in domain for domain_part in info["domains"]):
                return platform.title()

        # Generic detection
        if "linkedin" in domain:
            return "LinkedIn"
        elif "indeed" in domain:
            return "Indeed"
        elif "glassdoor" in domain:
            return "Glassdoor"

        return "Unknown Platform"

    def _get_platform_info(self, url: str) -> Dict[str, Any]:
        """Get platform information and recommendations"""
        provider = self._detect_provider(url)
        url_lower = url.lower()

        # Default info
        info = {
            "provider": provider or "Unknown",
            "requires_login": False,
            "recommendation": "May work - try it and see",
            "tips": [],
        }

        # Check known platforms
        for platform_key, platform_info in self.SUPPORTED_PLATFORMS.items():
            if platform_key == "company_careers":
                if any(
                    pattern in url_lower
                    for pattern in ["careers", "jobs", "join", "work-at"]
                ):
                    info.update(
                        {
                            "provider": "Company Career Page",
                            "requires_login": platform_info["requires_login"],
                            "recommendation": platform_info["recommendation"],
                            "tips": [
                                "Direct company sites usually work best",
                                "Excellent choice - these work reliably",
                            ],
                        }
                    )
                    break
            elif any(domain in url_lower for domain in platform_info["domains"]):
                info.update(
                    {
                        "provider": platform_key.title(),
                        "requires_login": platform_info["requires_login"],
                        "recommendation": platform_info["recommendation"],
                    }
                )

                # Add specific tips
                if platform_key == "linkedin":
                    info["tips"] = [
                        "LinkedIn requires account login for most job details",
                        "Try copying the job description text instead",
                        'Use the "Share" link if available',
                    ]
                elif platform_key == "indeed":
                    info["tips"] = [
                        "Indeed works reliably with direct job URLs",
                        "Make sure the URL includes the job ID",
                    ]
                break

        return info

    def validate_and_analyze_url(self, url: str) -> Dict[str, Any]:
        """Validate URL and provide analysis without fetching"""
        if not self._is_valid_url(url):
            return {
                "valid": False,
                "error": "Invalid URL format. Please provide a complete URL starting with http:// or https://",
                "platform_info": None,
            }

        platform_info = self._get_platform_info(url)

        return {
            "valid": True,
            "platform_info": platform_info,
            "warnings": (
                []
                if not platform_info["requires_login"]
                else [
                    f"This appears to be a {platform_info['provider']} URL, which may require login."
                ]
            ),
        }

    def _parse_html_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Parse HTML content to extract job description components.

        This is a heuristic-based parser that looks for common patterns
        in job posting HTML. May need tuning for specific job boards.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title = self._extract_title(soup, url)

        # Extract text content
        text_content = soup.get_text(separator="\n", strip=True)

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
            "h1",
            ".job-title",
            ".position-title",
            '[data-testid="job-title"]',
            "title",
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:  # Reasonable title length
                    return title

        # Fallback: extract from URL or page title
        page_title = soup.find("title")
        if page_title:
            title_text = page_title.get_text(strip=True)
            # Try to extract job title from page title
            # Common patterns: "Job Title | Company" or "Company - Job Title"
            if "|" in title_text:
                parts = title_text.split("|")
                title = parts[0].strip()
            elif "-" in title_text:
                parts = title_text.split("-")
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
            r"Responsibilities?:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"What you\'?ll do:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Role responsibilities:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Key responsibilities:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
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
            r"Requirements?:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"What you need:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Qualifications:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Skills required:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"You have:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
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
            r"About the role:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Job summary:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Position summary:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Overview:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
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
            lines = text.split("\n")
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
            r"About us:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"About the company:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Who we are:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
            r"Company description:?\s*\n?(.*?)(?:\n\n|\n[A-Z]|$)",
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
        if domain.startswith("www."):
            domain = domain[4:]

        # Common domain to company name mappings
        domain_hints = {
            "linkedin.com": "LinkedIn",
            "indeed.com": "Indeed",
            "glassdoor.com": "Glassdoor",
            "monster.com": "Monster",
            "dice.com": "Dice",
            "ziprecruiter.com": "ZipRecruiter",
        }

        if domain in domain_hints:
            return f"This position is posted on {domain_hints[domain]}, a leading job platform."

        # Try to extract company name from domain
        company_name = domain.split(".")[0].title()
        return f"This is a position at {company_name}."

    def _parse_list_items(self, text: str) -> List[str]:
        """Parse bullet points or numbered lists from text"""
        items = []

        # Split by common list markers
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # Remove bullet points and numbering
            cleaned_line = re.sub(r"^[-\*\•]\s*", "", line)  # Bullet points
            cleaned_line = re.sub(r"^\d+\.?\s*", "", cleaned_line)  # Numbered lists

            # Only keep substantial items
            if len(cleaned_line) > 10 and not cleaned_line.startswith(("http", "www.")):
                items.append(cleaned_line)

        return items

    def _is_redirected_to_login(
        self, response: httpx.Response, original_url: str
    ) -> bool:
        """
        Check if the response indicates we've been redirected to a login page.

        Args:
            response: The HTTP response
            original_url: The original URL we tried to fetch

        Returns:
            bool: True if redirected to login page
        """
        # Check if the URL changed (indicating a redirect)
        if response.url != original_url:
            final_url = str(response.url).lower()

            # Common login/auth URL patterns
            login_indicators = [
                "login",
                "auth",
                "signin",
                "sign-in",
                "log-in",
                "authenticate",
                "session_redirect",
                "uas/login",
            ]

            if any(indicator in final_url for indicator in login_indicators):
                return True

        # Check response content for login page indicators
        if response.text:
            content_lower = response.text.lower()
            login_content_indicators = [
                "sign in",
                "log in",
                "login required",
                "authentication required",
                "please sign in",
                "you must be logged in",
                "login to continue",
            ]

            if any(
                indicator in content_lower for indicator in login_content_indicators
            ):
                return True

        return False
