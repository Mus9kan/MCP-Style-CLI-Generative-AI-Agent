"""Custom exceptions for CLI AI Agent."""


class AgentError(Exception):
    """Base exception for agent-related errors."""

    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details or ""
        super().__init__(self.message)


class ConfigError(AgentError):
    """Configuration-related errors."""

    pass


class ToolError(AgentError):
    """Tool execution errors."""

    def __init__(self, tool_name: str, message: str, original_error: Exception = None):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(f"Tool '{tool_name}' error: {message}")


class APIError(AgentError):
    """OpenAI API-related errors."""

    pass


class ValidationError(AgentError):
    """Input validation errors."""

    pass


class RetryError(AgentError):
    """Retry mechanism errors."""

    def __init__(self, tool_name: str, max_retries: int, last_error: Exception = None):
        self.tool_name = tool_name
        self.max_retries = max_retries
        self.last_error = last_error
        super().__init__(
            f"Tool '{tool_name}' failed after {max_retries} retries",
            f"Last error: {str(last_error) if last_error else 'Unknown'}"
        )
