# 🧪 Complete Testing Guide - CLI AI Agent

This guide shows you how to test all 7 core features of the CLI AI Agent.

---

## 📋 Testing Overview

| # | Feature | Test Method | Time |
|---|---------|-------------|------|
| 1 | Tool Registry (MCP) | Unit tests + CLI commands | 5 min |
| 2 | Context Memory | Interactive test | 3 min |
| 3 | Agent Decision Loop | Unit tests + integration | 5 min |
| 4 | Error Handling & Retries | Unit tests + simulation | 10 min |
| 5 | Secure Authentication | Config tests | 3 min |
| 6 | CLI Command System | Manual testing | 15 min |
| 7 | Logging & Debugging | Log inspection | 5 min |

**Total Time: ~46 minutes**

---

## 🚀 Prerequisites

### 1. Install Dependencies
```bash
cd c:\Users\Lenovo\Desktop\cli_agents
pip install -r requirements.txt
```

### 2. Run Existing Test Suite
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_retry.py -v

# Run with coverage
python -m pytest tests/ --cov=cli_agent --cov-report=html
```

---

## 1️⃣ Test Tool Registry (MCP Compliant)

### Automated Tests
```bash
# Run tool registry tests
python -m pytest tests/test_tools.py::TestToolRegistry -v
```

### Manual Testing

#### List All Available Tools
```bash
# Windows PowerShell
python -m cli_agent.main tools

# If you have the alias set up
agent tools
```

**Expected Output:**
```
Available Tools - MCP-Style Tool Registry
Total Tools: 13

read_file
  Read contents of a file
  Parameters: path, line_limit

search_files
  Search for keywords in files
  Parameters: keyword, directory
  
[... more tools ...]
```

#### Test Individual Tools
```bash
# Test file reading tool
python -m cli_agent.main read README.md

# Test search tool
python -m cli_agent.main find "TODO" in .

# Test environment validation
python -m cli_agent.main validate-env
```

#### Verify MCP Compliance
```python
# Create test_mcp.py
from cli_agent.tools.registry import ToolRegistry
from cli_agent.tools import file_tools, api_tools, log_tools, system_tools

# Get all tool definitions (MCP format)
tools = ToolRegistry.get_tool_definitions()

print(f"Total tools registered: {len(tools)}")
for tool in tools:
    print(f"\nTool: {tool['name']}")
    print(f"Description: {tool['description']}")
    print(f"Parameters: {tool['parameters']}")
```

Run it:
```bash
python test_mcp.py
```

**✅ Success Criteria:**
- ✅ 13 tools registered
- ✅ Each tool has name, description, parameters
- ✅ Tools follow JSON Schema format
- ✅ Singleton pattern working

---

## 2️⃣ Test Context Memory

### Automated Test
```bash
python -m pytest tests/test_agent.py::TestAgent::test_clear_history -v
```

### Manual Interactive Test

Create a test script `test_memory.py`:
```python
from cli_agent.agent.core import Agent

# Initialize agent
agent = Agent()

# Simulate conversation
print("=== Testing Context Memory ===\n")

# Add messages to history
agent.conversation_history.append({"role": "user", "content": "Hello"})
agent.conversation_history.append({"role": "assistant", "content": "Hi there!"})
agent.conversation_history.append({"role": "user", "content": "How are you?"})

print(f"Messages in history: {len(agent.conversation_history)}")
for i, msg in enumerate(agent.conversation_history):
    print(f"{i+1}. [{msg['role']}] {msg['content']}")

# Test history clearing
print("\n--- Clearing history ---")
agent.clear_history()
print(f"Messages after clear: {len(agent.conversation_history)}")
```

Run it:
```bash
python test_memory.py
```

**✅ Success Criteria:**
- ✅ History accumulates messages
- ✅ Message roles preserved (user/assistant/tool)
- ✅ `clear_history()` empties the list
- ✅ History persists across multiple requests

---

## 3️⃣ Test Agent Decision Loop

### Automated Tests
```bash
# Test intent classification
python -m pytest tests/test_agent.py::TestIntentClassifier -v

# Test agent initialization
python -m pytest tests/test_agent.py::TestAgent::test_agent_initialization -v
```

### Manual Testing

#### Test Rule-Based Intent (No LLM)
```python
from cli_agent.agent.core import Agent

agent = Agent()

# Test without LLM
result = agent.process_request("read file README.md", use_llm=False)
print(f"Intent: {result}")
```

#### Test LLM-Based Decision (Requires API Key)
```bash
# Make sure API key is configured
python -m cli_agent.main setup

# Test natural language processing
python -m cli_agent.main debug cors issue
```

#### Test Decision Flow
```python
from cli_agent.agent.intent import IntentClassifier

# Test different intents
queries = [
    "read the file app.py",
    "check health of http://localhost:5000",
    "analyze logs server.log",
    "detect CORS issues",
    "find TODO in code"
]

for query in queries:
    intent = IntentClassifier.classify(query)
    print(f"Query: {query}")
    print(f"Intent: {intent['intent']}, Tool: {intent.get('tool')}, Confidence: {intent['confidence']:.2f}\n")
```

**✅ Success Criteria:**
- ✅ Correct intent classification
- ✅ High confidence for known patterns
- ✅ Fallback to LLM for ambiguous queries
- ✅ Proper tool selection

---

## 4️⃣ Test Error Handling & Retries ⭐ NEW

### Automated Tests
```bash
# Run all retry tests
python -m pytest tests/test_retry.py -v

# Expected: 9 tests passing
```

### Manual Retry Testing

#### Test 1: Simulate Flaky API
```python
from cli_agent.utils.retry import retry_with_backoff
import time

attempt = 0

@retry_with_backoff(max_retries=3, base_delay=0.5, jitter=False)
def flaky_api_call():
    global attempt
    attempt += 1
    print(f"Attempt {attempt}")
    if attempt < 3:
        raise ConnectionError("Server temporarily unavailable")
    return "Success!"

print("=== Testing Retry with Backoff ===")
result = flaky_api_call()
print(f"Result: {result}")
print(f"Total attempts: {attempt}")
```

Run it:
```bash
python test_retry_manual.py
```

**Expected Output:**
```
=== Testing Retry with Backoff ===
Attempt 1
Attempt 2
[WARNING] Attempt 1/3 failed... Retrying in 0.50s...
[WARNING] Attempt 2/3 failed... Retrying in 1.00s...
Attempt 3
Result: Success!
Total attempts: 3
```

#### Test 2: Exhaust All Retries
```python
from cli_agent.utils.retry import RetryContext
from cli_agent.utils.exceptions import RetryError

def always_fails():
    raise ValueError("Permanent failure")

print("=== Testing Retry Exhaustion ===")
try:
    with RetryContext(max_retries=2, base_delay=0.1, operation_name="test_op") as ctx:
        ctx.execute(always_fails)
except RetryError as e:
    print(f"RetryError caught: {e}")
    print(f"Max retries: {e.max_retries}")
    print(f"Last error: {e.last_error}")
```

#### Test 3: Tool Execution with Retries
```bash
# Test with non-existent file (will retry then fail gracefully)
python -m cli_agent.main read nonexistent_file.txt
```

**Check logs for retry attempts:**
```bash
# View log file
cat logs/agent.log

# Or in PowerShell
Get-Content logs/agent.log -Tail 50
```

**Expected Log Entries:**
```
WARNING: Attempt 1/3 failed for 'read_file': File not found...
WARNING: Retrying in 0.97s...
WARNING: Attempt 2/3 failed for 'read_file': File not found...
WARNING: Retrying in 1.93s...
ERROR: 'read_file' failed after 3 retries
```

**✅ Success Criteria:**
- ✅ Retries with exponential backoff (1s → 2s → 4s)
- ✅ Jitter prevents thundering herd
- ✅ RetryError raised after exhaustion
- ✅ Clear logging of each attempt
- ✅ Works for API calls, tools, and LLM requests

---

## 5️⃣ Test Secure Authentication

### Automated Test
```bash
python -m pytest tests/test_tools.py::TestSystemTools::test_validate_env -v
```

### Manual Testing

#### Test 1: Check Current Configuration
```bash
# Check if API key is set
python -m cli_agent.main validate-env
```

#### Test 2: Setup Wizard
```bash
# Interactive setup
python -m cli_agent.main setup
```

**Follow prompts:**
```
CLI AI Agent Setup - Configuration Wizard
Please enter your OpenAI API key:
API Key: sk-test123...
✓ API key saved successfully!
Using model: gpt-4o-mini
```

#### Test 3: Verify .env File
```bash
# Check .env file exists and has key
cat .env

# PowerShell
Get-Content .env
```

**Expected:**
```
OPENAI_API_KEY=your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

#### Test 4: Validation Error Handling
```python
from cli_agent.utils.config import get_config

# Temporarily remove API key
import os
os.environ['OPENAI_API_KEY'] = ''

config = get_config()
try:
    config.validate()
except Exception as e:
    print(f"Validation error (expected): {e}")
```

**✅ Success Criteria:**
- ✅ API key stored in .env (not hardcoded)
- ✅ Validation before API calls
- ✅ Clear error messages when missing
- ✅ Interactive setup wizard works

---

## 6️⃣ Test CLI Command System

### Test All Commands

#### Basic Commands
```bash
# Version info
python -m cli_agent.main version

# List tools
python -m cli_agent.main tools

# Help
python -m cli_agent.main --help
python -m cli_agent.main debug --help
```

#### File Operations
```bash
# Read file
python -m cli_agent.main read README.md

# Search files
python -m cli_agent.main find "TODO" in .

# With specific directory
python -m cli_agent.main find "import" in ./cli_agent
```

#### API Testing
```bash
# Health check (test with public API)
python -m cli_agent.main health-check https://httpbin.org/status/200

# Fetch API data
python -m cli_agent.main fetch-api https://jsonplaceholder.typicode.com/posts/1

# Test endpoint
python -m cli_agent.main test-api /posts/1 --base-url https://jsonplaceholder.typicode.com
```

#### Log Analysis
```bash
# Create sample log file
echo "2024-01-01 ERROR: Connection failed" > test.log
echo "2024-01-01 WARNING: Slow query" >> test.log
echo "2024-01-01 INFO: Request processed" >> test.log

# Analyze logs
python -m cli_agent.main analyze logs test.log

# Debug issues
python -m cli_agent.main debug --file test.log
```

#### System Operations
```bash
# Validate environment
python -m cli_agent.main validate-env

# Execute safe command
python -m cli_agent.main exec python --version

# System info (natural language)
python -m cli_agent.main what system am I on
```

#### Debug Commands
```bash
# CORS debugging
python -m cli_agent.main debug cors issue

# API failure debugging
python -m cli_agent.main debug api failure

# With specific log file
python -m cli_agent.main debug --file logs/agent.log --issue-type cors
```

**✅ Success Criteria:**
- ✅ All 12 subcommands work
- ✅ Help text displays properly
- ✅ Arguments parsed correctly
- ✅ Error messages for invalid commands

---

## 7️⃣ Test Logging & Debugging

### Check Logging System

#### View Log File
```bash
# View full log
cat logs/agent.log

# PowerShell
Get-Content logs\agent.log

# Follow log in real-time
Get-Content logs\agent.log -Wait -Tail 20
```

#### Enable Debug Mode
Edit `.env`:
```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

Run a command:
```bash
python -m cli_agent.main read README.md
```

Check detailed logs:
```bash
Get-Content logs\agent.log -Tail 100
```

**Expected Debug Output:**
```
2024-01-01 10:00:00 - cli_agent - DEBUG - Agent initialized with max_retries=3, retry_delay=1.0s
2024-01-01 10:00:01 - cli_agent - DEBUG - Classified intent: tool_call
2024-01-01 10:00:01 - cli_agent - DEBUG - Direct tool call: read_file with params: {'path': 'README.md'}
2024-01-01 10:00:01 - cli_agent - DEBUG - Executing tool: read_file
2024-01-01 10:00:01 - cli_agent - DEBUG - Tool result: {'success': True, ...}
```

### Test Debug Analyzer

```python
from cli_agent.debugger.analyzer import DebugAnalyzer

# Sample log with issues
log_content = """
2024-01-01 ERROR: Access-Control-Allow-Origin header missing
2024-01-01 ERROR: CORS policy blocked request
2024-01-01 WARNING: API endpoint returned 500
2024-01-01 ERROR: Connection refused to database
"""

analyzer = DebugAnalyzer()
result = analyzer.analyze_logs(log_content)

print(f"Total issues: {result['total_issues']}")
for issue in result['issues']:
    print(f"\nType: {issue['type']}")
    print(f"Severity: {issue['severity']}/10")
    print(f"Root Cause: {issue['root_cause']}")
    print(f"Fix: {issue['suggested_fix']}")
```

### Test Rich Console Logging
```bash
# Should see colored, formatted output
python -m cli_agent.main debug cors issue
```

**✅ Success Criteria:**
- ✅ Log file created in `logs/` directory
- ✅ Both console and file logging work
- ✅ Debug mode shows detailed traces
- ✅ DebugAnalyzer detects issues correctly
- ✅ Rich formatting in console

---

## 🎯 Integration Test: Full Workflow

Test all features together:

```bash
# 1. Verify setup
python -m cli_agent.main version
python -m cli_agent.main tools

# 2. Check environment
python -m cli_agent.main validate-env

# 3. Read a file (tests: CLI + Tool Registry + Error Handling)
python -m cli_agent.main read README.md

# 4. Analyze logs (tests: Logging + Debug + Decision Loop)
python -m cli_agent.main analyze logs logs/agent.log

# 5. Test external API (tests: Retries + API Tools)
python -m cli_agent.main health-check https://httpbin.org/status/200

# 6. Debug issues (tests: All features combined)
python -m cli_agent.main debug cors issue
```

---

## 📊 Test Results Summary

Create `test_report.py`:
```python
import subprocess
import sys

def run_test(test_name, command):
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"{'='*60}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ PASSED")
        return True
    else:
        print(f"❌ FAILED")
        print(result.stdout)
        print(result.stderr)
        return False

# Run all tests
tests = [
    ("Tool Registry", "python -m pytest tests/test_tools.py::TestToolRegistry -v"),
    ("Intent Classification", "python -m pytest tests/test_agent.py::TestIntentClassifier -v"),
    ("Agent Core", "python -m pytest tests/test_agent.py::TestAgent -v"),
    ("Retry Mechanism", "python -m pytest tests/test_retry.py -v"),
    ("File Tools", "python -m pytest tests/test_tools.py::TestReadFileTool -v"),
]

results = []
for name, cmd in tests:
    results.append(run_test(name, cmd))

# Summary
print(f"\n{'='*60}")
print(f"TEST SUMMARY")
print(f"{'='*60}")
passed = sum(results)
total = len(results)
print(f"Passed: {passed}/{total}")
print(f"Success Rate: {(passed/total)*100:.1f}%")

if passed == total:
    print("\n🎉 All tests passed!")
    sys.exit(0)
else:
    print(f"\n⚠️  {total - passed} test(s) failed")
    sys.exit(1)
```

Run it:
```bash
python test_report.py
```

---

## 🔍 Troubleshooting

### Tests Failing?

**Issue**: Module not found
```bash
# Reinstall in development mode
pip install -e .
```

**Issue**: Import errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Run from project root
cd c:\Users\Lenovo\Desktop\cli_agents
```

**Issue**: API key errors
```bash
# Verify .env file
cat .env

# Re-run setup
python -m cli_agent.main setup
```

### Retries Not Working?

```bash
# Check logs for retry attempts
Get-Content logs\agent.log | Select-String "Retry"

# Enable debug mode
# Add to .env: DEBUG_MODE=true, LOG_LEVEL=DEBUG
```

---

## ✅ Final Checklist

- [ ] All unit tests pass (`python -m pytest tests/ -v`)
- [ ] Tool registry shows 13+ tools
- [ ] Context memory accumulates messages
- [ ] Intent classification works correctly
- [ ] Retry mechanism logs attempts with backoff
- [ ] API key validation works
- [ ] All CLI commands execute successfully
- [ ] Log file created and populated
- [ ] Debug analyzer detects issues
- [ ] Integration test workflow completes

---

## 🎓 Next Steps

After testing:

1. **Customize Tools**: Add your own tools in `cli_agent/tools/`
2. **Adjust Retry Settings**: Modify `max_retries` in Agent initialization
3. **Extend Debug Patterns**: Add patterns to `DebugAnalyzer.ISSUE_PATTERNS`
4. **Monitor Logs**: Regularly check `logs/agent.log` for insights

---

**Happy Testing! 🚀**

For questions, check:
- [README.md](README.md)
- [EXAMPLE_COMMANDS.md](EXAMPLE_COMMANDS.md)
- [QUICKSTART.md](QUICKSTART.md)
