"""Intent classification for CLI AI Agent."""

from typing import Dict, Any, Optional, List
import re


class IntentClassifier:
    """Classify user intent to determine which tool to use."""

    # Intent patterns mapping keywords to tool names
    INTENT_PATTERNS = {
        "read_file": [
            r"\b(read|open|show|display|view)\s+(file|code)",
            r"\bfile\s+path",
            r"\.py$",
            r"\.js$",
            r"\.txt$",
            r"\.json$",
        ],
        "search_files": [
            r"\b(search|find|locate)\b.*\bin\b",
            r"\bfind\s+keyword",
            r"\bwhere\s+is\s+\w+",
        ],
        "summarize_file": [
            r"\b(summarize|summary|info|information)\b",
            r"\bwhat\s+does\s+\w+\s+do",
        ],
        "fetch_api_data": [
            r"\b(fetch|get|retrieve)\s+data",
            r"\bapi\s+(call|request|endpoint)",
            r"http[s]?://",  # Generic URL match
        ],
        "check_health": [
            r"\b(health|status|ping)\b",
            r"\bcheck\s+(health|status)\b",
            r"\bis\s+\w+\s+(up|running|alive)",
            r"check\s+health\s+of",  # Strong indicator
        ],
        "test_endpoint": [
            r"\btest\s+(endpoint|api|route)",
            r"\b(endpoint|api)\s+test",
        ],
        "get_logs": [
            r"\b(get|retrieve|show|read)\s+logs?",
            r"\blog\s+file",
        ],
        "analyze_logs": [
            r"\b(analyze|analysis|inspect)\s+logs?",
            r"\blog\s+analysis",
        ],
        "detect_cors_issue": [
            r"\b(cors|CORS|cross.origin)\b",
            r"\baccess.control.allow.origin",
        ],
        "execute_command": [
            r"\b(run|exec|execute|shell)\b",
            r"^\$\s*\w+",
        ],
        "validate_env": [
            r"\b(validate|check)\s+env",
            r"\benvironment\s+variables?",
        ],
        "check_env_var": [
            r"\bcheck\s+variable",
            r"\benv\s+\w+",
        ],
        "system_info": [
            r"\bsystem\s+info",
            r"\bwhat\s+system",
        ],
    }

    @classmethod
    def classify(cls, user_input: str) -> Dict[str, Any]:
        """
        Classify user input to determine intent.

        Args:
            user_input: User's command/query

        Returns:
            Dictionary with classification results
        """
        scores = {}
        
        # Check each intent pattern
        for tool_name, patterns in cls.INTENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                scores[tool_name] = score
        
        # Get best match
        if scores:
            best_tool = max(scores, key=scores.get)
            confidence = scores[best_tool] / max(len(cls.INTENT_PATTERNS[best_tool]), 1)
            
            return {
                "intent": "tool_call",
                "tool": best_tool,
                "confidence": min(confidence, 1.0),
                "scores": scores,
            }
        
        # Default to general conversation
        return {
            "intent": "conversation",
            "tool": None,
            "confidence": 0.0,
        }

    @classmethod
    def extract_parameters(cls, user_input: str, tool_name: str) -> Dict[str, Any]:
        """
        Extract parameters from user input based on tool type.

        Args:
            user_input: User's command/query
            tool_name: Identified tool name

        Returns:
            Dictionary of extracted parameters
        """
        params = {}
        
        if tool_name == "read_file":
            # Extract file path
            match = re.search(r"(\S+\.(py|js|txt|json|md|csv))", user_input)
            if match:
                params["path"] = match.group(1)
        
        elif tool_name == "search_files":
            # Extract keyword
            match = re.search(r'(?:find|search)\s+["\']?([^"\']+)["\']?', user_input)
            if match:
                params["keyword"] = match.group(1).strip()
        
        elif tool_name in ["fetch_api_data", "check_health"]:
            # Extract URL
            match = re.search(r"(http[s]?://\S+)", user_input)
            if match:
                params["url"] = match.group(1)
        
        elif tool_name == "test_endpoint":
            # Extract endpoint and base_url
            match = re.search(r"(http[s]?://[^/\s]+)(/\S+)?", user_input)
            if match:
                params["base_url"] = match.group(1)
                params["endpoint"] = match.group(2) or "/"
        
        elif tool_name in ["get_logs", "analyze_logs"]:
            # Extract log file path
            match = re.search(r"(\S+\.log)", user_input)
            if match:
                params["file"] = match.group(1)
        
        elif tool_name == "execute_command":
            # Extract command (everything after command verb)
            match = re.search(r"(?:run|exec|execute)\s+(.+)$", user_input)
            if match:
                params["command"] = match.group(1).strip()
        
        return params
