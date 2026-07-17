"""Tests for tool implementations."""

import pytest
from pathlib import Path
import tempfile
import os

from cli_agent.tools.file_tools import ReadFileTool, SearchFilesTool, SummarizeFileTool
from cli_agent.tools.api_tools import CheckHealthTool
from cli_agent.tools.log_tools import GetLogsTool, AnalyzeLogsTool
from cli_agent.tools.system_tools import ValidateEnvTool, SystemInfoTool
from cli_agent.tools.registry import ToolRegistry


class TestReadFileTool:
    """Test file reading functionality."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, World!\nLine 2\nLine 3")
            temp_path = f.name
        
        try:
            tool = ReadFileTool()
            result = tool.execute(path=temp_path)
            
            assert result["success"] is True
            assert "Hello, World!" in result["content"]
            assert result["lines_read"] == 3
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_file(self):
        """Test reading a nonexistent file."""
        tool = ReadFileTool()
        
        with pytest.raises(Exception) as exc_info:
            tool.execute(path="nonexistent.txt")
        
        assert "not found" in str(exc_info.value)

    def test_read_with_line_limit(self):
        """Test reading file with line limit."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for i in range(100):
                f.write(f"Line {i+1}\n")
            temp_path = f.name
        
        try:
            tool = ReadFileTool()
            result = tool.execute(path=temp_path, max_lines=50)
            
            assert result["lines_read"] <= 50
        finally:
            os.unlink(temp_path)


class TestSearchFilesTool:
    """Test file search functionality."""

    def test_search_keyword(self):
        """Test searching for a keyword."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            file1 = Path(tmpdir) / "test1.txt"
            file2 = Path(tmpdir) / "test2.txt"
            
            file1.write_text("Hello World")
            file2.write_text("Goodbye World")
            
            tool = SearchFilesTool()
            result = tool.execute(keyword="World", directory=tmpdir)
            
            assert result["success"] is True
            assert result["matches_found"] == 2


class TestSummarizeFileTool:
    """Test file summary functionality."""

    def test_summarize_python_file(self):
        """Test summarizing a Python file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# Comment\nprint('hello')\n")
            temp_path = f.name
        
        try:
            tool = SummarizeFileTool()
            result = tool.execute(path=temp_path)
            
            assert result["success"] is True
            assert result["extension"] == ".py"
            assert result["type"] == "Python"
            assert result["line_count"] == 2
        finally:
            os.unlink(temp_path)


class TestLogTools:
    """Test log analysis tools."""

    def test_analyze_logs(self):
        """Test log analysis."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write("INFO: Starting app\n")
            f.write("ERROR: Something failed\n")
            f.write("WARNING: Low memory\n")
            temp_path = f.name
        
        try:
            tool = AnalyzeLogsTool()
            result = tool.execute(file=temp_path)
            
            assert result["success"] is True
            assert result["error_count"] >= 1
            assert result["warning_count"] >= 1
        finally:
            os.unlink(temp_path)


class TestSystemTools:
    """Test system operation tools."""

    def test_validate_env(self):
        """Test environment validation."""
        tool = ValidateEnvTool()
        # Use platform-appropriate variables
        import os
        home_var = "HOME" if os.name != "nt" else "USERPROFILE"
        result = tool.execute(variables=["PATH", home_var])
        
        assert result["success"] is True
        assert "checked" in result
        assert "set" in result

    def test_system_info(self):
        """Test system info retrieval."""
        tool = SystemInfoTool()
        result = tool.execute()
        
        assert result["success"] is True
        assert "os" in result
        assert "python_version" in result


class TestToolRegistry:
    """Test tool registry functionality."""

    def test_list_tools(self):
        """Test listing all registered tools."""
        tools = ToolRegistry.list_tools()
        
        assert len(tools) > 0
        assert "read_file" in tools
        assert "check_health" in tools

    def test_get_tool(self):
        """Test getting a specific tool."""
        tool = ToolRegistry.get_tool("read_file")
        
        assert tool is not None
        assert tool.name == "read_file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
