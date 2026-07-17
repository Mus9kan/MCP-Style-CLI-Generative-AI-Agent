# CLI AI Agent - Example Commands

This file demonstrates all the commands you can run with the CLI AI Agent.

## 🚀 Setup

```bash
# Configure your OpenAI API key (interactive)
agent setup

# Or manually edit .env file
# Add: OPENAI_API_KEY=your_key_here

# Verify installation
agent version
agent tools
```

---

## 🐛 Debugging Commands

### Debug CORS Issues
```bash
# Detect CORS issues in logs
agent debug cors issue

# Analyze specific log file for CORS
agent debug cors --file logs/app.log

# General CORS debugging
agent detect CORS errors in backend logs
```

### Debug API Failures
```bash
# Debug API failure patterns
agent debug api failure

# Debug authentication issues
agent debug authentication problem

# Debug database connection issues
agent debug database error
```

### Analyze Logs
```bash
# Analyze log file
agent analyze logs app.log

# Check for errors and warnings
agent analyze logs server.log

# Get log summary
agent get logs application.log
```

---

## 📁 File Operations

### Read Files
```bash
# Read a Python file
agent read app.py

# Read configuration file
agent read config.json

# Read any text file
agent read README.md

# Read with line limit
agent read large_file.txt
```

### Search Files
```bash
# Find keyword in current directory
agent find "TODO" in .

# Search in specific directory
agent find "FIXME" in ./src

# Look for specific pattern
agent find "import os" in ./cli_agent
```

### File Information
```bash
# Get file summary
agent info package.json

# Check file details
agent summarize app.py
```

---

## 🌐 API Testing

### Health Checks
```bash
# Check if service is running
agent health-check http://localhost:5000

# Monitor API status
agent check health of https://api.example.com

# Quick ping test
agent status http://localhost:8080
```

### Fetch API Data
```bash
# GET request to endpoint
agent fetch-api http://localhost:5000/users

# Retrieve data from API
agent get data from https://jsonplaceholder.typicode.com/posts/1
```

### Test Endpoints
```bash
# Test specific endpoint
agent test-api /users --base-url http://localhost:5000

# Test POST endpoint
agent test /api/login at http://localhost:5000

# Full endpoint testing
agent test endpoint /health on http://localhost:5000
```

---

## 💻 System Operations

### Environment Validation
```bash
# Check all environment variables
agent validate-env

# Check specific variable
agent check PATH

# Verify API key is set
agent check OPENAI_API_KEY
```

### Execute Commands
```bash
# Run system commands
agent exec ls -la

# Git operations
agent exec git status

# Python commands
agent exec python --version

# Directory listing
agent exec dir
```

### System Information
```bash
# Get system details
agent system info

# Check OS and Python version
agent what system am I on
```

---

## 🔍 Advanced Usage

### Multi-Step Debugging
```bash
# 1. Analyze logs
agent analyze logs app.log

# 2. Debug detected issues
agent debug the problems in app.log

# 3. Get structured report
# (Output shows Problem, Root Cause, Suggested Fix)
```

### API Workflow
```bash
# 1. Check health
agent health-check http://localhost:5000

# 2. Test endpoints
agent test-api /users

# 3. Fetch data
agent fetch-api http://localhost:5000/data
```

### Code Analysis
```bash
# 1. Read file
agent read main.py

# 2. Search for patterns
agent find "def " in ./src

# 3. Get file info
agent summarize main.py
```

---

## 🎯 Real-World Scenarios

### Scenario 1: Backend Not Responding
```bash
# Check if service is up
agent health-check http://localhost:5000

# If down, check logs
agent analyze logs server.log

# Look for specific errors
agent find "ERROR" in ./logs
```

### Scenario 2: CORS Errors in Browser
```bash
# Detect CORS issues
agent debug cors issue

# Analyze frontend logs
agent analyze logs browser_console.log

# Get fix suggestions
# (Agent provides structured report with solutions)
```

### Scenario 3: API Integration Testing
```bash
# Test all endpoints
agent test-api /users --base-url http://localhost:5000
agent test-api /posts --base-url http://localhost:5000
agent test-api /comments --base-url http://localhost:5000

# Check response times
agent health-check http://localhost:5000
```

### Scenario 4: Deployment Verification
```bash
# Validate environment
agent validate-env

# Check service health
agent health-check http://production-server.com

# Verify logs
agent get logs deployment.log
```

---

## 📝 Command Patterns

### Natural Language Queries
The agent understands natural language, so you can say:

```bash
# Instead of exact syntax, just ask naturally:
agent what's in the app.py file?
agent can you check if localhost:5000 is running?
agent find all TODO comments in my code
agent why is my CORS failing?
agent show me the logs from today
```

### Combining Commands
```bash
# Chain multiple commands
agent read app.py && agent find "import" in app.py

# Use in scripts
for file in *.py; do
    agent summarize $file
done
```

---

## ⚡ Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| `debug` | Debug an issue | `agent debug cors` |
| `analyze` | Analyze logs | `agent analyze logs app.log` |
| `health-check` | Check service | `agent health http://...` |
| `read` | Read file | `agent read file.py` |
| `find` | Search files | `agent find "TODO"` |
| `fetch-api` | GET request | `agent fetch http://...` |
| `test-api` | Test endpoint | `agent test /users` |
| `validate-env` | Check env vars | `agent validate-env` |
| `exec` | Run command | `agent exec ls -la` |
| `tools` | List tools | `agent tools` |
| `version` | Show version | `agent version` |
| `setup` | Configure API | `agent setup` |

---

## 💡 Pro Tips

1. **Natural Language**: Don't memorize exact syntax - just ask naturally!
2. **Context Aware**: The agent understands context like "this file", "that URL", etc.
3. **Structured Output**: Debug reports always show Problem → Root Cause → Fix
4. **Safe Execution**: Dangerous commands are blocked automatically
5. **Rich Formatting**: Enjoy colored, formatted output in terminal

---

## 🆘 Getting Help

```bash
# Show help for any command
agent --help
agent debug --help
agent analyze --help

# List all available tools
agent tools

# Check version
agent version
```

---

**Happy debugging! 🚀**

For more information, see README.md
