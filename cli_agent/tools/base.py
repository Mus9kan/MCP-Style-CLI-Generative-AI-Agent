"""Base tool class for MCP-style tool architecture."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json


class BaseTool(ABC):
    """
    Abstract base class for all tools in the MCP-style architecture.
    
    Each tool should define:
    - name: Unique identifier for the tool
    - description: Human-readable description of what the tool does
    - parameters: JSON Schema defining the tool's input parameters
    """

    name: str = "base_tool"
    description: str = "Base tool class"
    parameters: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            Dictionary containing tool execution result
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool definition to dictionary for LLM API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def validate_params(self, **kwargs) -> bool:
        """
        Validate input parameters against schema.

        Args:
            **kwargs: Parameters to validate

        Returns:
            True if valid, raises ValueError otherwise
        """
        required = self.parameters.get("required", [])
        properties = self.parameters.get("properties", {})

        # Check required parameters
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")

        # Check parameter types
        for param, value in kwargs.items():
            if param in properties:
                expected_type = properties[param].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Parameter '{param}' must be a string")
                elif expected_type == "integer" and not isinstance(value, int):
                    raise ValueError(f"Parameter '{param}' must be an integer")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Parameter '{param}' must be a boolean")

        return True

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
