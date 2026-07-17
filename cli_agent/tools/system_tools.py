"""System operation tools for CLI AI Agent."""

import os
import subprocess
import sys
from typing import Dict, Any, List
from pathlib import Path

from .base import BaseTool
from .registry import register_tool
from ..utils.exceptions import ToolError


@register_tool
class ExecuteCommandTool(BaseTool):
    """Execute system commands safely."""

    name = "execute_command"
    description = "Execute a system command and return output (use with caution)"
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command to execute",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)",
            },
        },
        "required": ["command"],
    }

    def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute the system command."""
        try:
            # Security check - prevent dangerous commands
            dangerous_commands = ["rm -rf", "del /f", "format", "mkfs"]
            if any(dc in command.lower() for dc in dangerous_commands):
                raise ToolError(
                    self.name,
                    "Potentially dangerous command blocked for safety",
                )
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            
            return {
                "success": result.returncode == 0,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timeout": False,
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": command,
                "error": f"Command timed out after {timeout}s",
                "timeout": True,
            }
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class ValidateEnvTool(BaseTool):
    """Validate environment variables."""

    name = "validate_env"
    description = "Validate that required environment variables are set"
    parameters = {
        "type": "object",
        "properties": {
            "variables": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of environment variable names to check",
            },
        },
        "required": [],
    }

    def execute(self, variables: List[str] = None) -> Dict[str, Any]:
        """Execute environment validation."""
        try:
            # Default important variables to check
            if variables is None:
                # Use platform-specific variables
                home_var = "HOME" if os.name != "nt" else "USERPROFILE"
                variables = [
                    "OPENAI_API_KEY",
                    "PATH",
                    home_var,
                ]
            
            results = {}
            missing = []
            set_vars = []
            
            for var in variables:
                value = os.getenv(var)
                if value:
                    set_vars.append(var)
                    results[var] = {
                        "status": "set",
                        "length": len(value),
                        "first_chars": value[:20] + ("..." if len(value) > 20 else ""),
                    }
                else:
                    missing.append(var)
                    results[var] = {"status": "missing"}
            
            return {
                "success": len(missing) == 0,
                "checked": len(variables),
                "set": set_vars,
                "missing": missing,
                "details": results,
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class CheckEnvVarTool(BaseTool):
    """Check a specific environment variable."""

    name = "check_env_var"
    description = "Check the value of a specific environment variable"
    parameters = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the environment variable",
            },
        },
        "required": ["name"],
    }

    def execute(self, name: str) -> Dict[str, Any]:
        """Execute environment variable check."""
        try:
            value = os.getenv(name)
            
            if value is None:
                return {
                    "success": False,
                    "name": name,
                    "exists": False,
                    "value": None,
                }
            
            # Mask sensitive values
            is_sensitive = any(
                keyword in name.upper()
                for keyword in ["KEY", "SECRET", "PASSWORD", "TOKEN", "API"]
            )
            
            display_value = (
                "***REDACTED***" if is_sensitive and len(value) > 8 else value
            )
            
            return {
                "success": True,
                "name": name,
                "exists": True,
                "value": display_value,
                "length": len(value),
                "is_sensitive": is_sensitive,
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class SystemInfoTool(BaseTool):
    """Get system information."""

    name = "system_info"
    description = "Get basic system information (OS, Python version, etc.)"
    parameters = {
        "type": "object",
        "properties": {},
    }

    def execute(self) -> Dict[str, Any]:
        """Execute system info gathering."""
        try:
            import platform
            
            return {
                "success": True,
                "os": platform.system(),
                "os_version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cwd": str(Path.cwd()),
                "home": str(Path.home()),
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)
