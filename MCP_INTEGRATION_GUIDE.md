# CLI-MCP Integration Guide

Complete documentation of the Model Context Protocol (MCP) implementation in the CLI AI Agent, including all tool definitions, function declarations, and integration patterns.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [MCP Protocol Implementation](#mcp-protocol-implementation)
3. [Tool Registry System](#tool-registry-system)
4. [Complete Tool Reference](#complete-tool-reference)
5. [CLI Command Mapping](#cli-command-mapping)
6. [LLM Integration](#llm-integration)
7. [Adding Custom Tools](#adding-custom-tools)
8. [API Reference](#api-reference)

---

## 🏗️ Architecture Overview

The CLI AI Agent implements MCP (Model Context Protocol) to provide standardized tool calling capabilities for Large Language Models. This allows the LLM to understand, select, and execute tools dynamically.

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                   CLI Interface (main.py)                │
│  - argparse-based command parsing                       │
│  - 12+ CLI commands                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Agent Core (agent/core.py)                  │
│  - Intent classification                                │
│  - LLM orchestration                                    │
│  - Tool execution with retry                            │
│  - Context memory management                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            Tool Registry (tools/registry.py)             │
│  - Singleton pattern                                    │
│  - Dynamic tool discovery                               │
│  - MCP-compliant tool definitions                       │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              MCP Tools (13 Total)                        │
│  ├── File Tools (3): read, search, summarize            │
│  ├── API Tools (3): fetch, health, test                 │
│  ├── Log Tools (3): get, analyze, detect CORS           │
│  └── System Tools (4): exec, validate, check, info      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔌 MCP Protocol Implementation

### What is MCP?

Model Context Protocol (MCP) is a standardized way for LLMs to discover and call external tools/functions. It follows the OpenAI Function Calling specification.

### MCP Tool Definition Format

Every tool in this system follows this JSON Schema structure:

```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "Human-readable description",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                },
                "param2": {
                    "type": "integer",
                    "description": "Another parameter"
                }
            },
            "required": ["param1"]
        }
    }
}
```

### Base Tool Class

**File**: [`cli_agent/tools/base.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/tools/base.py)

```python
class BaseTool(ABC):
    """Abstract base class for all MCP tools."""
    
    # Required attributes
    name: str = "tool_name"
    description: str = "Tool description"
    parameters: Dict[str, Any] = {}  # JSON Schema
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool logic"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MCP/OpenAI format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
    
    def validate_params(self, **kwargs) -> bool:
        """Validate parameters against JSON Schema"""
        pass
```

---

## 🗂️ Tool Registry System

**File**: [`cli_agent/tools/registry.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/tools/registry.py)

The ToolRegistry is a singleton that manages all MCP tools.

### Registry Functions

```python
class ToolRegistry:
    """Central MCP tool registry."""
    
    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """Register a tool class"""
        tool_instance = tool_class()
        cls._tools[tool_instance.name] = tool_instance
        return tool_class
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return cls._tools.get(name)
    
    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """Get all registered tools"""
        return list(cls._tools.values())
    
    @classmethod
    def get_tool_definitions(cls) -> List[Dict]:
        """Get MCP definitions for LLM API"""
        return [tool.to_dict() for tool in cls._tools.values()]
    
    @classmethod
    def list_tools(cls) -> List[str]:
        """List all tool names"""
        return list(cls._tools.keys())
    
    @classmethod
    def execute_tool(cls, name: str, **kwargs) -> Dict:
        """Execute a tool by name"""
        tool = cls.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        return tool.execute(**kwargs)
```

### Tool Registration Decorator

```python
@register_tool  # Automatically registers the tool
class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    parameters = {...}
    
    def execute(self, **kwargs):
        return {"success": True}
```

---

## 📚 Complete Tool Reference

### 📁 File Operations Tools (3 tools)

**File**: [`cli_agent/tools/file_tools.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/tools/file_tools.py)

#### 1. read_file

**Purpose**: Read contents of a file

**MCP Definition**:
```python
{
    "name": "read_file",
    "description": "Read the contents of a file at the specified path",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read"
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum number of lines to read (default: 100)"
            }
        },
        "required": ["path"]
    }
}
```

**Function Signature**:
```python
def execute(self, path: str, max_lines: int = 100) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "path": "/absolute/path/to/file",
    "content": "File contents here...",
    "lines_read": 50
}
```

**CLI Command**: `agent read <file>`

---

#### 2. search_files

**Purpose**: Search for files containing specific keyword

**MCP Definition**:
```python
{
    "name": "search_files",
    "description": "Search for files containing a specific keyword or pattern",
    "parameters": {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Keyword or pattern to search for"
            },
            "directory": {
                "type": "string",
                "description": "Directory to search in (default: current directory)"
            },
            "file_pattern": {
                "type": "string",
                "description": "File pattern to match (e.g., '*.py')"
            }
        },
        "required": ["keyword"]
    }
}
```

**Function Signature**:
```python
def execute(
    self,
    keyword: str,
    directory: str = ".",
    file_pattern: str = "*"
) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "keyword": "TODO",
    "files_checked": 25,
    "matches_found": 3,
    "results": [
        {"file": "/path/to/file1.py", "occurrences": 5},
        {"file": "/path/to/file2.py", "occurrences": 2}
    ]
}
```

**CLI Command**: `agent find "<keyword>" in <directory>`

---

#### 3. summarize_file

**Purpose**: Get summary information about a file

**MCP Definition**:
```python
{
    "name": "summarize_file",
    "description": "Get summary information about a file (size, lines, type)",
    "parameters": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file"
            }
        },
        "required": ["path"]
    }
}
```

**Function Signature**:
```python
def execute(self, path: str) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "path": "/absolute/path",
    "filename": "app.py",
    "extension": ".py",
    "type": "Python",
    "size_bytes": 4096,
    "size_kb": 4.0,
    "line_count": 150,
    "created": 1704067200.0,
    "modified": 1704153600.0
}
```

**CLI Command**: `agent info <file>` or `agent summarize <file>`

---

### 🌐 API Operation Tools (3 tools)

**File**: [`cli_agent/tools/api_tools.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/tools/api_tools.py)

#### 4. fetch_api_data

**Purpose**: Fetch data from REST API endpoint

**MCP Definition**:
```python
{
    "name": "fetch_api_data",
    "description": "Fetch data from a REST API endpoint using HTTP GET request",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL of the API endpoint"
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds (default: 30)"
            }
        },
        "required": ["url"]
    }
}
```

**Function Signature**:
```python
def execute(self, url: str, timeout: int = 30) -> Dict[str, Any]
```

**Retry Configuration**:
- Max retries: 3
- Base delay: 1.0s
- Max delay: 30.0s
- Retryable: Timeout, ConnectionError

**Return Value**:
```python
{
    "success": True,
    "url": "https://api.example.com/data",
    "status_code": 200,
    "data": {"key": "value"},
    "content_length": 1024
}
```

**CLI Command**: `agent fetch-api <url>`

---

#### 5. check_health

**Purpose**: Check health/status of API endpoint

**MCP Definition**:
```python
{
    "name": "check_health",
    "description": "Check the health status of a web service or API endpoint",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL of the service to check"
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds (default: 10)"
            }
        },
        "required": ["url"]
    }
}
```

**Function Signature**:
```python
def execute(self, url: str, timeout: int = 10) -> Dict[str, Any]
```

**Retry Configuration**:
- Max retries: 2
- Base delay: 0.5s
- Max delay: 10.0s

**Return Value**:
```python
{
    "success": True,
    "url": "http://localhost:5000",
    "status": "healthy",
    "http_status": 200,
    "response_time_ms": 45.2,
    "timestamp": "2024-01-01 12:00:00"
}
```

**CLI Command**: `agent health-check <url>`

---

#### 6. test_endpoint

**Purpose**: Test API endpoint with various HTTP methods

**MCP Definition**:
```python
{
    "name": "test_endpoint",
    "description": "Test an API endpoint with HTTP methods and validate responses",
    "parameters": {
        "type": "object",
        "properties": {
            "endpoint": {
                "type": "string",
                "description": "API endpoint path (e.g., '/api/users')"
            },
            "base_url": {
                "type": "string",
                "description": "Base URL (e.g., 'http://localhost:5000')"
            },
            "method": {
                "type": "string",
                "description": "HTTP method (GET, POST, PUT, DELETE)"
            }
        },
        "required": ["endpoint", "base_url"]
    }
}
```

**Function Signature**:
```python
def execute(
    self,
    endpoint: str,
    base_url: str,
    method: str = "GET"
) -> Dict[str, Any]
```

**Retry Configuration**:
- Max retries: 2
- Base delay: 1.0s
- Max delay: 20.0s

**Return Value**:
```python
{
    "success": True,
    "endpoint": "/api/users",
    "base_url": "http://localhost:5000",
    "method": "GET",
    "status_code": 200,
    "response_time_ms": 120.5,
    "issues": ["Slow response: 120.5ms"],
    "headers": {"Content-Type": "application/json", ...}
}
```

**CLI Command**: `agent test-api <endpoint> --base-url <url>`

---

### 📊 Log Analysis Tools (3 tools)

**File**: [`cli_agent/tools/log_tools.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/tools/log_tools.py)

#### 7. get_logs

**Purpose**: Retrieve log entries from file

**MCP Definition**:
```python
{
    "name": "get_logs",
    "description": "Retrieve log entries from a log file",
    "parameters": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to the log file"
            },
            "lines": {
                "type": "integer",
                "description": "Number of recent lines to retrieve (default: 50)"
            }
        },
        "required": ["file"]
    }
}
```

**Function Signature**:
```python
def execute(self, file: str, lines: int = 50) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "file": "/path/to/app.log",
    "total_lines": 1000,
    "retrieved_lines": 50,
    "logs": "2024-01-01 ERROR: ...\n..."
}
```

**CLI Command**: `agent get logs <file>`

---

#### 8. analyze_logs

**Purpose**: Analyze log file for patterns and issues

**MCP Definition**:
```python
{
    "name": "analyze_logs",
    "description": "Analyze a log file for errors, warnings, and patterns",
    "parameters": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to the log file"
            }
        },
        "required": ["file"]
    }
}
```

**Function Signature**:
```python
def execute(self, file: str) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "file": "/path/to/app.log",
    "total_lines": 1000,
    "level_counts": {
        "ERROR": 15,
        "WARNING": 42,
        "INFO": 800,
        "DEBUG": 100,
        "CRITICAL": 3
    },
    "error_count": 18,
    "warning_count": 42,
    "has_timestamps": True,
    "sample_errors": ["2024-01-01 ERROR: Connection failed", ...]
}
```

**CLI Command**: `agent analyze logs <file>`

---

#### 9. detect_cors_issue

**Purpose**: Detect CORS-related issues in logs

**MCP Definition**:
```python
{
    "name": "detect_cors_issue",
    "description": "Analyze logs to detect CORS (Cross-Origin Resource Sharing) errors",
    "parameters": {
        "type": "object",
        "properties": {
            "logs": {
                "type": "string",
                "description": "Log content to analyze"
            },
            "file": {
                "type": "string",
                "description": "Path to log file (alternative to direct logs)"
            }
        },
        "required": []
    }
}
```

**Function Signature**:
```python
def execute(self, logs: str = None, file: str = None) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "cors_detected": True,
    "issue_count": 5,
    "issues_found": ["CORS policy error", "Access-Control-Allow-Origin missing"],
    "related_lines": ["2024-01-01 ERROR: CORS blocked...", ...],
    "recommendation": "Configure CORS headers on server: Access-Control-Allow-Origin: *"
}
```

**CLI Command**: `agent debug cors issue`

---

### 💻 System Operation Tools (4 tools)

**File**: [`cli_agent/tools/system_tools.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/tools/system_tools.py)

#### 10. execute_command

**Purpose**: Execute system commands safely

**MCP Definition**:
```python
{
    "name": "execute_command",
    "description": "Execute a system command and return output (use with caution)",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Command to execute"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 30)"
            }
        },
        "required": ["command"]
    }
}
```

**Function Signature**:
```python
def execute(self, command: str, timeout: int = 30) -> Dict[str, Any]
```

**Security Features**:
- Blocks dangerous commands: `rm -rf`, `del /f`, `format`, `mkfs`
- Timeout protection
- Output capture

**Return Value**:
```python
{
    "success": True,
    "command": "ls -la",
    "return_code": 0,
    "stdout": "total 48\ndrwxr-xr-x ...",
    "stderr": "",
    "timeout": False
}
```

**CLI Command**: `agent exec <command>`

---

#### 11. validate_env

**Purpose**: Validate environment variables

**MCP Definition**:
```python
{
    "name": "validate_env",
    "description": "Validate that required environment variables are set",
    "parameters": {
        "type": "object",
        "properties": {
            "variables": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of environment variable names to check"
            }
        },
        "required": []
    }
}
```

**Function Signature**:
```python
def execute(self, variables: List[str] = None) -> Dict[str, Any]
```

**Platform Awareness**:
- Windows: Checks `USERPROFILE`
- Unix/Linux: Checks `HOME`

**Return Value**:
```python
{
    "success": True,
    "checked": 3,
    "set": ["OPENAI_API_KEY", "PATH", "USERPROFILE"],
    "missing": [],
    "details": {
        "OPENAI_API_KEY": {
            "status": "set",
            "length": 51,
            "first_chars": "sk-proj-abc123..."
        },
        ...
    }
}
```

**CLI Command**: `agent validate-env`

---

#### 12. check_env_var

**Purpose**: Check specific environment variable

**MCP Definition**:
```python
{
    "name": "check_env_var",
    "description": "Check the value of a specific environment variable",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the environment variable"
            }
        },
        "required": ["name"]
    }
}
```

**Function Signature**:
```python
def execute(self, name: str) -> Dict[str, Any]
```

**Security**: Automatically masks sensitive values (KEY, SECRET, PASSWORD, TOKEN, API)

**Return Value**:
```python
{
    "success": True,
    "name": "OPENAI_API_KEY",
    "exists": True,
    "value": "***REDACTED***",
    "length": 51,
    "is_sensitive": True
}
```

**CLI Command**: `agent check <VARIABLE_NAME>`

---

#### 13. system_info

**Purpose**: Get system information

**MCP Definition**:
```python
{
    "name": "system_info",
    "description": "Get basic system information (OS, Python version, etc.)",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

**Function Signature**:
```python
def execute(self) -> Dict[str, Any]
```

**Return Value**:
```python
{
    "success": True,
    "os": "Windows",
    "os_version": "10.0.26200",
    "machine": "AMD64",
    "processor": "AMD64 Family 23 Model 24...",
    "python_version": "3.10.11",
    "cwd": "C:\\Users\\Lenovo\\Desktop\\cli_agents",
    "home": "C:\\Users\\Lenovo"
}
```

**CLI Command**: `agent system info`

---

## 🎯 CLI Command Mapping

How CLI commands map to MCP tools:

| CLI Command | MCP Tool | Intent Pattern |
|-------------|----------|----------------|
| `agent read <file>` | `read_file` | `read file`, `.py$`, `.txt$` |
| `agent find "<kw>" in <dir>` | `search_files` | `find ... in`, `search` |
| `agent info <file>` | `summarize_file` | `info`, `summary`, `what does` |
| `agent fetch-api <url>` | `fetch_api_data` | `fetch data`, `api call`, URLs |
| `agent health-check <url>` | `check_health` | `health`, `status`, `check health of` |
| `agent test-api <endpoint>` | `test_endpoint` | `test endpoint`, `api test` |
| `agent get logs <file>` | `get_logs` | `get logs`, `log file` |
| `agent analyze logs <file>` | `analyze_logs` | `analyze logs`, `log analysis` |
| `agent debug cors` | `detect_cors_issue` | `cors`, `CORS`, `cross-origin` |
| `agent exec <cmd>` | `execute_command` | `run`, `exec`, `execute` |
| `agent validate-env` | `validate_env` | `validate env`, `environment variables` |
| `agent check <VAR>` | `check_env_var` | `check variable`, `env <VAR>` |
| `agent system info` | `system_info` | `system info`, `what system` |

---

## 🤖 LLM Integration

### How LLM Calls MCP Tools

**File**: [`cli_agent/agent/core.py`](file:///c:/Users/Lenovo/Desktop/cli_agents/cli_agent/agent/core.py)

#### Step 1: Get Tool Definitions

```python
from cli_agent.tools.registry import ToolRegistry

# Get all MCP tool definitions
tools = ToolRegistry.get_tool_definitions()
# Returns list of tool schemas in OpenAI format
```

#### Step 2: Send to LLM

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ],
    tools=tools,  # MCP tool definitions
    tool_choice="auto",
)
```

#### Step 3: Execute Tool

```python
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)
    
    # Execute via registry
    result = ToolRegistry.execute_tool(tool_name, **tool_args)
```

#### Step 4: Return Result to LLM

```python
# Send tool result back to LLM
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": json.dumps(result),
})

# Get final response
final_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
)
```

---

## 🛠️ Adding Custom Tools

### Step-by-Step Guide

#### 1. Create Tool File

Create `cli_agent/tools/my_tool.py`:

```python
from .base import BaseTool
from .registry import register_tool

@register_tool
class MyCustomTool(BaseTool):
    """My custom tool description."""
    
    name = "my_custom_tool"
    description = "Detailed description of what this tool does"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of param1"
            },
            "param2": {
                "type": "integer",
                "description": "Description of param2"
            }
        },
        "required": ["param1"]
    }
    
    def execute(self, param1: str, param2: int = 10) -> Dict[str, Any]:
        try:
            # Your tool logic here
            result = do_something(param1, param2)
            
            return {
                "success": True,
                "result": result,
                "metadata": {...}
            }
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)
```

#### 2. Import in __init__.py

Edit `cli_agent/tools/__init__.py`:

```python
from . import my_tool  # Add this line
```

#### 3. Add Intent Patterns

Edit `cli_agent/agent/intent.py`:

```python
INTENT_PATTERNS = {
    ...
    "my_custom_tool": [
        r"\b(my|custom)\s+tool\b",
        r"\bdo\s+something\b",
    ],
    ...
}
```

#### 4. Add CLI Command (Optional)

Edit `cli_agent/main.py`:

```python
def cmd_my_tool(args):
    """Handle my-tool command."""
    agent = Agent()
    result = agent.process_request(f"my custom tool {args.param}")
    if result["success"]:
        print_result(result["response"])

# In main():
my_parser = subparsers.add_parser("my-tool", help="Run my custom tool")
my_parser.add_argument("param", help="Parameter")
my_parser.set_defaults(func=cmd_my_tool)
```

#### 5. Test Your Tool

```bash
# Via CLI
agent my-tool "test"

# Via LLM (natural language)
agent do something with test

# List tools
agent tools
```

---

## 📖 API Reference

### Core Classes

#### BaseTool

**Location**: `cli_agent/tools/base.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `execute` | `abstract execute(**kwargs) -> Dict` | Main tool logic (must override) |
| `to_dict` | `to_dict() -> Dict` | Convert to MCP format |
| `validate_params` | `validate_params(**kwargs) -> bool` | Validate against schema |

#### ToolRegistry

**Location**: `cli_agent/tools/registry.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `register` | `register(tool_class) -> Type` | Register a tool |
| `get_tool` | `get_tool(name) -> BaseTool` | Get tool instance |
| `get_all_tools` | `get_all_tools() -> List[BaseTool]` | Get all tools |
| `get_tool_definitions` | `get_tool_definitions() -> List[Dict]` | Get MCP definitions |
| `list_tools` | `list_tools() -> List[str]` | List tool names |
| `execute_tool` | `execute_tool(name, **kwargs) -> Dict` | Execute tool |
| `clear` | `clear() -> None` | Clear registry (testing) |

#### Agent

**Location**: `cli_agent/agent/core.py`

| Method | Signature | Description |
|--------|-----------|-------------|
| `process_request` | `process_request(input, use_llm) -> Dict` | Process user input |
| `_execute_tool` | `_execute_tool(name, params) -> Dict` | Execute with retry |
| `_process_with_llm` | `_process_with_llm(input) -> Dict` | LLM processing |
| `clear_history` | `clear_history() -> None` | Clear conversation |
| `get_available_tools` | `get_available_tools() -> List[str]` | List tools |

---

## 🔧 Configuration

### Retry Settings

Tools use automatic retry with exponential backoff:

```python
@retry_with_backoff(
    max_retries=3,        # Number of retries
    base_delay=1.0,       # Initial delay (seconds)
    max_delay=30.0,       # Maximum delay cap
    jitter=True,          # Add randomness
    retryable_exceptions=(Timeout, ConnectionError)
)
```

### Agent Configuration

```python
agent = Agent(
    max_retries=3,        # Default retries for all operations
    retry_delay=1.0       # Base delay between retries
)
```

---

## 📝 Examples

### Example 1: Direct Tool Execution

```python
from cli_agent.tools.registry import ToolRegistry
from cli_agent.tools import file_tools  # Import to register

# Execute tool directly
result = ToolRegistry.execute_tool(
    "read_file",
    path="README.md",
    max_lines=10
)

print(result["content"])
```

### Example 2: Via Agent (LLM)

```python
from cli_agent.agent.core import Agent

agent = Agent()

# Natural language request
result = agent.process_request(
    "Read the first 10 lines of README.md"
)

print(result["response"])
```

### Example 3: Via CLI

```bash
# Command line
agent read README.md

# With options
agent find "TODO" in ./src --directory ./cli_agent
```

### Example 4: Get All MCP Definitions

```python
from cli_agent.tools.registry import ToolRegistry
from cli_agent.tools import file_tools, api_tools, log_tools, system_tools
import json

# Get all tool definitions
definitions = ToolRegistry.get_tool_definitions()

# Print as JSON
print(json.dumps(definitions, indent=2))
```

---

## 🎓 Key Concepts

### MCP Compliance

This implementation follows the OpenAI Function Calling specification, which is compatible with:
- OpenAI API (GPT-3.5, GPT-4)
- Azure OpenAI
- Other LLM providers that support function calling

### Tool Discovery

Tools are automatically discovered and registered via the `@register_tool` decorator. No manual registration needed.

### Intent Classification

The agent uses pattern matching to classify user intent before deciding whether to:
1. Call a tool directly (high confidence)
2. Ask LLM to choose (medium confidence)
3. Respond directly (low confidence / conversation)

### Error Handling

All tools include:
- Parameter validation
- Try-catch error handling
- Custom exception types
- Automatic retry for transient failures
- Detailed error messages

---

## 📊 Tool Summary

| Category | Tools | Total |
|----------|-------|-------|
| File Operations | `read_file`, `search_files`, `summarize_file` | 3 |
| API Operations | `fetch_api_data`, `check_health`, `test_endpoint` | 3 |
| Log Analysis | `get_logs`, `analyze_logs`, `detect_cors_issue` | 3 |
| System Operations | `execute_command`, `validate_env`, `check_env_var`, `system_info` | 4 |
| **Total** | | **13** |

---

## 🔗 Related Documentation

- [README.md](README.md) - Main project documentation
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete testing guide
- [EXAMPLE_COMMANDS.md](EXAMPLE_COMMANDS.md) - CLI command examples
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

---

## 📞 Support

For questions or issues:
1. Check the [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. Review tool definitions in `cli_agent/tools/`
3. Examine intent patterns in `cli_agent/agent/intent.py`
4. Check logs in `logs/agent.log`

---

**Last Updated**: 2026-04-07  
**Version**: 1.0.0  
**Total MCP Tools**: 13
