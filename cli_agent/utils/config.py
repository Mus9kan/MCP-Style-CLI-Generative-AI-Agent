"""Configuration management with .env support."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .exceptions import ConfigError


class Config:
    """Application configuration manager."""

    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        """Singleton pattern to ensure single config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize configuration."""
        if self._initialized:
            return

        self._load_env()
        self.api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.timeout: int = int(os.getenv("DEFAULT_TIMEOUT", "30"))
        self._initialized = True

    def _load_env(self) -> None:
        """Load environment variables from .env file."""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            # Try current directory as fallback
            env_path = Path.cwd() / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)

    def validate(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise ConfigError(
                "OpenAI API key not found",
                "Please set OPENAI_API_KEY in .env file or environment variable. "
                "Run 'agent setup' to configure.",
            )

    def is_configured(self) -> bool:
        """Check if configuration is valid."""
        return bool(self.api_key)

    def setup_api_key(self, api_key: str) -> None:
        """Set up API key and save to .env file."""
        self.api_key = api_key
        env_path = Path(__file__).parent.parent.parent / ".env"
        
        # Read existing content or create new
        content = ""
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                content = f.read()
        
        # Update or add API key
        lines = content.split("\n")
        found = False
        for i, line in enumerate(lines):
            if line.startswith("OPENAI_API_KEY="):
                lines[i] = f"OPENAI_API_KEY={api_key}"
                found = True
                break
        
        if not found:
            lines.append(f"OPENAI_API_KEY={api_key}")
        
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def get_config() -> Config:
    """Get application configuration."""
    return Config()
