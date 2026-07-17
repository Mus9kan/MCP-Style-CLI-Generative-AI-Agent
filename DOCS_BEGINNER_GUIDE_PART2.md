# Part 2: Agent Core - The AI Brain

This documentation explains how the AI agent works - the "brain" that understands your commands and decides what to do.

## Table of Contents

1. [Intent Classifier (intent.py)](#intent-classifier)
2. [Agent Core (core.py)](#agent-core)
3. [How Everything Connects](#how-everything-connects)

---

## Intent Classifier (cli_agent/agent/intent.py)

**Purpose**: Figures out what you want when you type a command. It's like a receptionist who directs your call to the right department.

### Imports (Lines 1-6)

```python
"""Intent classification for CLI AI Agent."""
# ^ Docstring explaining file purpose

from typing import Dict, Any, Optional, List
# ^ Type hints for better code understanding
# Dict = dictionary, Any = any type, Optional = can be None, List = list

import re
# ^ Regular expressions library for pattern matching (searching text)
```

### Class Definition (Lines 7-70)

```python
class IntentClassifier:
    """Classify user intent to determine which tool to use."""
    
    # INTENT_PATTERNS is a DICTIONARY (key-value pairs)
    # Each key is a tool name, each value is a LIST of regex patterns
    INTENT_PATTERNS = {
        "read_file": [
            r"\b(read|open|show|display|view)\s+(file|code)",
            # ^ Matches: "read file", "open code", "show file", etc.
            # \b = word boundary (start/end of word)
            # | means OR
            # \s+ = one or more spaces
            r"\bfile\s+path",      # Matches: "file path"
            r"\.py$",              # Matches: anything ending with .py
            r"\.js$",              # Matches: anything ending with .js
            r"\.txt$",             # Matches: anything ending with .txt
            r"\.json$",            # Matches: anything ending with .json
        ],
        
        "search_files": [
            r"\b(search|find|locate)\b.*\bin\b",
            # ^ Matches: "search for X in", "find X in", "locate X in"
            # .* = any characters (wildcard)
            r"\bfind\s+keyword",   # Matches: "find keyword"
            r"\bwhere\s+is\s+\w+", # Matches: "where is something"
            # \w+ = one or more word characters (letters, numbers, underscore)
        ],
        
        "summarize_file": [
            r"\b(summarize|summary|info|information)\b",
            # ^ Matches: "summarize", "summary", "info", "information"
            r"\bwhat\s+does\s+\w+\s+do",
            # ^ Matches: "what does filename do"
        ],
        
        "fetch_api_data": [
            r"\b(fetch|get|retrieve)\s+data",
            # ^ Matches: "fetch data", "get data", "retrieve data"
            r"\bapi\s+(call|request|endpoint)",
            # ^ Matches: "api call", "api request", "api endpoint"
            r"http[s]?://",
            # ^ Matches: http:// or https:// (URLs)
            # [s]? means 's' is optional
        ],
        
        "check_health": [
            r"\b(health|status|ping|check)\b",
            # ^ Matches: "health", "status", "ping", "check"
            r"\bis\s+\w+\s+(up|running|alive)",
            # ^ Matches: "is server up", "is api running", "is service alive"
        ],
        
        "test_endpoint": [
            r"\btest\s+(endpoint|api|route)",
            # ^ Matches: "test endpoint", "test api", "test route"
            r"\b(endpoint|api)\s+test",
            # ^ Matches: "endpoint test", "api test"
        ],
        
        "get_logs": [
            r"\b(get|retrieve|show|read)\s+logs?",
            # ^ Matches: "get log", "get logs", "retrieve logs", etc.
            # ? means previous character ('s') is optional
            r"\blog\s+file",       # Matches: "log file"
        ],
        
        "analyze_logs": [
            r"\b(analyze|analysis|inspect)\s+logs?",
            # ^ Matches: "analyze logs", "analysis log", "inspect logs"
            r"\blog\s+analysis",   # Matches: "log analysis"
        ],
        
        "detect_cors_issue": [
            r"\b(cors|CORS|cross.origin)\b",
            # ^ Matches: "cors", "CORS", "cross-origin"
            # . matches any character (including dot)
            r"\baccess.control.allow.origin",
            # ^ Matches CORS header name
        ],
        
        "execute_command": [
            r"\b(run|exec|execute|shell)\b",
            # ^ Matches: "run", "exec", "execute", "shell"
            r"^\$\s*\w+",
            # ^ Matches: $ followed by optional spaces and word
            # ^ = start of string
        ],
        
        "validate_env": [
            r"\b(validate|check)\s+env",
            # ^ Matches: "validate env", "check env"
            r"\benvironment\s+variables?",
            # ^ Matches: "environment variable" or "environment variables"
        ],
        
        "check_env_var": [
            r"\bcheck\s+variable",  # Matches: "check variable"
            r"\benv\s+\w+",         # Matches: "env SOMETHING"
        ],
        
        "system_info": [
            r"\bsystem\s+info",     # Matches: "system info"
            r"\bwhat\s+system",     # Matches: "what system"
        ],
    }
```

### classify Method (Lines 72-112)

```python
@classmethod
# ^ Decorator meaning this method belongs to the CLASS itself, not instances
def classify(cls, user_input: str) -> Dict[str, Any]:
    """
    Classify user input to determine intent.

    Args:
        user_input: User's command/query

    Returns:
        Dictionary with classification results
    """
    scores = {}
    # ^ Empty dictionary to store scores for each tool
    
    # Check each intent pattern
    for tool_name, patterns in cls.INTENT_PATTERNS.items():
        # ^ Loops through dictionary: gets tool_name and list of patterns
        score = 0
        # ^ Score starts at 0 for this tool
        
        for pattern in patterns:
            # ^ Checks each regex pattern for this tool
            if re.search(pattern, user_input, re.IGNORECASE):
                # ^ Searches for pattern in user_input
                # re.IGNORECASE makes it case-insensitive
                score += 1
                # ^ Found a match! Add 1 to score
            
            if score > 0:
                # ^ If any patterns matched
                scores[tool_name] = score
                # ^ Store the score for this tool
    
    # Get best match
    if scores:
        # ^ If any tools scored (dictionary not empty)
        best_tool = max(scores, key=scores.get)
        # ^ Finds tool with highest score
        # max() with key=scores.get means "use the score values to compare"
        
        confidence = scores[best_tool] / max(len(cls.INTENT_PATTERNS[best_tool]), 1)
        # ^ Calculates confidence as percentage
        # len() counts how many patterns exist for best_tool
        # max(..., 1) prevents division by zero
        
        return {
            "intent": "tool_call",
            # ^ We want to call a tool
            "tool": best_tool,
            # ^ Name of best matching tool
            "confidence": min(confidence, 1.0),
            # ^ Confidence capped at 1.0 (100%)
            # min() ensures it never exceeds 1.0
            "scores": scores,
            # ^ All scores (for debugging)
        }
    
    # Default to general conversation (no tool matches)
    return {
        "intent": "conversation",
        # ^ Just chat, don't use tools
        "tool": None,
        # ^ No tool selected
        "confidence": 0.0,
        # ^ Zero confidence in tool matching
    }
```

### extract_parameters Method (Lines 114-166)

```python
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
    # ^ Empty dictionary for parameters
    
    if tool_name == "read_file":
        # ^ If we're reading a file
        match = re.search(r"(\S+\.(py|js|txt|json|md|csv))", user_input)
        # ^ Looks for filename with common extensions
        # \S+ = one or more non-space characters
        # () = capture group (saves the match)
        if match:
            # ^ If filename found
            params["path"] = match.group(1)
            # ^ Save filename as 'path' parameter
            # group(1) gets the first captured group
    
    elif tool_name == "search_files":
        # ^ If searching files
        match = re.search(r'(?:find|search)\s+["\']?([^"\']+)["\']?', user_input)
        # ^ Complex pattern to find search keyword
        # (?:find|search) = non-capturing group for "find" or "search"
        # ["\']? = optional quote (single or double)
        # ([^"\']+) = capture everything except quotes
        if match:
            params["keyword"] = match.group(1).strip()
            # ^ Save keyword, strip() removes extra spaces
    
    elif tool_name in ["fetch_api_data", "check_health"]:
        # ^ For API calls or health checks
        match = re.search(r"(http[s]?://\S+)", user_input)
        # ^ Extracts URL starting with http:// or https://
        if match:
            params["url"] = match.group(1)
            # ^ Save URL as 'url' parameter
    
    elif tool_name == "test_endpoint":
        # ^ Testing API endpoint
        match = re.search(r"(http[s]?://[^/\s]+)(/\S+)?", user_input)
        # ^ Splits base URL and endpoint path
        # [^/\s]+ = everything except slash or space
        # (/\S+)? = optional path starting with /
        if match:
            params["base_url"] = match.group(1)
            # ^ First part (e.g., http://localhost:5000)
            params["endpoint"] = match.group(2) or "/"
            # ^ Second part (e.g., /users) or default "/"
    
    elif tool_name in ["get_logs", "analyze_logs"]:
        # ^ For log operations
        match = re.search(r"(\S+\.log)", user_input)
        # ^ Finds filename ending with .log
        if match:
            params["file"] = match.group(1)
            # ^ Save log filename
    
    elif tool_name == "execute_command":
        # ^ For system commands
        match = re.search(r"(?:run|exec|execute)\s+(.+)$", user_input)
        # ^ Gets everything after run/exec/execute
        # (.+)$ = capture rest of line until end
        if match:
            params["command"] = match.group(1).strip()
            # ^ Save command text
    
    return params
    # ^ Return extracted parameters (might be empty if nothing found)
```

---

## Agent Core (cli_agent/agent/core.py)

**Purpose**: The main brain that talks to OpenAI's GPT and decides whether to use tools or just chat.

### Imports (Lines 1-16)

```python
"""Core agent logic for LLM interaction and tool orchestration."""
# ^ Explains this file handles LLM (Large Language Model) and tool management

from typing import Dict, Any, List, Optional
# ^ Type hints

import json
# ^ For working with JSON data

from openai import OpenAI
# ^ OpenAI's Python library for talking to GPT models

from ..utils.config import get_config
# ^ Gets configuration (API keys, settings)
# .. means "go up one folder" (from agent/ to cli_agent/)

from ..utils.logger import get_logger
# ^ Gets logging functionality

from ..utils.exceptions import APIError, ToolError
# ^ Custom error types for better error handling

from ..utils.formatter import print_tool_execution
# ^ Pretty prints tool execution info

from .intent import IntentClassifier
# ^ Imports the intent classifier we just learned about
# . means "current folder" (agent/)

from ..tools.registry import ToolRegistry
# ^ Gets the tool registry (database of all available tools)
```

### Logger Setup (Line 15)

```python
logger = get_logger(__name__)
# ^ Creates a logger for this file
# __name__ = special variable containing current module name
# This helps identify which file logged each message
```

### Agent Class (Lines 18-30)

```python
class Agent:
    """Main agent class for handling LLM interactions and tool execution."""
    
    def __init__(self):
        """Initialize the agent."""
        self.config = get_config()
        # ^ Gets configuration object
        self.client = None
        # ^ Will hold OpenAI client (starts as None)
        self.conversation_history: List[Dict[str, Any]] = []
        # ^ List to remember conversation (for context)
        # Type hint says: List of Dictionaries with string keys and any values
        
        if self.config.is_configured():
            # ^ Checks if API key exists
            self.client = OpenAI(api_key=self.config.api_key)
            # ^ Creates OpenAI client with API key
        
        logger.debug("Agent initialized")
        # ^ Logs initialization (now using DEBUG level instead of INFO)
```

### System Prompt (Lines 32-49)

```python
def _get_system_prompt(self) -> str:
    """Get system prompt for the agent."""
    # ^ Returns instructions for the AI
    
    return """You are a helpful CLI assistant that helps users with various tasks.
You have access to tools that can:
- Read and search files
- Make API calls and check service health
- Analyze logs and detect issues
- Execute system commands (safely)
- Check environment variables

When a user asks you to do something:
1. Determine if you need to use a tool
2. If yes, call the appropriate tool with correct parameters
3. Use the tool result to provide a helpful response
4. Be concise but informative
5. Format your responses clearly

If you're not sure about something, ask for clarification."""
```

### process_request Method (Lines 51-104)

This is the **MAIN ENTRY POINT** for processing user commands!

```python
def process_request(self, user_input: str, use_llm: bool = True) -> Dict[str, Any]:
    """
    Process a user request.

    Args:
        user_input: User's input text
        use_llm: Whether to use LLM for processing (default True)

    Returns:
        Dictionary with response and metadata
    """
    try:
        # Try-except block catches errors
        # First, try rule-based intent classification
        intent = IntentClassifier.classify(user_input)
        # ^ Uses the IntentClassifier to figure out what user wants
        
        logger.debug(f"Classified intent: {intent}")
        # ^ Logs the classification result
        
        # If high confidence tool match, use it directly
        if intent["intent"] == "tool_call" and intent["confidence"] > 0.3:
            # ^ Checks if: 1) wants to call tool AND 2) confidence > 30%
            tool_name = intent["tool"]
            # ^ Gets the tool name
            params = IntentClassifier.extract_parameters(user_input, tool_name)
            # ^ Extracts parameters (like file paths, URLs) from user input
            
            logger.debug(f"Direct tool call: {tool_name} with params: {params}")
            # ^ Logs the tool call details
            
            # Execute tool
            result = self._execute_tool(tool_name, params)
            # ^ Calls the tool (defined later)
            
            return {
                "success": True,
                # ^ Operation succeeded
                "response": self._format_tool_result(tool_name, result),
                # ^ Formats tool result nicely
                "tool_used": tool_name,
                # ^ Which tool was used
                "parameters": params,
                # ^ What parameters were passed
                "used_llm": False,
                # ^ Didn't use LLM (used rule-based matching)
            }
        
        # Otherwise, use LLM if available and requested
        if use_llm and self.client:
            # ^ If LLM usage allowed AND OpenAI client exists
            return self._process_with_llm(user_input)
            # ^ Use AI to understand request (explained next)
        
        # Fallback: simple response (no LLM, no tool match)
        return {
            "success": True,
            "response": f"I understood: '{user_input}'. Configure OpenAI API key for advanced features.",
            # ^ Tells user they need API key for AI features
            "tool_used": None,
            "used_llm": False,
        }
    
    except Exception as e:
        # ^ Catches ANY error
        logger.error(f"Error processing request: {e}", exc_info=True)
        # ^ Logs error with full traceback (exc_info=True)
        return {
            "success": False,
            "response": f"Error: {str(e)}",
            # ^ Shows error to user
            "error": str(e),
        }
```

### _process_with_llm Method (Lines 106-190)

Uses OpenAI's GPT to understand complex requests:

```python
def _process_with_llm(self, user_input: str) -> Dict[str, Any]:
    """Process request using LLM with tool calling."""
    try:
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            # ^ Messages have roles: "user", "assistant", "system", "tool"
            "content": user_input,
            # ^ The actual message text
        })
        
        # Get tool definitions
        tools = ToolRegistry.get_tool_definitions()
        # ^ Gets all tools in format OpenAI understands
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.config.model,
            # ^ Which AI model to use (e.g., gpt-4o-mini)
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                # ^ System instructions (defines AI's behavior)
                *self.conversation_history,
                # ^ Unpacks conversation history into the list
                # The * operator expands the list
            ],
            tools=tools,
            # ^ Tells AI what tools it can use
            tool_choice="auto",
            # ^ Let AI decide whether to use tools
            max_tokens=1000,
            # ^ Limits response length (saves money!)
        )
        
        assistant_message = response.choices[0].message
        # ^ Gets AI's response message
        
        # Check if tool call requested
        if assistant_message.tool_calls:
            # ^ If AI wants to use a tool
            tool_call = assistant_message.tool_calls[0]
            # ^ Gets first tool call
            tool_name = tool_call.function.name
            # ^ Extracts tool name
            tool_args = json.loads(tool_call.function.arguments)
            # ^ Parses arguments from JSON string to dictionary
            
            logger.info(f"LLM requested tool call: {tool_name}")
            # ^ Logs tool call
            
            # Execute the tool
            result = self._execute_tool(tool_name, tool_args)
            # ^ Runs the tool
            
            # Send tool result back to LLM
            self.conversation_history.append(assistant_message.to_dict())
            # ^ Adds AI's tool request to history
            self.conversation_history.append({
                "role": "tool",
                # ^ Special role for tool responses
                "tool_call_id": tool_call.id,
                # ^ Links response to specific tool call
                "content": json.dumps(result),
                # ^ Converts result to JSON string
            })
            
            # Get final response from LLM
            final_response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    *self.conversation_history,
                ],
                max_tokens=1000,
            )
            
            response_text = final_response.choices[0].message.content
            # ^ Gets AI's final explanation
            
            return {
                "success": True,
                "response": response_text,
                "tool_used": tool_name,
                "parameters": tool_args,
                "tool_result": result,
                # ^ Includes raw tool result
                "used_llm": True,
                # ^ Yes, used LLM
            }
        
        # No tool call, just response
        response_text = assistant_message.content
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text,
        })
        
        return {
            "success": True,
            "response": response_text,
            "tool_used": None,
            "used_llm": True,
        }
    
    except Exception as e:
        # ^ Error handling
        logger.error(f"LLM processing error: {e}", exc_info=True)
        raise APIError(f"Failed to process with LLM: {str(e)}")
        # ^ Wraps error in custom APIError
```

### _execute_tool Method (Lines 192-207)

```python
def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with given parameters."""
    try:
        logger.debug(f"Executing tool: {tool_name}")
        # ^ Logs tool execution (DEBUG level now)
        
        print_tool_execution(tool_name, params)
        # ^ Prints nice formatted output to terminal
        
        result = ToolRegistry.execute_tool(tool_name, **params)
        # ^ Executes tool from registry
        # **params unpacks dictionary into keyword arguments
        # Example: if params = {"file": "test.log"}, it becomes:
        # execute_tool(tool_name, file="test.log")
        
        logger.debug(f"Tool result: {result}")
        # ^ Logs result
        
        return result
    
    except ToolError:
        # ^ Re-raises ToolError as-is (already handled)
        raise
    except Exception as e:
        # ^ Wraps other errors in ToolError
        raise ToolError(tool_name, str(e), original_error=e)
```

### _format_tool_result Method (Lines 209-243)

Makes tool results look pretty:

```python
def _format_tool_result(
    self, tool_name: str, result: Dict[str, Any]
) -> str:
    """Format tool result for display."""
    if not result.get("success"):
        # ^ Checks if result failed
        return f"❌ Tool '{tool_name}' failed: {result.get('error', 'Unknown error')}"
        # ^ Shows error message
    
    # Format based on tool type
    formatters = {
        # ^ Dictionary of lambda functions (one-line functions)
        "read_file": lambda r: f"📄 File contents:\n{r.get('content', '')}",
        # ^ Simple formatter for read_file
        
        "check_health": lambda r: (
            f"✅ Status: {r['status'].upper()}\n"
            f"HTTP Code: {r['http_status']}\n"
            f"Response Time: {r['response_time_ms']}ms"
        ),
        # ^ Formats health check results
        
        "analyze_logs": lambda r: (
            f"📊 Log Analysis:\n"
            f"Total Lines: {r['total_lines']}\n"
            f"Errors: {r['error_count']}\n"
            f"Warnings: {r['warning_count']}"
        ),
        # ^ This is what formats your log analysis output!
        
        "detect_cors_issue": lambda r: (
            f"{'⚠️' if r['cors_detected'] else '✅'} CORS Analysis:\n"
            f"Issues Found: {r['issue_count']}\n"
            f"Recommendation: {r['recommendation']}"
        ),
        # ^ Conditional emoji based on whether CORS issue found
        
        "validate_env": lambda r: (
            f"{'✅' if r['success'] else '⚠️'} Environment Check:\n"
            f"Set: {len(r['set'])}\n"
            f"Missing: {len(r['missing'])}"
        ),
    }
    
    formatter = formatters.get(tool_name, lambda r: str(r))
    # ^ Gets formatter for this tool, or default that just converts to string
    return formatter(result)
    # ^ Applies formatter to result
```

### Other Methods (Lines 245-253)

```python
def clear_history(self) -> None:
    """Clear conversation history."""
    self.conversation_history.clear()
    # ^ Empties the conversation memory
    logger.info("Conversation history cleared")


def get_available_tools(self) -> List[str]:
    """Get list of available tool names."""
    return ToolRegistry.list_tools()
    # ^ Returns list of all tool names
```

---

## How Everything Connects

Here's the complete flow when you type `agent analyze test_sample.log`:

### Step 1: main.py Receives Command
```python
# In main.py cmd_analyze function:
agent = Agent()
result = agent.process_request(f"analyze logs {args.file}")
```

### Step 2: process_request Classifies Intent
```python
# In core.py:
intent = IntentClassifier.classify("analyze logs test_sample.log")
# Returns: {"intent": "tool_call", "tool": "analyze_logs", "confidence": 1.0}
```

### Step 3: Parameters Extracted
```python
params = IntentClassifier.extract_parameters("analyze logs test_sample.log", "analyze_logs")
# Returns: {"file": "test_sample.log"}
```

### Step 4: Tool Executed
```python
result = self._execute_tool("analyze_logs", {"file": "test_sample.log"})
# Tool runs and returns: {"success": True, "total_lines": 13, "error_count": 7, ...}
```

### Step 5: Result Formatted
```python
response = self._format_tool_result("analyze_logs", result)
# Returns formatted string with emojis showing analysis
```

### Step 6: Output Displayed
```python
# Back in main.py:
print_result(result["response"])
# Shows the beautiful boxed output you see!
```

---

## Continue Reading

- **Part 1**: [Project Structure & Main Entry Point](DOCS_BEGINNER_GUIDE_PART1.md)
- **Part 3**: [Tools System](docs/PART3_TOOLS_SYSTEM.md) - How tools work internally
- **Part 4**: [Utilities](docs/PART4_UTILITIES.md) - Configuration, logging, exceptions
- **Part 5**: [Debugger](docs/PART5_DEBUGGER.md) - Debug analysis
- **Part 6**: [Tests](docs/PART6_TESTS.md) - Testing everything
