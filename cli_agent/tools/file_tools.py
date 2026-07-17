"""File operation tools for CLI AI Agent."""

from pathlib import Path
from typing import Dict, Any, List
import os

from .base import BaseTool
from .registry import register_tool
from ..utils.exceptions import ToolError, ValidationError


@register_tool
class ReadFileTool(BaseTool):
    """Read contents of a file."""

    name = "read_file"
    description = "Read the contents of a file at the specified path"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read",
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to read (default: 100)",
            },
        },
        "required": ["path"],
    }

    def execute(self, path: str, max_lines: int = 100) -> Dict[str, Any]:
        """Execute the file read operation."""
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                raise ToolError(self.name, f"File not found: {path}")
            
            if not file_path.is_file():
                raise ToolError(self.name, f"Not a file: {path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        # Don't add the limit message to lines_read count
                        lines.append(f"... ({max_lines} lines limit reached)")
                        break
                    lines.append(line.rstrip())
                
                content = "\n".join(lines)
                # Count only actual lines read, not the limit message
                lines_read = min(i + 1, max_lines) if len(lines) > 0 else 0
            
            return {
                "success": True,
                "path": str(file_path.absolute()),
                "content": content,
                "lines_read": lines_read,
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class SearchFilesTool(BaseTool):
    """Search for files containing specific keyword."""

    name = "search_files"
    description = "Search for files containing a specific keyword or pattern"
    parameters = {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Keyword or pattern to search for",
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in (default: current directory)",
            },
            "file_pattern": {
                "type": "string",
                "description": "File pattern to match (e.g., '*.py')",
            },
        },
        "required": ["keyword"],
    }

    def execute(
        self,
        keyword: str,
        directory: str = ".",
        file_pattern: str = "*",
    ) -> Dict[str, Any]:
        """Execute the file search operation."""
        try:
            search_dir = Path(directory)
            
            if not search_dir.exists():
                raise ToolError(self.name, f"Directory not found: {directory}")
            
            results = []
            files_checked = 0
            
            for file_path in search_dir.rglob(file_pattern):
                if file_path.is_file():
                    files_checked += 1
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if keyword in content:
                                # Count occurrences
                                count = content.count(keyword)
                                results.append({
                                    "file": str(file_path),
                                    "occurrences": count,
                                })
                    except Exception:
                        continue
            
            return {
                "success": True,
                "keyword": keyword,
                "files_checked": files_checked,
                "matches_found": len(results),
                "results": results,
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class SummarizeFileTool(BaseTool):
    """Get summary information about a file."""

    name = "summarize_file"
    description = "Get summary information about a file (size, lines, type)"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file",
            },
        },
        "required": ["path"],
    }

    def execute(self, path: str) -> Dict[str, Any]:
        """Execute the file summary operation."""
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                raise ToolError(self.name, f"File not found: {path}")
            
            if not file_path.is_file():
                raise ToolError(self.name, f"Not a file: {path}")
            
            # Get file stats
            stats = file_path.stat()
            
            # Count lines
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                line_count = sum(1 for _ in f)
            
            # Get file extension
            extension = file_path.suffix.lower()
            file_type_map = {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".cpp": "C++",
                ".c": "C",
                ".h": "Header",
                ".html": "HTML",
                ".css": "CSS",
                ".json": "JSON",
                ".xml": "XML",
                ".md": "Markdown",
                ".txt": "Text",
            }
            file_type = file_type_map.get(extension, "Unknown")
            
            return {
                "success": True,
                "path": str(file_path.absolute()),
                "filename": file_path.name,
                "extension": extension,
                "type": file_type,
                "size_bytes": stats.st_size,
                "size_kb": round(stats.st_size / 1024, 2),
                "line_count": line_count,
                "created": stats.st_ctime,
                "modified": stats.st_mtime,
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)
