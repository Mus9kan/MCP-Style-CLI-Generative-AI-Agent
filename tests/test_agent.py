"""Tests for agent functionality."""

import pytest
from unittest.mock import Mock, patch

from cli_agent.agent.core import Agent
from cli_agent.agent.intent import IntentClassifier


class TestIntentClassifier:
    """Test intent classification."""

    def test_classify_read_file(self):
        """Test classification of read file intent."""
        result = IntentClassifier.classify("read the file app.py")
        
        assert result["intent"] == "tool_call"
        assert result["tool"] == "read_file"

    def test_classify_health_check(self):
        """Test classification of health check intent."""
        result = IntentClassifier.classify("check health of http://localhost:5000")
        
        assert result["intent"] == "tool_call"
        assert result["tool"] == "check_health"

    def test_classify_cors_issue(self):
        """Test classification of CORS issue detection."""
        result = IntentClassifier.classify("detect CORS issues in logs")
        
        assert result["intent"] == "tool_call"
        assert result["tool"] == "detect_cors_issue"

    def test_extract_file_parameter(self):
        """Test parameter extraction for file reading."""
        params = IntentClassifier.extract_parameters(
            "read file app.py",
            "read_file"
        )
        
        assert "path" in params
        assert params["path"] == "app.py"

    def test_extract_url_parameter(self):
        """Test parameter extraction for API calls."""
        params = IntentClassifier.extract_parameters(
            "fetch data from http://example.com/api",
            "fetch_api_data"
        )
        
        assert "url" in params
        assert params["url"] == "http://example.com/api"


class TestAgent:
    """Test agent core functionality."""

    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = Agent()
        
        assert agent is not None
        assert hasattr(agent, 'config')

    def test_get_available_tools(self):
        """Test getting list of available tools."""
        agent = Agent()
        tools = agent.get_available_tools()
        
        assert len(tools) > 0
        assert isinstance(tools, list)

    def test_process_without_llm(self):
        """Test processing without LLM (rule-based)."""
        agent = Agent()
        result = agent.process_request(
            "read file test.txt",
            use_llm=False
        )
        
        assert "success" in result
        # Will fail because file doesn't exist, but should have proper structure
        assert isinstance(result, dict)

    def test_clear_history(self):
        """Test clearing conversation history."""
        agent = Agent()
        agent.clear_history()
        
        assert len(agent.conversation_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
