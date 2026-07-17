# Complete Code Documentation for Beginners

This documentation explains every code file line-by-line for absolute beginners who have never programmed before.

## Table of Contents

1. [Project Structure Overview](#project-structure-overview)
2. [Configuration Files](#configuration-files)
3. [Main Entry Point](#main-entry-point)
4. [Agent Core](#agent-core)
5. [Tools System](#tools-system)
6. [Utilities](#utilities)
7. [Debugger](#debugger)
8. [Tests](#tests)

---

## Project Structure Overview

```
cli_agents/
├── cli_agent/              # Main package folder (all the code)
│   ├── __init__.py        # Makes this folder a Python package
│   ├── main.py            # Starting point (what runs when you type 'agent')
│   ├── agent/             # AI Agent logic
│   ├── tools/             # Tools the agent can use
│   ├── utils/             # Helper functions
│   └── debugger/          # Debug analysis tools
├── tests/                 # Test files to verify everything works
├── .env                   # Your private API keys (never share this!)
├── requirements.txt       # List of libraries needed
└── README.md             # Project description
```

### What is a Python Package?

A **Python package** is just a folder that contains Python files. The `__init__.py` file tells Python "this folder is a package" so you can import code from it.

---

## Configuration Files

### 1. requirements.txt

**Purpose**: Lists all the external libraries your project needs to work.

```
# Core dependencies
openai>=1.0.0           # OpenAI's library for talking to GPT models
requests>=2.31.0        # For making HTTP requests (calling APIs)
python-dotenv>=1.0.0    # Reads .env files for API keys
rich>=13.7.0            # Makes beautiful colored terminal output

# Development dependencies (only needed for testing)
pytest>=7.4.0           # Testing framework
pytest-cov>=4.1.0       # Measures how much code is tested
black>=23.12.0          # Automatically formats code nicely
flake8>=7.0.0           # Checks for mistakes in code
```

**Line-by-line explanation**:
- Lines starting with `#` are **comments** - Python ignores them (for humans)
- Each line has a package name followed by `>=` and a version number
- `>=1.0.0` means "version 1.0.0 or newer"

---

### 2. .env.example

**Purpose**: Template showing what environment variables you need (never commit actual `.env` with real keys!)

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-...      # Your secret OpenAI key (starts with 'sk-')
OPENAI_MODEL=gpt-4o-mini       # Which AI model to use

# Application Settings
LOG_LEVEL=INFO                 # How detailed logs should be (DEBUG, INFO, WARNING, ERROR)
DEBUG_MODE=false               # Turn on/off debug mode

# Optional: Custom API endpoints
DEFAULT_TIMEOUT=30             # Wait max 30 seconds for API calls
```

**What are Environment Variables?**
They're like global settings for your program, stored outside the code. This keeps secrets (like API keys) separate from code you share on GitHub.

---

### 3. pyproject.toml

**Purpose**: Configuration file for testing and code coverage tools.

```toml
[tool.pytest.ini_options]     # Settings for pytest (testing tool)
minversion = "7.0"            # Need pytest version 7.0 or higher
addopts = "-ra -q --strict-markers"  # Extra command options
testpaths = ["tests"]         # Look for tests in 'tests' folder
python_files = ["test_*.py"]  # Test files start with 'test_'
python_classes = ["Test*"]    # Test classes start with 'Test'
python_functions = ["test_*"] # Test functions start with 'test_'

# Logging
log_cli = true                # Show logs in terminal
log_cli_level = "INFO"        # Log level for terminal

# Coverage
[tool.coverage.run]           # Code coverage settings
source = ["cli_agent"]        # Measure coverage for cli_agent folder

[tool.coverage.report]        # Report settings
exclude_lines = [             # Don't count these lines in coverage
    "pragma: no cover",       # Special comment to skip line
    "def __repr__",           # String representation methods
    "raise AssertionError",   # Error handling
    "raise NotImplementedError", # Placeholder methods
]
```

---

## Main Entry Point

### 4. cli_agent/main.py

**Purpose**: This is what runs when you type `agent` in your terminal. It reads your command and calls the right function.

#### Imports Section (Lines 1-23)

```python
"""Main entry point for CLI AI Agent."""
# Docstring - describes what this file does

import argparse      # Built-in Python library for parsing command-line arguments
import sys          # System-specific parameters (like exiting the program)
from typing import Optional  # For type hints (tells you what type of data to expect)

# Import tools to register them (MUST be before other imports that use tools)
from .tools import file_tools, api_tools, log_tools, system_tools
# ^ This imports all tool files so they get registered in the tool system
# The dot '.' means "from the current package"

from .utils.config import get_config, ConfigError
# ^ Imports configuration management and a custom error type

from .utils.formatter import (
    print_header,
    print_section,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_result,
)
# ^ Imports pretty printing functions for colorful terminal output

from .agent.core import Agent           # The main AI agent
from .debugger.analyzer import DebugAnalyzer  # Debug analysis tool
from .tools.registry import ToolRegistry      # Tool registration system
```

#### Setup Wizard Function (Lines 24-48)

```python
def setup_wizard():
    """Interactive setup wizard for API key configuration."""
    # ^ Function definition with docstring explaining its purpose
    
    print_header("CLI AI Agent Setup", "Configuration Wizard")
    # ^ Prints a fancy header with title and subtitle
    
    config = get_config()
    # ^ Gets the configuration object that manages .env file
    
    if config.is_configured():
        # ^ Checks if API key already exists
        print_success("OpenAI API key is already configured!")
        response = input("\nDo you want to update it? (y/n): ")
        # ^ Asks user for input (waits for keyboard response)
        if response.lower() != "y":
            # ^ Converts to lowercase and checks if NOT 'y'
            return
            # ^ Exits the function early if user doesn't want to update
    
    print("\nPlease enter your OpenAI API key:")
    print("You can get one from: https://platform.openai.com/api-keys\n")
    
    api_key = input("API Key: ").strip()
    # ^ Gets user input and removes extra spaces from start/end
    
    if not api_key:
        # ^ Checks if api_key is empty
        print_error("No API key provided. Setup cancelled.")
        return
    
    config.setup_api_key(api_key)
    # ^ Saves the API key to .env file
    print_success("API key saved successfully!")
    print_info(f"Using model: {config.model}")
    # ^ f-string - embeds variable inside string with {}
```

#### Debug Command Handler (Lines 50-105)

```python
def cmd_debug(args):
    """Handle debug command."""
    # ^ args contains parsed command-line arguments
    agent = Agent()
    # ^ Creates a new Agent instance
    analyzer = DebugAnalyzer()
    # ^ Creates a DebugAnalyzer for analyzing issues
    
    query = " ".join(args.query) if args.query else ""
    # ^ Joins list of words into single string, or empty string if no query
    
    if args.issue_type:
        # ^ Checks if specific issue type was provided (--issue-type flag)
        query = f"{args.issue_type} issue {query}"
        # ^ Adds issue type to query (e.g., "cors issue")
    
    # Special handling for CORS
    if "cors" in query.lower():
        # ^ Checks if 'cors' appears anywhere in query (case-insensitive)
        print_section("Debugging CORS Issue")
        
        if args.file:
            # ^ If --file flag was provided
            result = agent.process_request(f"detect CORS issues in {args.file}")
        else:
            result = agent.process_request("detect CORS issues in logs")
        
        if result["success"]:
            # ^ Checks if operation succeeded
            print_result(result["response"], title="CORS Analysis")
        else:
            print_error(result.get("response", "Debug failed"))
    
    elif args.file:
        # ^ Else if file was provided (but not CORS)
        print_section(f"Analyzing Log File: {args.file}")
        
        try:
            from pathlib import Path
            # ^ Import inside function (lazy import)
            with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
                # ^ Opens file safely, ignoring encoding errors
                content = f.read()
                # ^ Reads entire file content
            
            analysis = analyzer.analyze_logs(content)
            # ^ Analyzes log content
            
            if analysis["total_issues"] > 0:
                # ^ If issues found
                print_info(f"Found {analysis['total_issues']} issue(s)")
                
                for i, report in enumerate(analyzer.get_all_reports()):
                    # ^ Loops through all reports with index
                    analyzer.print_report(i)
            else:
                print_success("No common issues detected in logs")
        
        except Exception as e:
            # ^ Catches any errors
            print_error(str(e))
            # ^ Converts error to string and displays it
    
    else:
        # ^ General debug query (no special case)
        print_section("Debug Query")
        result = agent.process_request(f"debug {query}")
        
        if result["success"]:
            print_result(result["response"])
        else:
            print_error(result.get("response", "Debug failed"))
```

#### Analyze Command Handler (Lines 107-118)

```python
def cmd_analyze(args):
    """Handle analyze command."""
    print_section(f"Analyzing Log File: {args.file}")
    
    agent = Agent()
    result = agent.process_request(f"analyze logs {args.file}")
    # ^ Tells agent to analyze the specified log file
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Analysis failed"))
```

#### Health Check Command (Lines 120-131)

```python
def cmd_health_check(args):
    """Handle health-check command."""
    print_section(f"Health Check: {args.url}")
    
    agent = Agent()
    result = agent.process_request(f"check health of {args.url}")
    # ^ Asks agent to check if URL is working
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Health check failed"))
```

#### Read Command (Lines 133-144)

```python
def cmd_read(args):
    """Handle read command."""
    print_section(f"Reading File: {args.file}")
    
    agent = Agent()
    result = agent.process_request(f"read file {args.file}")
    # ^ Agent uses read_file tool
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Failed to read file"))
```

#### Find Command (Lines 146-159)

```python
def cmd_find(args):
    """Handle find command."""
    print_section(f"Searching for: {args.keyword}")
    
    directory = args.directory if args.directory else "."
    # ^ Uses provided directory or current directory (".")
    
    agent = Agent()
    result = agent.process_request(f"find '{args.keyword}' in {directory}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Search failed"))
```

#### Fetch API Command (Lines 161-172)

```python
def cmd_fetch_api(args):
    """Handle fetch-api command."""
    print_section(f"Fetching API: {args.url}")
    
    agent = Agent()
    result = agent.process_request(f"fetch data from {args.url}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "API fetch failed"))
```

#### Test API Command (Lines 174-189)

```python
def cmd_test_api(args):
    """Handle test-api command."""
    print_section(f"Testing API Endpoint: {args.endpoint}")
    
    base_url = args.base_url if args.base_url else "http://localhost:5000"
    # ^ Uses provided base URL or default localhost
    
    agent = Agent()
    result = agent.process_request(
        f"test endpoint {args.endpoint} at {base_url}"
    )
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "API test failed"))
```

#### Validate Environment Command (Lines 191-202)

```python
def cmd_validate_env(args):
    """Handle validate-env command."""
    print_section("Environment Validation")
    
    agent = Agent()
    result = agent.process_request("validate environment variables")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Validation failed"))
```

#### Execute Command (Lines 204-218)

```python
def cmd_exec(args):
    """Handle exec command."""
    command = " ".join(args.cmd)
    # ^ Joins all command parts into single string
    
    print_section(f"Executing Command: {command}")
    print_warning("Use with caution - system commands can be dangerous")
    # ^ Warns user that commands can be risky
    
    agent = Agent()
    result = agent.process_request(f"execute command: {command}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Command execution failed"))
```

#### Tools List Command (Lines 220-234)

```python
def cmd_tools(args):
    """List available tools."""
    print_header("Available Tools", "MCP-Style Tool Registry")
    
    tools = ToolRegistry.get_all_tools()
    # ^ Gets all registered tools from registry
    
    print_section(f"Total Tools: {len(tools)}")
    # ^ len() returns count of items
    
    for tool in tools:
        # ^ Loops through each tool
        print(f"\n[bold cyan]{tool.name}[/bold cyan]")
        # ^ Rich markup for colored text
        print(f"  {tool.description}")
        if tool.parameters.get("properties"):
            # ^ Checks if tool has parameters
            params = list(tool.parameters["properties"].keys())
            # ^ Extracts parameter names
            print(f"  Parameters: {', '.join(params)}")
```

#### Version Command (Lines 236-242)

```python
def cmd_version(args):
    """Show version info."""
    from cli_agent import __version__
    # ^ Imports version number from package
    
    print_header("CLI AI Agent", f"Version {__version__}")
    print_info("Production-ready CLI agent with MCP-style tool calling")
```

#### Main Function (Lines 244-356)

This is the **most important function** - it sets up all the commands!

```python
def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="agent",
        # ^ Program name shown in help
        description="CLI AI Agent - Intelligent assistant with tool calling capabilities",
        # ^ Description shown in help
        epilog="Examples:\n"
        "  agent debug cors issue\n"
        "  agent analyze logs app.log\n"
        "  agent health-check http://localhost:5000\n"
        "  agent read app.py\n"
        "  agent find 'TODO' in ./src\n"
        "  agent fetch-api http://localhost:5000/data\n"
        "  agent test-api /users --base-url http://localhost:5000\n"
        "  agent validate-env\n",
        # ^ Examples shown at bottom of help
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # ^ Keeps formatting of epilog text
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    # ^ Creates subcommands (debug, analyze, read, etc.)
    
    # Setup command
    subparsers.add_parser("setup", help="Configure API key and settings")
    # ^ Simple command with no extra arguments
    
    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Debug an issue")
    debug_parser.add_argument("query", nargs="*", help="Debug query")
    # ^ nargs="*" means zero or more arguments
    debug_parser.add_argument("--issue-type", "-t", help="Issue type (e.g., cors, api)")
    # ^ Optional argument with short form -t
    debug_parser.add_argument("--file", "-f", help="Log file to analyze")
    debug_parser.set_defaults(func=cmd_debug)
    # ^ Sets which function handles this command
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze logs")
    analyze_parser.add_argument("file", help="Log file to analyze")
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Health-check command
    health_parser = subparsers.add_parser("health-check", help="Check service health")
    health_parser.add_argument("url", help="URL to check")
    health_parser.set_defaults(func=cmd_health_check)
    
    # Read command
    read_parser = subparsers.add_parser("read", help="Read a file")
    read_parser.add_argument("file", help="File to read")
    read_parser.set_defaults(func=cmd_read)
    
    # Find command
    find_parser = subparsers.add_parser("find", help="Find keyword in files")
    find_parser.add_argument("keyword", help="Keyword to search for")
    find_parser.add_argument("--directory", "-d", default=".", help="Directory to search")
    # ^ default="." means current directory if not specified
    find_parser.set_defaults(func=cmd_find)
    
    # Fetch-api command
    fetch_parser = subparsers.add_parser("fetch-api", help="Fetch data from API")
    fetch_parser.add_argument("url", help="API URL")
    fetch_parser.set_defaults(func=cmd_fetch_api)
    
    # Test-api command
    test_parser = subparsers.add_parser("test-api", help="Test API endpoint")
    test_parser.add_argument("endpoint", help="Endpoint path (e.g., /users)")
    test_parser.add_argument("--base-url", "-b", default="http://localhost:5000", help="Base URL")
    test_parser.set_defaults(func=cmd_test_api)
    
    # Validate-env command
    env_parser = subparsers.add_parser("validate-env", help="Validate environment variables")
    env_parser.set_defaults(func=cmd_validate_env)
    
    # Exec command
    exec_parser = subparsers.add_parser("exec", help="Execute system command")
    exec_parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to execute")
    # ^ REMAINDER captures all remaining arguments (even with spaces)
    exec_parser.set_defaults(func=cmd_exec)
    
    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available tools")
    tools_parser.set_defaults(func=lambda args: print("\n".join(ToolRegistry.list_tools())))
    # ^ Lambda = anonymous function (one-liner)
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=cmd_version)
    
    args = parser.parse_args()
    # ^ Parses actual command-line arguments typed by user
    
    # Handle commands
    if args.command == "setup":
        setup_wizard()
    elif hasattr(args, "func"):
        # ^ Checks if 'func' attribute exists on args
        try:
            # Validate config for commands that need it
            config = get_config()
            if args.command not in ["version", "tools", "setup"]:
                try:
                    config.validate()
                    # ^ Checks if API key is configured
                except ConfigError as e:
                    # ^ Catches configuration error
                    print_error(str(e))
                    print_info("Run 'agent setup' to configure your API key")
                    sys.exit(1)
                    # ^ Exits program with error code 1
            
            args.func(args)
            # ^ Calls the function associated with the command
            # Example: if 'debug' command, calls cmd_debug(args)
        except KeyboardInterrupt:
            # ^ User pressed Ctrl+C
            print("\n")
            print_warning("Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            # ^ Any other error
            print_error(f"Error: {str(e)}")
            if config.debug_mode:
                import traceback
                traceback.print_exc()
                # ^ Prints full error stack trace in debug mode
            sys.exit(1)
    else:
        parser.print_help()
        # ^ Shows help if no command given


if __name__ == "__main__":
    # ^ This check ensures code only runs when file is executed directly
    # Not when imported as a module
    main()
```

---

## Continue Reading

This is Part 1 covering configuration files and the main entry point. Continue with:

- **Part 2**: [Agent Core](docs/PART2_AGENT_CORE.md) - The AI brain
- **Part 3**: [Tools System](docs/PART3_TOOLS_SYSTEM.md) - File operations, API calls, log analysis
- **Part 4**: [Utilities](docs/PART4_UTILITIES.md) - Configuration, logging, formatting
- **Part 5**: [Debugger](docs/PART5_DEBUGGER.md) - Debug analysis
- **Part 6**: [Tests](docs/PART6_TESTS.md) - Testing everything
