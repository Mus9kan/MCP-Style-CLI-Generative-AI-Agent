"""Tool registry for dynamic tool discovery and execution."""

from typing import Dict, List, Type, Optional
from .base import BaseTool


class ToolRegistry:
    """Central registry for all available tools."""

    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, BaseTool] = {}

    def __new__(cls) -> "ToolRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """
        Register a tool class.

        Args:
            tool_class: Tool class to register

        Returns:
            The registered class
        """
        tool_instance = tool_class()
        cls._tools[tool_instance.name] = tool_instance
        return tool_class

    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """Get all registered tools."""
        return list(cls._tools.values())

    @classmethod
    def get_tool_definitions(cls) -> List[Dict]:
        """Get all tool definitions for LLM API."""
        return [tool.to_dict() for tool in cls._tools.values()]

    @classmethod
    def list_tools(cls) -> List[str]:
        """List all registered tool names."""
        return list(cls._tools.keys())

    @classmethod
    def execute_tool(cls, name: str, **kwargs) -> Dict:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            **kwargs: Tool parameters

        Returns:
            Tool execution result
        """
        tool = cls.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        return tool.execute(**kwargs)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools (for testing)."""
        cls._tools.clear()


# Decorator for easy tool registration
def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """Decorator to register a tool."""
    ToolRegistry.register(tool_class)
    return tool_class
