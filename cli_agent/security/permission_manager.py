"""Permission manager for tool access control and security."""

from typing import Dict, List, Optional, Set
from enum import Enum
import re

from ..utils.logger import get_logger
from ..utils.config import get_config

logger = get_logger(__name__)


class SecurityLevel(Enum):
    """Security levels for tools."""
    LOW = "low"  # Safe operations (read-only)
    MEDIUM = "medium"  # Operations with side effects
    HIGH = "high"  # Potentially dangerous operations
    CRITICAL = "critical"  # Destructive operations


class PermissionManager:
    """Manages tool permissions and access control."""

    def __init__(self):
        """Initialize permission manager."""
        self.config = get_config()
        
        # Default security levels for tools
        self.tool_security_levels: Dict[str, SecurityLevel] = {
            # Low risk - read only
            "read_file": SecurityLevel.LOW,
            "search_files": SecurityLevel.LOW,
            "check_health": SecurityLevel.LOW,
            "fetch_api_data": SecurityLevel.LOW,
            "test_endpoint": SecurityLevel.LOW,
            "validate_env": SecurityLevel.LOW,
            "analyze_logs": SecurityLevel.LOW,
            "find_text": SecurityLevel.LOW,
            
            # Medium risk - operations with side effects
            "get_weather": SecurityLevel.MEDIUM,
            "get_time": SecurityLevel.MEDIUM,
            
            # High risk - system operations
            "execute_command": SecurityLevel.HIGH,
            "write_file": SecurityLevel.HIGH,
            "delete_file": SecurityLevel.HIGH,
        }
        
        # Default permissions
        self.allowed_tools: Optional[Set[str]] = None  # None means all allowed
        self.blocked_tools: Set[str] = self._load_blocked_tools()
        
        # Dangerous patterns to block
        self.dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Don't delete root
            r"sudo\s+rm",  # Don't sudo delete
            r"mkfs\.",  # Don't format disks
            r">>\s*/etc/passwd",  # Don't modify passwd
            r"chmod\s+777\s+/",  # Don't chmod root
        ]
        
        logger.info("Permission manager initialized")

    def _load_blocked_tools(self) -> Set[str]:
        """Load blocked tools from configuration."""
        # Could be loaded from config file in the future
        return set()

    def set_allowed_tools(self, tools: Set[str]):
        """
        Set explicitly allowed tools (whitelist mode).
        
        Args:
            tools: Set of tool names that are allowed
        """
        self.allowed_tools = tools
        logger.info(f"Allowed tools set: {tools}")

    def block_tool(self, tool_name: str):
        """
        Block a specific tool.
        
        Args:
            tool_name: Tool to block
        """
        self.blocked_tools.add(tool_name)
        logger.warning(f"Tool blocked: {tool_name}")

    def unblock_tool(self, tool_name: str):
        """
        Unblock a specific tool.
        
        Args:
            tool_name: Tool to unblock
        """
        self.blocked_tools.discard(tool_name)
        logger.info(f"Tool unblocked: {tool_name}")

    def check_permission(self, tool_name: str, params: Optional[Dict] = None) -> Dict:
        """
        Check if a tool execution is allowed.
        
        Args:
            tool_name: Tool name to check
            params: Tool parameters
            
        Returns:
            Dictionary with permission decision and reason
        """
        # Check if tool is explicitly blocked
        if tool_name in self.blocked_tools:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' is blocked",
                "security_level": self.tool_security_levels.get(tool_name, SecurityLevel.MEDIUM),
            }
        
        # Check whitelist
        if self.allowed_tools is not None and tool_name not in self.allowed_tools:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' is not in the allowed list",
                "security_level": self.tool_security_levels.get(tool_name, SecurityLevel.MEDIUM),
            }
        
        # Check parameter safety
        if params:
            safety_check = self._check_parameter_safety(tool_name, params)
            if not safety_check["safe"]:
                return safety_check
        
        # Get security level
        security_level = self.tool_security_levels.get(tool_name, SecurityLevel.MEDIUM)
        
        return {
            "allowed": True,
            "reason": "Permission granted",
            "security_level": security_level,
        }

    def _check_parameter_safety(self, tool_name: str, params: Dict) -> Dict:
        """
        Check if tool parameters are safe.
        
        Args:
            tool_name: Tool name
            params: Tool parameters
            
        Returns:
            Dictionary with safety assessment
        """
        security_level = self.tool_security_levels.get(tool_name, SecurityLevel.MEDIUM)
        
        # Check for dangerous patterns in string parameters
        for key, value in params.items():
            if isinstance(value, str):
                for pattern in self.dangerous_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        return {
                            "allowed": False,
                            "safe": False,
                            "reason": f"Dangerous pattern detected in parameter '{key}'",
                            "security_level": security_level,
                        }
        
        # File path safety checks
        if tool_name in ["write_file", "delete_file", "read_file"]:
            file_path = params.get("path", "")
            
            # Prevent directory traversal
            if ".." in file_path:
                return {
                    "allowed": False,
                    "safe": False,
                    "reason": "Directory traversal not allowed",
                    "security_level": security_level,
                }
            
            # Prevent access to sensitive system files
            sensitive_paths = ["/etc/shadow", "/etc/passwd", "/etc/sudoers"]
            if file_path in sensitive_paths:
                return {
                    "allowed": False,
                    "safe": False,
                    "reason": f"Access to sensitive file '{file_path}' is blocked",
                    "security_level": security_level,
                }
        
        return {
            "allowed": True,
            "safe": True,
            "reason": "Parameters are safe",
            "security_level": security_level,
        }

    def requires_confirmation(self, tool_name: str) -> bool:
        """
        Check if a tool requires user confirmation before execution.
        
        Args:
            tool_name: Tool name
            
        Returns:
            True if confirmation required
        """
        security_level = self.tool_security_levels.get(tool_name, SecurityLevel.MEDIUM)
        return security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]

    def get_security_report(self) -> Dict:
        """
        Get a security configuration report.
        
        Returns:
            Dictionary with security configuration
        """
        return {
            "total_tools": len(self.tool_security_levels),
            "blocked_tools": list(self.blocked_tools),
            "allowed_tools": list(self.allowed_tools) if self.allowed_tools else "all",
            "security_levels": {
                level.value: sum(1 for l in self.tool_security_levels.values() if l == level)
                for level in SecurityLevel
            },
        }

    def add_custom_tool_security(self, tool_name: str, level: SecurityLevel):
        """
        Add security level for a custom tool.
        
        Args:
            tool_name: Tool name
            level: Security level
        """
        self.tool_security_levels[tool_name] = level
        logger.info(f"Security level set for {tool_name}: {level.value}")
