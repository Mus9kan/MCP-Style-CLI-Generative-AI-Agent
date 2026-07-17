# Complete Project Documentation - Summary Guide

## Quick Navigation

This is your master index for all documentation files:

### Part 1: Foundation
**File**: `DOCS_BEGINNER_GUIDE_PART1.md`
- Project structure
- Configuration files (requirements.txt, .env, pyproject.toml)
- Main entry point (main.py) - How commands are parsed
- All command handlers explained

### Part 2: AI Brain
**File**: `DOCS_BEGINNER_GUIDE_PART2.md`
- Intent Classifier (intent.py) - How agent understands your commands
- Agent Core (core.py) - LLM integration and tool orchestration
- Complete request flow explained step-by-step

### Part 3: Tools System (This File)
- How tools work internally
- File operations (file_tools.py)
- API operations (api_tools.py)
- Log analysis (log_tools.py)
- System operations (system_tools.py)

### Part 4: Utilities
- Configuration management
- Logging system
- Exception handling
- Output formatting

### Part 5: Debugger
- Debug analyzer
- Issue detection
- Report generation

### Part 6: Testing
- Unit tests
- Integration tests
- Running tests

---

## Part 3: Tools System - Deep Dive

### What is a Tool?

A **tool** is a function the AI can call to perform specific tasks. Think of tools as the agent's "hands" that actually do things.

### The Base Class: BaseTool

All tools inherit from `BaseTool`:

```python
from .base import BaseTool
from .registry import register_tool

@register_tool  # This decorator automatically registers the tool
class MyTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."}
        },
        "required": ["param1"]
    }
    
    def execute(self, param1: str):
        # Your code here
        return {"success": True, "result": "..."}
```

### Key Concepts:

1. **@register_tool decorator**: Automatically adds your tool to the registry
2. **name**: Unique identifier (used in code)
3. **description**: Tells AI when to use this tool
4. **parameters**: JSON Schema defining what inputs the tool accepts
5. **execute()**: The actual code that runs

---

## File Operations (file_tools.py)

### 1. ReadFileTool

**Name**: `read_file`  
**Purpose**: Reads file contents safely

**Parameters**:
- `path` (required): File path
- `max_lines` (optional): Max lines to read (default 100)

**Code Explanation**:
```python
def execute(self, path: str, max_lines: int = 100):
    file_path = Path(path)
    # ^ Converts string to Path object (easier to work with)
    
    if not file_path.exists():
        raise ToolError(self.name, f"File not found: {path}")
    # ^ Checks file exists
    
    if not file_path.is_file():
        raise ToolError(self.name, f"Not a file: {path}")
    # ^ Ensures it's actually a file (not directory)
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = []
        for i, line in enumerate(f):
            if i >= max_lines:
                lines.append(f"... ({max_lines} lines limit reached)")
                break
            lines.append(line.rstrip())
        # ^ Reads file line-by-line, stops at max_lines
    
    return {
        "success": True,
        "path": str(file_path.absolute()),
        "content": content,
        "lines_read": len(lines),
    }
```

### 2. SearchFilesTool

**Name**: `search_files`  
**Purpose**: Searches for keyword across multiple files

**Parameters**:
- `keyword` (required): What to search for
- `directory` (optional): Where to search (default ".")
- `file_pattern` (optional): File type filter (e.g., "*.py")

**Key Technique**:
```python
for file_path in search_dir.rglob(file_pattern):
    # ^ rglob recursively searches subdirectories
    if file_path.is_file():
        with open(file_path, "r", errors="ignore") as f:
            content = f.read()
            if keyword in content:
                count = content.count(keyword)
                # ^ Counts occurrences
```

### 3. SummarizeFileTool

**Name**: `summarize_file`  
**Purpose**: Gets file metadata and statistics

**Returns**:
- File size (bytes and KB)
- Line count
- File type (based on extension)
- Creation/modification timestamps

---

## API Operations (api_tools.py)

### 1. FetchAPIDataTool

**Name**: `fetch_api_data`  
**Purpose**: Makes HTTP GET requests to APIs

**Key Code**:
```python
response = requests.get(url, timeout=timeout)
response.raise_for_status()
# ^ Raises error if HTTP status is 4xx or 5xx

try:
    data = response.json()
    # ^ Parses JSON response
except ValueError:
    data = {"text": response.text[:1000]}
    # ^ Falls back to plain text
```

**Error Handling**:
- `Timeout`: Request took too long
- `ConnectionError`: Server unreachable
- `HTTPError`: Invalid response (404, 500, etc.)

### 2. CheckHealthTool

**Name**: `check_health`  
**Purpose**: Checks if a service is running

**Smart Features**:
```python
start_time = time.time()
response = requests.get(url, timeout=timeout)
response_time = round((time.time() - start_time) * 1000, 2)
# ^ Measures response time in milliseconds

status = "healthy" if response.status_code < 400 else "unhealthy"
# ^ Status based on HTTP code
```

**Returns**:
- Status: healthy/unhealthy/timeout/unreachable
- HTTP status code
- Response time in ms
- Timestamp

### 3. TestEndpointTool

**Name**: `test_endpoint`  
**Purpose**: Tests API endpoints with different HTTP methods

**Supports**:
- GET, POST, PUT, DELETE methods
- Response time analysis
- Error detection (4xx, 5xx errors)
- Slow response warning (>1000ms)

---

## Log Analysis (log_tools.py)

### 1. GetLogsTool

**Name**: `get_logs`  
**Purpose**: Retrieves recent log entries

**Smart Feature**:
```python
with open(log_path, "r") as f:
    all_lines = f.readlines()
    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
    # ^ Gets last N lines only
```

### 2. AnalyzeLogsTool

**Name**: `analyze_logs`  
**Purpose**: Comprehensive log analysis

**Analysis Steps**:

1. **Count Log Levels**:
```python
level_patterns = {
    "ERROR": r"\b(ERROR|error|Error|FATAL)\b",
    "WARNING": r"\b(WARNING|warning|WARN)\b",
    "INFO": r"\b(INFO|info)\b",
}

for level, pattern in level_patterns.items():
    matches = re.findall(pattern, content)
    level_counts[level] = len(matches)
    # ^ Uses regex to count each log level
```

2. **Extract Error Messages**:
```python
error_lines = []
for line in lines:
    if re.search(level_patterns["ERROR"], line):
        error_lines.append(line.strip())
        # ^ Collects all error lines
```

3. **Timestamp Detection**:
```python
timestamp_pattern = r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
timestamps = re.findall(timestamp_pattern, content)
# ^ Finds ISO format timestamps
```

**Returns**:
- Total lines analyzed
- Count by log level (ERROR, WARNING, INFO, DEBUG, CRITICAL)
- Sample error messages (first 10)
- Whether timestamps present

### 3. DetectCorsIssueTool

**Name**: `detect_cors_issue`  
**Purpose**: Finds CORS-related errors in logs

**CORS Patterns Detected**:
```python
cors_patterns = [
    r"CORS.*(?:policy|error|issue)",
    r"Access-Control-Allow-Origin",
    r"(?:cross-origin|CORS).*request",
    r"No\s*['\"]Access-Control-Allow-Origin['\"]\s*header",
    r"Origin\s+(?:not\s+)?allowed",
    r"preflight.*fail",
]
```

**Smart Recommendation**:
```python
recommendation = (
    "Configure CORS headers on server: Access-Control-Allow-Origin: *"
    if has_cors_issue
    else "No CORS issues detected"
)
```

---

## System Operations (system_tools.py)

### 1. ExecuteCommandTool

**Name**: `execute_command`  
**Purpose**: Runs shell commands safely

**Safety Features**:
```python
# Blocked commands for safety
blocked_commands = [
    "rm -rf",      # Dangerous deletion
    "sudo",        # Privilege escalation
    "chmod 777",   # Insecure permissions
    "dd",          # Disk operations
    "mkfs",        # Filesystem creation
]

for blocked in blocked_commands:
    if blocked in command:
        raise ToolError(self.name, f"Dangerous command blocked: {blocked}")
```

**Execution**:
```python
import subprocess

result = subprocess.run(
    command,
    shell=True,
    capture_output=True,
    text=True,
    timeout=30  # Safety timeout
)
```

### 2. ValidateEnvTool

**Name**: `validate_env`  
**Purpose**: Checks environment variables

**Checks**:
- Required variables set
- Missing variables
- Variable values validity

### 3. SystemInfoTool

**Name**: `system_info`  
**Purpose**: Gets system details

**Returns**:
- OS name and version
- Python version
- CPU count
- Memory info
- Disk usage

---

## Tool Registry Explained

The **ToolRegistry** is a central database of all available tools.

### Singleton Pattern

```python
class ToolRegistry:
    _instance = None  # Only one instance ever exists
    _tools = {}       # Dictionary of tools
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        # ^ Ensures only ONE registry exists
```

### Registration Process

When you use `@register_tool`:

```python
@register_tool
class ReadFileTool(BaseTool):
    ...

# Behind the scenes:
# 1. Class is created
# 2. Instance is made: tool_instance = ReadFileTool()
# 3. Added to registry: ToolRegistry._tools["read_file"] = tool_instance
```

### Tool Execution Flow

```python
# When agent calls a tool:
result = ToolRegistry.execute_tool("read_file", path="test.txt")

# Inside execute_tool:
tool = cls.get_tool(name)  # Get tool from dictionary
return tool.execute(**kwargs)  # Call execute with parameters
```

---

## Error Handling

### Custom Exceptions

**ToolError**:
```python
class ToolError(Exception):
    def __init__(self, tool_name: str, message: str, original_error=None):
        self.tool_name = tool_name
        self.message = message
        self.original_error = original_error
        super().__init__(f"Tool '{tool_name}' failed: {message}")
```

**Usage**:
```python
try:
    # Some operation
    raise FileNotFoundError("File not found")
except Exception as e:
    raise ToolError("read_file", str(e), original_error=e)
    # ^ Wraps original error with context
```

### ValidationError

For parameter validation:
```python
if not path:
    raise ValidationError("Path cannot be empty")
```

---

## Real Example: analyze_logs Command

Let's trace what happens when you run:
```bash
agent analyze test_sample.log
```

### Step 1: main.py
```python
def cmd_analyze(args):
    agent = Agent()
    result = agent.process_request(f"analyze logs {args.file}")
    # ^ Calls: process_request("analyze logs test_sample.log")
```

### Step 2: core.py - Intent Classification
```python
intent = IntentClassifier.classify("analyze logs test_sample.log")
# Returns: {"intent": "tool_call", "tool": "analyze_logs", "confidence": 1.0}

params = IntentClassifier.extract_parameters(...)
# Returns: {"file": "test_sample.log"}
```

### Step 3: core.py - Tool Execution
```python
result = self._execute_tool("analyze_logs", {"file": "test_sample.log"})
# ^ Calls ToolRegistry.execute_tool("analyze_logs", file="test_sample.log")
```

### Step 4: log_tools.py - Actual Work
```python
class AnalyzeLogsTool(BaseTool):
    def execute(self, file: str):
        with open(file, "r") as f:
            content = f.read()
        
        # Count ERROR patterns
        matches = re.findall(r"\bERROR\b", content)
        error_count = len(matches)
        
        return {
            "success": True,
            "total_lines": len(content.split("\n")),
            "error_count": error_count,
            "warning_count": ...,
        }
```

### Step 5: core.py - Formatting
```python
response = self._format_tool_result("analyze_logs", result)
# Returns formatted string:
# "📊 Log Analysis:\nTotal Lines: 13\nErrors: 7\nWarnings: 2"
```

### Step 6: main.py - Display
```python
print_result(result["response"])
# Shows beautiful boxed output
```

---

## Adding Your Own Tool

### Example: WeatherTool

Let's create a new tool that fetches weather:

```python
# cli_agent/tools/weather_tools.py
from .base import BaseTool
from .registry import register_tool
import requests

@register_tool
class WeatherTool(BaseTool):
    name = "get_weather"
    description = "Get current weather for a city"
    parameters = {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name",
            },
            "unit": {
                "type": "string",
                "description": "celsius or fahrenheit",
                "enum": ["celsius", "fahrenheit"],
            },
        },
        "required": ["city"],
    }
    
    def execute(self, city: str, unit: str = "celsius"):
        try:
            # Use free weather API
            url = f"https://wttr.in/{city}?format=%t+%C"
            response = requests.get(url, timeout=10)
            
            return {
                "success": True,
                "city": city,
                "weather": response.text.strip(),
                "unit": unit,
            }
        except Exception as e:
            raise ToolError("get_weather", str(e))
```

### Register in main.py

Add to imports:
```python
from .tools import file_tools, api_tools, log_tools, system_tools, weather_tools
```

Now you can use:
```bash
agent get weather in New York
```

---

## Best Practices

### 1. Always Validate Inputs
```python
if not path:
    raise ValidationError("Path is required")
```

### 2. Use Timeouts for Network Calls
```python
requests.get(url, timeout=30)  # Prevent hanging
```

### 3. Handle Encoding Issues
```python
open(file, "r", encoding="utf-8", errors="ignore")
```

### 4. Provide Clear Error Messages
```python
raise ToolError(self.name, f"File not found: {path}")
# Better than: raise Exception("Error")
```

### 5. Return Structured Data
```python
return {
    "success": True,
    "data": ...,
    "metadata": ...,
}
```

### 6. Document Everything
```python
"""Clear docstring explaining what tool does."""
```

---

## Continue Reading

- **Part 4**: [Utilities](docs/PART4_UTILITIES.md) - Config, logging, exceptions
- **Part 5**: [Debugger](docs/PART5_DEBUGGER.md) - Debug analysis
- **Part 6**: [Tests](docs/PART6_TESTS.md) - Testing strategies

---

## Quick Reference Card

### Tool Categories

| Category | Tools | Purpose |
|----------|-------|---------|
| **Files** | read_file, search_files, summarize_file | File operations |
| **API** | fetch_api_data, check_health, test_endpoint | Web services |
| **Logs** | get_logs, analyze_logs, detect_cors_issue | Log analysis |
| **System** | execute_command, validate_env, system_info | System ops |

### Common Patterns

**Regex for filenames**:
```python
r"(\S+\.(py|js|txt|json))"  # Matches filenames with extensions
```

**Safe file reading**:
```python
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
```

**HTTP request with error handling**:
```python
try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
except requests.Timeout:
    raise ToolError("Request timed out")
```

---

**Made with ❤️ for beginners learning Python and AI agents!**
