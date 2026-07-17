# CLI AI Agent 🚀

**Production-ready CLI AI agent with MCP-style tool calling capabilities**

A powerful command-line assistant that uses OpenAI's LLM for intent understanding and executes tools dynamically based on user commands. Features modular architecture inspired by Model Context Protocol (MCP).

## ✨ Features

- **🧠 Intelligent Intent Recognition**: Uses LLM or rule-based classification to understand commands
- **🔧 MCP-Style Tool Architecture**: Modular tools that can be easily extended

- **📁 File Operations**: Read, search, and summarize files
- **🌐 API Testing**: Fetch data, check health, test endpoints
- **📊 Log Analysis**: Analyze logs, detect CORS issues, find errors
- **💻 System Commands**: Execute shell commands safely
- **🔍 Debug Assistant**: Detect common backend issues with structured reports
- **🎨 Professional UI**: Rich-formatted terminal output with colors and spinners
- **📝 Comprehensive Logging**: Structured logging with file and console output
- **⚙️ Configuration Management**: .env support with interactive setup

## 🚀 Quick Startf
### Prerequisites

- Python 3.8+
- OpenAI API Key

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your API key**:
```bash
agent setup
```

Or manually create a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

4. **Test installation**:
```bash
agent version
agent tools
```

## 📖 Usage Examples

### Debugging

```bash
# Debug CORS issues
agent debug cors issue

# Analyze log files
agent analyze logs app.log

# Debug specific issue types
agent debug api failure
agent debug authentication
```

### File Operations

```bash
# Read a file
agent read app.py

# Search for keyword in project
agent find "TODO" in ./src

# Get file summary
agent info package.json
```

### API Testing

```bash
# Check service health
agent health-check http://localhost:5000

# Fetch API data
agent fetch-api http://localhost:5000/users

# Test endpoint
agent test-api /users --base-url http://localhost:5000
```

### System Operations

```bash
# Validate environment variables
agent validate-env

# Execute system command (safely)
agent exec ls -la

# Get system info
agent system info
```

## 🛠️ Available Tools

The agent includes these built-in tools:

| Tool | Description | Example |
|------|-------------|---------|
| `read_file` | Read file contents | "read app.py" |
| `search_files` | Search for keywords | "find 'TODO' in src" |
| `summarize_file` | Get file summary | "info config.json" |
| `fetch_api_data` | Fetch from API | "fetch http://api.com/data" |
| `check_health` | Check service status | "health http://localhost:5000" |
| `test_endpoint` | Test API endpoint | "test /users at http://..." |
| `get_logs` | Retrieve logs | "get logs app.log" |
| `analyze_logs` | Analyze log patterns | "analyze logs app.log" |
| `detect_cors_issue` | Find CORS errors | "debug cors" |
| `execute_command` | Run shell commands | "exec git status" |
| `validate_env` | Check env variables | "validate-env" |
| `check_env_var` | Check specific variable | "check PATH" |
| `system_info` | Get system details | "system info" |

## 🏗️ Architecture

### MCP-Style Tool Calling Flow

```
User Input → Intent Classifier → Tool Selection → Tool Execution → LLM Response → Formatted Output
```

### Project Structure

```
cli_agents/
├── cli_agent/
│   ├── main.py              # CLI entry point
│   ├── agent/
│   │   ├── core.py          # Main agent logic
│   │   └── intent.py        # Intent classification
│   ├── tools/
│   │   ├── base.py          # Base tool class
│   │   ├── registry.py      # Tool registry
│   │   ├── file_tools.py    # File operations
│   │   ├── api_tools.py     # API operations
│   │   ├── log_tools.py     # Log analysis
│   │   └── system_tools.py  # System operations
│   ├── utils/
│   │   ├── config.py        # Configuration
│   │   ├── logger.py        # Logging
│   │   ├── formatter.py     # Rich formatting
│   │   └── exceptions.py    # Custom exceptions
│   └── debugger/
│       └── analyzer.py      # Debug analysis
├── tests/
├── requirements.txt
├── setup.py
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Application Settings
LOG_LEVEL=INFO
DEBUG_MODE=false

# Optional
DEFAULT_TIMEOUT=30
```

### Custom Tools

Add new tools by extending `BaseTool`:

```python
from cli_agent.tools.base import BaseTool
from cli_agent.tools.registry import register_tool

@register_tool
class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    parameters = {
        "type": "object",
        "properties": {
            "param1": {"type": "string"}
        },
        "required": ["param1"]
    }
    
    def execute(self, param1: str):
        return {"result": "success"}
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=cli_agent --cov-report=html
```

## 📝 Command Reference

### Setup Commands
```bash
agent setup                 # Interactive configuration
agent version              # Show version info
agent tools                # List available tools
```

### Debug Commands
```bash
agent debug <query>                    # General debug query
agent debug cors --file app.log       # Debug CORS issues
agent debug api failure               # Debug API problems
```

### Analysis Commands
```bash
agent analyze logs <file.log>         # Analyze log file
```

### Health Check Commands
```bash
agent health-check <url>              # Check service health
```

### File Commands
```bash
agent read <file>                     # Read file contents
agent find "<keyword>" [-d dir]      # Search files
```

### API Commands
```bash
agent fetch-api <url>                 # Fetch API data
agent test-api <endpoint> [-b base]  # Test endpoint
```

### System Commands
```bash
agent validate-env                    # Check environment
agent exec <command>                  # Execute command
```

## 🎯 Key Design Principles

1. **Modularity**: Each tool is independent and replaceable
2. **Extensibility**: Easy to add new tools without modifying core logic
3. **Safety**: Dangerous commands are blocked, timeouts enforced
4. **Transparency**: All tool executions are logged and displayed
5. **Professional UX**: Rich formatting makes output readable and beautiful

## 🔒 Security Notes

- System commands are filtered for dangerous operations
- API keys are stored securely in `.env` file
- Timeouts prevent hanging operations
- Input validation on all tool parameters

## 🐛 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
```bash
# Run setup wizard
agent setup

# Or manually add to .env file
OPENAI_API_KEY=your_key_here
```

**"Tool execution failed"**
- Check that required parameters are provided
- Verify file paths are correct
- Ensure URLs are accessible

**"Module import errors"**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📚 Additional Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Rich Library Documentation](https://rich.readthedocs.io/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Follow PEP8 style guidelines
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author

Created as a production-ready example of MCP-style CLI agent architecture.

---

**Made with ❤️ using advanced CLI agent patterns**

For questions or support, please open an issue on GitHub.
