import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ErrorCategory(str, Enum):
    """Categories of errors for better handling and user communication"""

    NETWORK = "network"
    VALIDATION = "validation"
    LLM = "llm"
    PARSING = "parsing"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class JobAgentError(Exception):
    """Base exception for Job Agent errors"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None,
    ):
        super().__init__(message)
        self.category = category
        self.details = details or {}
        self.user_message = user_message or message

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            "error": self.user_message,
            "category": self.category.value,
            "details": self.details,
        }


class NetworkError(JobAgentError):
    """Network-related errors"""

    def __init__(
        self, message: str, url: Optional[str] = None, status_code: Optional[int] = None
    ):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            details={"url": url, "status_code": status_code},
            user_message=self._get_user_message(message, url),
        )

    def _get_user_message(self, message: str, url: Optional[str]) -> str:
        if "404" in message or "Not Found" in message:
            return "The job posting URL could not be found. Please check the URL and try again."
        elif "403" in message or "Forbidden" in message:
            return "Access to this job posting is restricted. Try using a different job board or copy-paste the description."
        elif "500" in message or "502" in message or "503" in message:
            return "The job board is temporarily unavailable. Please try again later."
        elif "timeout" in message.lower():
            return "The request timed out. Please check your internet connection and try again."
        else:
            return "Unable to access the job posting. Please try a different URL or copy-paste the job description."


class ValidationError(JobAgentError):
    """Input validation errors"""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Optional[Any] = None
    ):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            details={"field": field, "value": str(value)[:100] if value else None},
            user_message=self._get_user_message(message, field),
        )

    def _get_user_message(self, message: str, field: Optional[str]) -> str:
        if field == "job_description_url":
            return "Please provide a valid job posting URL (must start with http:// or https://)."
        elif "profile" in str(field or "").lower():
            return "Please provide a complete profile with career background and education information."
        else:
            return "Please check your input and try again."


class LLMError(JobAgentError):
    """LLM-related errors"""

    def __init__(
        self, message: str, provider: Optional[str] = None, model: Optional[str] = None
    ):
        super().__init__(
            message,
            category=ErrorCategory.LLM,
            details={"provider": provider, "model": model},
            user_message=self._get_user_message(message),
        )

    def _get_user_message(self, message: str) -> str:
        if "api key" in message.lower() or "authentication" in message.lower():
            return "AI service is not configured properly. Please contact support."
        elif "rate limit" in message.lower() or "quota" in message.lower():
            return "AI service is temporarily busy. Please try again in a few minutes."
        elif "timeout" in message.lower():
            return "AI response timed out. Please try again."
        else:
            return "AI service temporarily unavailable. Please try again."


class AuthenticationError(JobAgentError):
    """Authentication-related errors"""

    def __init__(self, message: str, provider: Optional[str] = None):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            details={"provider": provider},
            user_message="This job posting requires login to view. Please try a different job board or copy-paste the description directly.",
        )


class RetryConfig:
    """Configuration for retry behavior"""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        retryable_errors: Optional[List[ErrorCategory]] = None,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retryable_errors = retryable_errors or [
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
        ]


async def retry_with_backoff(
    func: Callable[..., Any], config: RetryConfig = RetryConfig(), *args, **kwargs
) -> Any:
    """
    Retry a function with exponential backoff for retryable errors.

    Args:
        func: The async function to retry
        config: Retry configuration
        *args, **kwargs: Arguments to pass to the function

    Returns:
        The result of the function call

    Raises:
        The last exception if all retries are exhausted
    """
    last_exception = None

    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except JobAgentError as e:
            last_exception = e

            # Don't retry if error is not retryable
            if e.category not in config.retryable_errors:
                logger.warning(f"Non-retryable error: {e.category} - {str(e)}")
                raise e

            # Don't retry on the last attempt
            if attempt == config.max_attempts - 1:
                logger.error(f"All {config.max_attempts} attempts failed: {str(e)}")
                raise e

            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.backoff_factor**attempt), config.max_delay
            )

            logger.warning(
                f"Attempt {attempt + 1} failed ({e.category}): {str(e)}. Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)

        except Exception as e:
            last_exception = e

            # Don't retry unknown exceptions
            logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt == config.max_attempts - 1:
                raise JobAgentError(
                    f"Unexpected error: {str(e)}", ErrorCategory.UNKNOWN
                ) from e

            delay = min(
                config.base_delay * (config.backoff_factor**attempt), config.max_delay
            )
            await asyncio.sleep(delay)

    # This should never be reached, but just in case
    if last_exception:
        raise last_exception


def handle_job_loading_errors(func):
    """
    Decorator to handle common job loading errors and convert them to JobAgentError
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)

            # Network errors
            if "404" in error_msg or "Not Found" in error_msg:
                raise NetworkError(error_msg, status_code=404) from e
            elif "403" in error_msg or "Forbidden" in error_msg:
                raise AuthenticationError(error_msg) from e
            elif "timeout" in error_msg.lower():
                raise NetworkError(error_msg) from e
            elif any(code in error_msg for code in ["500", "502", "503", "504"]):
                raise NetworkError(error_msg) from e

            # Re-raise as JobAgentError if not already one
            if isinstance(e, JobAgentError):
                raise
            else:
                raise JobAgentError(
                    f"Job loading failed: {error_msg}", ErrorCategory.UNKNOWN
                ) from e

    return wrapper


def handle_llm_errors(func):
    """
    Decorator to handle common LLM errors and convert them to JobAgentError
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()

            # API key/auth errors
            if (
                "api key" in error_msg
                or "authentication" in error_msg
                or "unauthorized" in error_msg
            ):
                raise LLMError(
                    "API authentication failed",
                    user_message="AI service configuration error",
                ) from e

            # Rate limiting
            elif "rate limit" in error_msg or "quota" in error_msg:
                raise LLMError(
                    "Rate limit exceeded",
                    user_message="AI service is busy, please try again later",
                ) from e

            # Timeout
            elif "timeout" in error_msg:
                raise LLMError(
                    "Request timed out",
                    user_message="AI response timed out, please try again",
                ) from e

            # Re-raise as JobAgentError if not already one
            if isinstance(e, JobAgentError):
                raise
            else:
                raise LLMError(
                    f"AI service error: {str(e)}",
                    user_message="AI service temporarily unavailable",
                ) from e

    return wrapper


def handle_validation_errors(func):
    """
    Decorator to handle validation errors and convert them to ValidationError
    """

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)

            # Check for common validation patterns
            if "URL" in error_msg or "url" in error_msg:
                raise ValidationError(error_msg, field="job_description_url") from e
            elif "profile" in error_msg.lower():
                raise ValidationError(error_msg, field="user_profile") from e

            # Re-raise as ValidationError if not already one
            if isinstance(e, JobAgentError):
                raise
            else:
                raise ValidationError(f"Validation failed: {error_msg}") from e

    return wrapper
