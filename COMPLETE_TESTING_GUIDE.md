# 🧪 Complete CLI Testing Guide

This guide shows you how to test **EVERY feature** of your CLI Agent step-by-step.

---

## 📋 Quick Test Commands

Copy and paste these commands one by one to test all features:

```bash
# Set alias for convenience (optional)
alias agent="python -m cli_agent.main"

# Or use full command each time
python -m cli_agent.main [command]
```

---

## ✅ TEST 1: Basic Commands

### 1.1 Help Command
```bash
python -m cli_agent.main --help
```
**Expected:** Shows all available commands and options

### 1.2 Version Command
```bash
python -m cli_agent.main version
```
**Expected:** Shows "CLI AI Agent - Version 1.0.0"

### 1.3 Setup Command
```bash
python -m cli_agent.main setup
```
**Expected:** Interactive prompt to configure API key

---

## ✅ TEST 2: Chat & Streaming

### 2.1 Basic Chat
```bash
python -m cli_agent.main chat "What is artificial intelligence in 2 sentences?"
```
**Expected:** AI response in a green panel

### 2.2 Streaming Chat ⭐
```bash
python -m cli_agent.main chat --stream "Explain quantum computing in simple terms"
```
**Expected:** Text appears in real-time with typing effect and blinking cursor

### 2.3 Chat with Tool Use
```bash
python -m cli_agent.main chat "Read the file README.md"
```
**Expected:** Agent reads and summarizes the file

---

## ✅ TEST 3: Session Management

### 3.1 Create Session
```bash
python -m cli_agent.main session new --topic "Project Planning"
```
**Expected:** Shows new session ID (e.g., "4672234e")

### 3.2 List Sessions
```bash
python -m cli_agent.main session list
```
**Expected:** Shows all sessions with IDs, topics, message counts, and timestamps

### 3.3 Search Sessions
```bash
python -m cli_agent.main session search "artificial intelligence"
```
**Expected:** Shows matching messages from conversation history

### 3.4 Load Session
```bash
# Replace with your actual session ID from step 3.1
python -m cli_agent.main session load --session-id 4672234e
```
**Expected:** Shows session details and message count

### 3.5 Delete Session
```bash
python -m cli_agent.main session delete --session-id 4672234e
```
**Expected:** Confirms session deletion

---

## ✅ TEST 4: Plugin System

### 4.1 List Plugins
```bash
python -m cli_agent.main plugin list
```
**Expected:** Shows installed plugins (should show weather_tool if installed)

### 4.2 Install Plugin
```bash
# Plugin should be in ~/.cli_agent/plugins/ directory
python -m cli_agent.main plugin install weather_tool
```
**Expected:** Confirms plugin installation

### 4.3 Use Plugin Tool
```bash
# If you have OPENWEATHER_API_KEY set
python -m cli_agent.main chat "What's the weather in London?"
```
**Expected:** Agent uses weather_tool to get real weather data

### 4.4 Uninstall Plugin
```bash
python -m cli_agent.main plugin uninstall weather_tool
```
**Expected:** Confirms plugin removal

---

## ✅ TEST 5: Cache Management

### 5.1 View Cache Stats
```bash
python -m cli_agent.main cache stats
```
**Expected:** Shows cache entries, size, TTL, and location

### 5.2 Test Caching
```bash
# First request (will call LLM - takes 2-3 seconds)
python -m cli_agent.main chat "What is 2+2? Answer in one word."

# Second request (should be instant from cache)
python -m cli_agent.main chat "What is 2+2? Answer in one word."
```
**Expected:** Second request is much faster, logs show "Returning cached LLM response"

### 5.3 Clear Cache
```bash
# Clear all cache
python -m cli_agent.main cache clear

# Clear only entries older than 12 hours
python -m cli_agent.main cache clear --older-than 12
```
**Expected:** Shows number of entries cleared

### 5.4 Cache Cleanup
```bash
python -m cli_agent.main cache cleanup
```
**Expected:** Removes expired entries, shows count

---

## ✅ TEST 6: Security Layer

### 6.1 Test via Python Console
```bash
python
```

Then run:
```python
from cli_agent.agent.core import Agent

# Create agent
agent = Agent()

# Test 1: Check security levels
report = agent.permission_mgr.get_security_report()
print("Security Report:")
print(f"  Total tools: {report['total_tools']}")
print(f"  Security levels: {report['security_levels']}")

# Test 2: Permission for safe tool
perm = agent.permission_mgr.check_permission("read_file", {"path": "test.txt"})
print(f"\nread_file permission: {perm['allowed']} (Level: {perm['security_level'].value})")

# Test 3: Permission for dangerous tool
perm = agent.permission_mgr.check_permission("execute_command", {"command": "ls"})
print(f"execute_command permission: {perm['allowed']} (Level: {perm['security_level'].value})")
print(f"Requires confirmation: {agent.permission_mgr.requires_confirmation('execute_command')}")

# Test 4: Dangerous pattern blocking
perm = agent.permission_mgr.check_permission("execute_command", {"command": "rm -rf /"})
print(f"\nDangerous pattern blocked: {not perm['allowed']}")
print(f"Reason: {perm['reason']}")

# Test 5: Directory traversal blocking
perm = agent.permission_mgr.check_permission("read_file", {"path": "../../../etc/passwd"})
print(f"\nDirectory traversal blocked: {not perm['allowed']}")
print(f"Reason: {perm['reason']}")

exit()
```

**Expected:** All security checks should work correctly

---

## ✅ TEST 7: Persistent Memory

### 7.1 Test via Python Console
```bash
python
```

Then run:
```python
from cli_agent.memory import MemoryDB, SessionManager

# Initialize
db = MemoryDB()
sm = SessionManager(db)

print(f"Database location: {db.db_path}")

# Create session
session_id = sm.create_session("Memory Test")
print(f"Created session: {session_id}")

# Save messages
sm.save_message("user", "Hello, I'm testing memory")
sm.save_message("assistant", "Hi! Memory system is working")
print("Saved 2 messages")

# Retrieve history
history = sm.get_history()
print(f"Retrieved {len(history)} messages")

# Search
results = sm.search("testing")
print(f"Search found {len(results)} results")

# List all sessions
sessions = sm.list_sessions()
print(f"Total sessions: {len(sessions)}")

exit()
```

**Expected:** All operations complete successfully

### 7.2 Verify Database File
```bash
# Check if database exists
ls $env:USERPROFILE\.cli_agent\memory.db

# Check file size
(Get-Item $env:USERPROFILE\.cli_agent\memory.db).Length
```

**Expected:** File exists with size > 0

---

## ✅ TEST 8: MCP Tool Registry

### 8.1 Test via Python Console
```bash
python
```

Then run:
```python
from cli_agent.tools.registry import ToolRegistry

# List all registered tools
tools = ToolRegistry.list_tools()
print(f"Registered tools: {len(tools)}")
for tool in tools:
    print(f"  - {tool}")

# Get MCP definitions
definitions = ToolRegistry.get_tool_definitions()
print(f"\nMCP definitions: {len(definitions)}")

# Check format (OpenAI Function Calling)
sample = definitions[0]
print(f"Sample definition keys: {sample.keys()}")
print(f"Has 'type' and 'function': {'type' in sample and 'function' in sample}")

# Test tool execution
result = ToolRegistry.execute_tool("read_file", path="README.md")
print(f"\nTool execution success: {result['success']}")
print(f"Content preview: {result.get('content', '')[:100]}...")

exit()
```

**Expected:** All tools registered and executable

---

## ✅ TEST 9: Intent Classification

### 9.1 Test via Python Console
```bash
python
```

Then run:
```python
from cli_agent.agent.intent import IntentClassifier

test_queries = [
    "read the file config.py",
    "check health of localhost:5000",
    "analyze logs app.log",
    "fetch data from http://api.example.com",
    "search for TODO in ./src",
    "test endpoint /api/users"
]

for query in test_queries:
    result = IntentClassifier.classify(query)
    print(f"Query: {query}")
    print(f"  Intent: {result['intent']}")
    print(f"  Confidence: {result['confidence']:.2f}")
    if result.get('tool'):
        print(f"  Tool: {result['tool']}")
    print()

exit()
```

**Expected:** All queries classified with confidence > 0

---

## ✅ TEST 10: Retry Mechanism

### 10.1 Test via Python Console
```bash
python
```

Then run:
```python
from cli_agent.utils.retry import retry_with_backoff
import time

# Test retry with eventual success
attempt = 0

@retry_with_backoff(max_retries=3, base_delay=0.1)
def flaky_function():
    global attempt
    attempt += 1
    if attempt < 3:
        raise ValueError(f"Attempt {attempt} failed")
    return f"Success on attempt {attempt}!"

print("Testing retry mechanism...")
start = time.time()
result = flaky_function()
elapsed = time.time() - start

print(f"Result: {result}")
print(f"Time taken: {elapsed:.2f}s")
print(f"Total attempts: {attempt}")

exit()
```

**Expected:** Function retries and succeeds on 3rd attempt with exponential backoff

---

## ✅ TEST 11: Specific Tool Commands

### 11.1 Read File
```bash
python -m cli_agent.main read README.md
```

### 11.2 Health Check
```bash
python -m cli_agent.main health-check https://httpbin.org
```

### 11.3 API Fetch
```bash
python -m cli_agent.main fetch-api https://httpbin.org/get
```

### 11.4 Environment Validation
```bash
python -m cli_agent.main validate-env
```

### 11.5 Search Files
```bash
python -m cli_agent.main find "import" in .
```

---

## 📊 Test Results Checklist

Print this and check off each test:

```
BASIC COMMANDS
☐ 1.1 Help command
☐ 1.2 Version command  
☐ 1.3 Setup command

CHAT & STREAMING
☐ 2.1 Basic chat
☐ 2.2 Streaming chat
☐ 2.3 Chat with tool use

SESSION MANAGEMENT
☐ 3.1 Create session
☐ 3.2 List sessions
☐ 3.3 Search sessions
☐ 3.4 Load session
☐ 3.5 Delete session

PLUGIN SYSTEM
☐ 4.1 List plugins
☐ 4.2 Install plugin
☐ 4.3 Use plugin tool
☐ 4.4 Uninstall plugin

CACHE MANAGEMENT
☐ 5.1 View cache stats
☐ 5.2 Test caching (fast second request)
☐ 5.3 Clear cache
☐ 5.4 Cache cleanup

SECURITY LAYER
☐ 6.1 Security checks (Python console)

PERSISTENT MEMORY
☐ 7.1 Memory operations (Python console)
☐ 7.2 Database file exists

MCP TOOL REGISTRY
☐ 8.1 Tools registered and executable

INTENT CLASSIFICATION
☐ 9.1 Intent classification working

RETRY MECHANISM
☐ 10.1 Retry with backoff working

SPECIFIC TOOLS
☐ 11.1 Read file
☐ 11.2 Health check
☐ 11.3 API fetch
☐ 11.4 Environment validation
☐ 11.5 Search files
```

---

## 🎯 Quick Smoke Test (5 minutes)

If you want to quickly verify everything works, run these 5 commands:

```bash
# 1. Basic chat
python -m cli_agent.main chat "Hello, world!"

# 2. Streaming
python -m cli_agent.main chat --stream "Tell me a joke"

# 3. Sessions
python -m cli_agent.main session list

# 4. Cache
python -m cli_agent.main cache stats

# 5. Plugins
python -m cli_agent.main plugin list
```

If all 5 work, your CLI Agent is fully functional! ✅

---

## 🐛 Troubleshooting

### Issue: "agent command not found"
**Solution:** Use `python -m cli_agent.main` instead of `agent`

### Issue: "Module not found"
**Solution:** Make sure you're in the project root directory:
```bash
cd c:\Users\Lenovo\Desktop\cli_agents
```

### Issue: Streaming not working
**Solution:** Make sure you have OPENAI_API_KEY set:
```bash
$env:OPENAI_API_KEY="sk-..."
```

### Issue: Plugin not loading
**Solution:** Check plugin directory:
```bash
ls $env:USERPROFILE\.cli_agent\plugins\
```

### Issue: Database errors
**Solution:** Delete and recreate:
```bash
rm $env:USERPROFILE\.cli_agent\memory.db
# It will be recreated on next use
```

---

## 🎉 All Tests Passing?

If everything works, congratulations! Your CLI Agent has:

✅ Real-time streaming output  
✅ Extensible plugin architecture  
✅ Persistent conversation memory  
✅ Enterprise-grade security  
✅ Response caching for performance  
✅ MCP-compliant tool registry  
✅ Intent classification  
✅ Automatic retry mechanisms  

**You have a production-ready CLI AI Agent!** 🚀
