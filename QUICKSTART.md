# 🚀 Quick Start Guide - CLI AI Agent

Get up and running in 5 minutes!

---

## ⚡ Installation (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key
```bash
python -m cli_agent.main setup
```
Enter your OpenAI API key when prompted.

**Alternative**: Create `.env` file manually:
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Step 3: Verify Installation
```bash
python verify.py
```

You should see:
```
✓ All modules imported successfully
✓ Found 13 tools
✓ Agent initialized
```

---

## 🎯 Your First Commands

### Try These (No API Key Required)
```bash
# List all available tools
python -m cli_agent.main tools

# Check version
python -m cli_agent.main version

# Read a file
python -m cli_agent.main read README.md

# Find text in files
python -m cli_agent.main find "TODO" in .

# Validate environment
python -m cli_agent.main validate-env
```

### With API Key Configured
```bash
# Natural language queries
python -m cli_agent.main debug cors issue

# Analyze logs
python -m cli_agent.main analyze logs app.log

# Check service health
python -m cli_agent.main health-check http://localhost:5000

# Test API endpoints
python -m cli_agent.main test-api /users --base-url http://localhost:5000
```

---

## 📖 Common Use Cases

### 🔍 Debug CORS Issue
```bash
# See what's wrong with CORS
agent debug cors issue

# Output shows:
# Problem: CORS detected
# Root Cause: Missing Access-Control-Allow-Origin header
# Suggested Fix: Add CORS middleware to server
```

### 📊 Analyze Logs
```bash
# Find errors in logs
agent analyze logs server.log

# Output shows:
# Total Lines: 1000
# Errors: 15
# Warnings: 42
# Sample errors listed
```

### 🏥 Check Service Health
```bash
# Is my server running?
agent health-check http://localhost:5000

# Output shows:
# Status: HEALTHY
# HTTP Code: 200
# Response Time: 45ms
```

### 📁 Work with Files
```bash
# Read file contents
agent read app.py

# Search for keyword
agent find "import os" in ./src

# Get file summary
agent info package.json
```

---

## 🛠️ Tool Reference

All 13 available tools:

| Tool | Command Example | Description |
|------|----------------|-------------|
| `read_file` | `agent read file.py` | Read file contents |
| `search_files` | `agent find "TODO"` | Search for keywords |
| `summarize_file` | `agent info file.txt` | Get file metadata |
| `fetch_api_data` | `agent fetch http://...` | GET request to API |
| `check_health` | `agent health http://...` | Check service status |
| `test_endpoint` | `agent test /api/users` | Test API endpoint |
| `get_logs` | `agent get logs app.log` | Retrieve log entries |
| `analyze_logs` | `agent analyze logs app.log` | Analyze log patterns |
| `detect_cors_issue` | `agent debug cors` | Detect CORS errors |
| `execute_command` | `agent exec ls -la` | Run system command |
| `validate_env` | `agent validate-env` | Check env variables |
| `check_env_var` | `agent check PATH` | Check specific variable |
| `system_info` | `agent system info` | Get system details |

---

## 💡 Pro Tips

### Natural Language Works Best
Don't memorize exact syntax! Just ask naturally:
```bash
agent can you read the main.py file?
agent check if localhost:5000 is up
agent find TODO comments in my code
```

### Combine Commands
```bash
# Chain multiple operations
agent read app.py && agent find "def " in app.py

# Use in scripts
for log in *.log; do
    agent analyze logs $log
done
```

### Debug Like a Pro
```bash
# 1. Check health first
agent health-check http://localhost:5000

# 2. If failing, analyze logs
agent analyze logs server.log

# 3. Debug specific issues
agent debug the error in server.log
```

---

## ❓ Troubleshooting

### "OpenAI API key not found"
**Solution**: Run `agent setup` or add to `.env`:
```bash
OPENAI_API_KEY=your-key-here
```

### "Module not found"
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --upgrade
```

### "Tool execution failed"
**Check**:
- File paths are correct
- URLs are accessible
- Parameters are provided

### No output from tools
**Try**: Enable debug mode in `.env`:
```bash
DEBUG_MODE=true
```

---

## 📚 Next Steps

Once you're comfortable with basics:

1. **Read Full Documentation**
   - See [README.md](README.md) for complete guide
   - Check [EXAMPLE_COMMANDS.md](EXAMPLE_COMMANDS.md) for all commands

2. **Explore Advanced Features**
   - Multi-step debugging workflows
   - Custom tool creation
   - Conversation mode (with LLM)

3. **Customize for Your Needs**
   - Add your own tools
   - Modify existing tools
   - Integrate with your workflow

---

## 🎓 Learning Resources

### Understanding the Architecture
- Tools follow MCP (Model Context Protocol) pattern
- Intent classifier uses pattern matching + LLM
- Rich library handles terminal formatting

### Code Structure
- `cli_agent/tools/` - All tool implementations
- `cli_agent/agent/` - LLM interaction logic
- `cli_agent/utils/` - Helper functions
- `tests/` - Test suite

---

## ✅ Verification Checklist

Before you start, ensure:

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API key configured (`.env` file or `agent setup`)
- [ ] Verification passed (`python verify.py`)

---

## 🆘 Getting Help

```bash
# Show all commands
agent --help

# Help for specific command
agent debug --help

# List available tools
agent tools

# Check version
agent version
```

---

## 🎉 You're Ready!

Start exploring:
```bash
# Read this project's README
agent read README.md

# Check your system
agent system info

# Validate your environment
agent validate-env

# Debug something!
agent debug cors issue
```

---

**Happy coding! 🚀**

For detailed documentation, see:
- [README.md](README.md) - Complete user guide
- [EXAMPLE_COMMANDS.md](EXAMPLE_COMMANDS.md) - All commands
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture overview
