"""Log analysis tools for CLI AI Agent."""

from pathlib import Path
from typing import Dict, Any, List
import re
from collections import Counter

from .base import BaseTool
from .registry import register_tool
from ..utils.exceptions import ToolError


@register_tool
class GetLogsTool(BaseTool):
    """Read and retrieve logs from a file."""

    name = "get_logs"
    description = "Retrieve log entries from a log file"
    parameters = {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to the log file",
            },
            "lines": {
                "type": "integer",
                "description": "Number of recent lines to retrieve (default: 50)",
            },
        },
        "required": ["file"],
    }

    def execute(self, file: str, lines: int = 50) -> Dict[str, Any]:
        """Execute the log retrieval operation."""
        try:
            log_path = Path(file)
            
            if not log_path.exists():
                raise ToolError(self.name, f"Log file not found: {file}")
            
            # Read last N lines
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            return {
                "success": True,
                "file": str(log_path.absolute()),
                "total_lines": len(all_lines),
                "retrieved_lines": len(recent_lines),
                "logs": "".join(recent_lines),
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class AnalyzeLogsTool(BaseTool):
    """Analyze log file for patterns and issues."""

    name = "analyze_logs"
    description = "Analyze a log file for errors, warnings, and patterns"
    parameters = {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to the log file",
            },
        },
        "required": ["file"],
    }

    def execute(self, file: str) -> Dict[str, Any]:
        """Execute the log analysis operation."""
        try:
            log_path = Path(file)
            
            if not log_path.exists():
                raise ToolError(self.name, f"Log file not found: {file}")
            
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
            
            # Count log levels
            level_patterns = {
                "ERROR": r"\b(ERROR|error|Error|FATAL|Fatal|fatal)\b",
                "WARNING": r"\b(WARNING|warning|Warning|WARN|warn|Warn)\b",
                "INFO": r"\b(INFO|info|Info)\b",
                "DEBUG": r"\b(DEBUG|debug|Debug)\b",
                "CRITICAL": r"\b(CRITICAL|critical|Critical|CRIT|crit|Crit)\b",
            }
            
            level_counts = {}
            for level, pattern in level_patterns.items():
                matches = re.findall(pattern, content)
                level_counts[level] = len(matches)
            
            # Extract error messages
            error_lines = []
            for line in lines:
                if re.search(level_patterns["ERROR"], line) or re.search(
                    level_patterns["CRITICAL"], line
                ):
                    error_lines.append(line.strip())
            
            # Time-based analysis (if timestamps present)
            timestamp_pattern = r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
            timestamps = re.findall(timestamp_pattern, content)
            
            analysis = {
                "success": True,
                "file": str(log_path.absolute()),
                "total_lines": len(lines),
                "level_counts": level_counts,
                "error_count": level_counts.get("ERROR", 0) + level_counts.get("CRITICAL", 0),
                "warning_count": level_counts.get("WARNING", 0),
                "has_timestamps": len(timestamps) > 0,
                "sample_errors": error_lines[:10],  # First 10 errors
            }
            
            return analysis
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class DetectCorsIssueTool(BaseTool):
    """Detect CORS-related issues in logs."""

    name = "detect_cors_issue"
    description = "Analyze logs to detect CORS (Cross-Origin Resource Sharing) errors"
    parameters = {
        "type": "object",
        "properties": {
            "logs": {
                "type": "string",
                "description": "Log content to analyze",
            },
            "file": {
                "type": "string",
                "description": "Path to log file (alternative to direct logs)",
            },
        },
        "required": [],
    }

    def execute(
        self, logs: str = None, file: str = None
    ) -> Dict[str, Any]:
        """Execute the CORS issue detection operation."""
        try:
            # Get log content
            if file:
                log_path = Path(file)
                if not log_path.exists():
                    raise ToolError(self.name, f"Log file not found: {file}")
                
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    logs = f.read()
            elif not logs:
                raise ToolError(self.name, "Either 'logs' or 'file' parameter required")
            
            # CORS error patterns
            cors_patterns = [
                r"CORS.*(?:policy|error|issue)",
                r"Access-Control-Allow-Origin",
                r"(?:cross-origin|CORS).*request",
                r"No\s*['\"]Access-Control-Allow-Origin['\"]\s*header",
                r"Origin\s+(?:not\s+)?allowed",
                r"preflight.*fail",
            ]
            
            detected_issues = []
            for pattern in cors_patterns:
                matches = re.findall(pattern, logs, re.IGNORECASE)
                if matches:
                    detected_issues.extend(matches)
            
            # Find related error lines
            cors_lines = []
            for line in logs.split("\n"):
                if any(
                    re.search(pattern, line, re.IGNORECASE)
                    for pattern in cors_patterns
                ):
                    cors_lines.append(line.strip())
            
            has_cors_issue = len(detected_issues) > 0
            
            return {
                "success": True,
                "cors_detected": has_cors_issue,
                "issue_count": len(detected_issues),
                "issues_found": list(set(detected_issues))[:10],
                "related_lines": cors_lines[:10],
                "recommendation": (
                    "Configure CORS headers on server: "
                    "Access-Control-Allow-Origin: *"
                    if has_cors_issue
                    else "No CORS issues detected"
                ),
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)
