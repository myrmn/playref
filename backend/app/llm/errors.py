"""Custom exception classes for LLM and Model API calls."""


class LLMError(Exception):
    """Base exception for LLM operations."""

    pass


class APIConnectionError(LLMError):
    """Network connection failure."""

    pass


class APITimeoutError(LLMError):
    """Request timed out."""

    pass


class RateLimitError(LLMError):
    """API rate limit exceeded (HTTP 429)."""

    pass


class AuthenticationError(LLMError):
    """Invalid API key or unauthorized (HTTP 401/403)."""

    pass


class ModelResponseError(LLMError):
    """Malformed or unexpected model response."""

    pass
