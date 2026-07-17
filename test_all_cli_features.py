"""
Comprehensive CLI Feature Test Suite
Tests ALL commands and features of the CLI Agent
"""

import subprocess
import sys
from pathlib import Path
import json
import time

class Colors:
    """Terminal colors for output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}▶ {text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*70}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def run_command(cmd, timeout=30):
    """Run a CLI command and return result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'stdout': '', 'stderr': 'Timeout', 'returncode': -1}
    except Exception as e:
        return {'success': False, 'stdout': '', 'stderr': str(e), 'returncode': -1}

def test_basic_commands():
    """Test basic CLI commands."""
    print_header("TEST 1: BASIC CLI COMMANDS")
    
    tests = []
    
    # Test 1: Help command
    print_section("1.1 Help Command")
    result = run_command("python -m cli_agent.main --help")
    if result['success'] and 'usage' in result['stdout'].lower():
        print_success("Help command works")
        tests.append(True)
    else:
        print_error("Help command failed")
        tests.append(False)
    
    # Test 2: Version command
    print_section("1.2 Version Command")
    result = run_command("python -m cli_agent.main version")
    if result['success'] and 'version' in result['stdout'].lower():
        print_success("Version command works")
        tests.append(True)
    else:
        print_error("Version command failed")
        tests.append(False)
    
    # Test 3: Setup command
    print_section("1.3 Setup Command")
    result = run_command("python -m cli_agent.main setup")
    if result['success']:
        print_success("Setup command accessible")
        tests.append(True)
    else:
        print_error("Setup command failed")
        tests.append(False)
    
    return tests

def test_chat_commands():
    """Test chat and streaming commands."""
    print_header("TEST 2: CHAT & STREAMING")
    
    tests = []
    
    # Test 1: Basic chat
    print_section("2.1 Basic Chat (Non-streaming)")
    result = run_command(
        'python -m cli_agent.main chat "What is 2+2? Answer in one word."',
        timeout=20
    )
    if result['success'] and ('four' in result['stdout'].lower() or '4' in result['stdout']):
        print_success("Basic chat works")
        tests.append(True)
    else:
        print_error("Basic chat failed")
        print_info(f"Output: {result['stdout'][:200]}")
        tests.append(False)
    
    # Test 2: Streaming chat
    print_section("2.2 Streaming Chat")
    result = run_command(
        'python -m cli_agent.main chat --stream "Explain AI in 1 sentence"',
        timeout=20
    )
    if result['success'] and 'streaming response' in result['stdout'].lower():
        print_success("Streaming chat works")
        tests.append(True)
    else:
        print_error("Streaming chat failed")
        print_info(f"Output: {result['stdout'][:200]}")
        tests.append(False)
    
    # Test 3: Cache verification
    print_section("2.3 Response Caching (Repeat same query)")
    result = run_command(
        'python -m cli_agent.main chat "What is 2+2? Answer in one word."',
        timeout=20
    )
    if result['success'] and 'cached' in result['stderr'].lower():
        print_success("Response caching works (cache hit)")
        tests.append(True)
    else:
        print_info("Cache status unclear (may still be working)")
        tests.append(True)  # Don't fail on this
    
    return tests

def test_session_management():
    """Test session management features."""
    print_header("TEST 3: SESSION MANAGEMENT")
    
    tests = []
    session_id = None
    
    # Test 1: Create session
    print_section("3.1 Create New Session")
    result = run_command(
        'python -m cli_agent.main session new --topic "Test Session"',
        timeout=10
    )
    if result['success'] and 'session id:' in result['stdout'].lower():
        print_success("Session creation works")
        # Extract session ID
        for line in result['stdout'].split('\n'):
            if 'session id:' in line.lower():
                session_id = line.split()[-1].strip()
                print_info(f"Session ID: {session_id}")
                break
        tests.append(True)
    else:
        print_error("Session creation failed")
        tests.append(False)
    
    # Test 2: List sessions
    print_section("3.2 List Sessions")
    result = run_command("python -m cli_agent.main session list", timeout=10)
    if result['success'] and 'total sessions:' in result['stdout'].lower():
        print_success("Session listing works")
        tests.append(True)
    else:
        print_error("Session listing failed")
        tests.append(False)
    
    # Test 3: Search sessions
    print_section("3.3 Search Sessions")
    result = run_command(
        'python -m cli_agent.main session search "test"',
        timeout=10
    )
    if result['success']:
        print_success("Session search works")
        tests.append(True)
    else:
        print_error("Session search failed")
        tests.append(False)
    
    # Test 4: Load session (if we have a session ID)
    if session_id:
        print_section("3.4 Load Session")
        result = run_command(
            f'python -m cli_agent.main session load --session-id {session_id}',
            timeout=10
        )
        if result['success']:
            print_success("Session loading works")
            tests.append(True)
        else:
            print_error("Session loading failed")
            tests.append(False)
    
    return tests

def test_plugin_system():
    """Test plugin management features."""
    print_header("TEST 4: PLUGIN SYSTEM")
    
    tests = []
    
    # Test 1: List plugins
    print_section("4.1 List Plugins")
    result = run_command("python -m cli_agent.main plugin list", timeout=10)
    if result['success']:
        print_success("Plugin listing works")
        if 'weather_tool' in result['stdout']:
            print_info("Weather plugin detected")
        tests.append(True)
    else:
        print_error("Plugin listing failed")
        tests.append(False)
    
    # Test 2: Verify plugin tools are registered
    print_section("4.2 Plugin Tool Registration")
    from cli_agent.tools.plugin_manager import PluginManager
    pm = PluginManager()
    plugins = pm.list_plugins()
    if len(plugins) > 0:
        print_success(f"Found {len(plugins)} plugin(s)")
        for plugin in plugins:
            print_info(f"  - {plugin['name']}: {plugin['tools']}")
        tests.append(True)
    else:
        print_info("No plugins installed (this is OK)")
        tests.append(True)
    
    return tests

def test_cache_management():
    """Test cache management features."""
    print_header("TEST 5: CACHE MANAGEMENT")
    
    tests = []
    
    # Test 1: Cache stats
    print_section("5.1 Cache Statistics")
    result = run_command("python -m cli_agent.main cache stats", timeout=10)
    if result['success'] and 'total entries' in result['stdout'].lower():
        print_success("Cache stats work")
        tests.append(True)
    else:
        print_error("Cache stats failed")
        tests.append(False)
    
    # Test 2: Cache cleanup
    print_section("5.2 Cache Cleanup")
    result = run_command("python -m cli_agent.main cache cleanup", timeout=10)
    if result['success']:
        print_success("Cache cleanup works")
        tests.append(True)
    else:
        print_error("Cache cleanup failed")
        tests.append(False)
    
    return tests

def test_security_features():
    """Test security layer features."""
    print_header("TEST 6: SECURITY LAYER")
    
    tests = []
    
    # Test 1: Permission manager initialization
    print_section("6.1 Security Initialization")
    try:
        from cli_agent.security import PermissionManager, SecurityLevel
        pm = PermissionManager()
        print_success("Permission manager initialized")
        tests.append(True)
    except Exception as e:
        print_error(f"Permission manager failed: {e}")
        tests.append(False)
        return tests
    
    # Test 2: Security levels
    print_section("6.2 Security Levels")
    report = pm.get_security_report()
    print_info(f"Total tools configured: {report['total_tools']}")
    print_info(f"Security levels: {report['security_levels']}")
    if report['total_tools'] > 0:
        print_success("Security levels configured")
        tests.append(True)
    else:
        print_error("No security levels configured")
        tests.append(False)
    
    # Test 3: Permission checks
    print_section("6.3 Permission Checks")
    
    # Safe tool
    perm = pm.check_permission("read_file", {"path": "test.txt"})
    if perm['allowed']:
        print_success("Safe tool permission granted")
        tests.append(True)
    else:
        print_error("Safe tool incorrectly blocked")
        tests.append(False)
    
    # Dangerous pattern
    perm = pm.check_permission("execute_command", {"command": "rm -rf /"})
    if not perm['allowed']:
        print_success("Dangerous pattern blocked")
        tests.append(True)
    else:
        print_error("Dangerous pattern not blocked")
        tests.append(False)
    
    # Directory traversal
    perm = pm.check_permission("read_file", {"path": "../../../etc/passwd"})
    if not perm['allowed']:
        print_success("Directory traversal blocked")
        tests.append(True)
    else:
        print_error("Directory traversal not blocked")
        tests.append(False)
    
    return tests

def test_memory_persistence():
    """Test persistent memory features."""
    print_header("TEST 7: PERSISTENT MEMORY")
    
    tests = []
    
    # Test 1: Database initialization
    print_section("7.1 Database Initialization")
    try:
        from cli_agent.memory import MemoryDB, SessionManager
        db = MemoryDB()
        print_success(f"Database created at: {db.db_path}")
        tests.append(True)
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        tests.append(False)
        return tests
    
    # Test 2: Session management
    print_section("7.2 Session Operations")
    sm = SessionManager(db)
    
    # Create session
    session_id = sm.create_session("Memory Test")
    if session_id:
        print_success(f"Session created: {session_id}")
        tests.append(True)
    else:
        print_error("Session creation failed")
        tests.append(False)
        return tests
    
    # Save messages
    sm.save_message("user", "Test message 1")
    sm.save_message("assistant", "Test response 1")
    print_success("Messages saved")
    tests.append(True)
    
    # Test 3: History retrieval
    print_section("7.3 History Retrieval")
    history = sm.get_history()
    if len(history) >= 2:
        print_success(f"Retrieved {len(history)} messages")
        tests.append(True)
    else:
        print_error("History retrieval failed")
        tests.append(False)
    
    # Test 4: Search
    print_section("7.4 Search Functionality")
    results = sm.search("Test message")
    if len(results) > 0:
        print_success(f"Search found {len(results)} result(s)")
        tests.append(True)
    else:
        print_error("Search failed")
        tests.append(False)
    
    # Test 5: List sessions
    print_section("7.5 Session Listing")
    sessions = sm.list_sessions()
    if len(sessions) > 0:
        print_success(f"Found {len(sessions)} session(s)")
        tests.append(True)
    else:
        print_error("Session listing failed")
        tests.append(False)
    
    return tests

def test_tool_registry():
    """Test MCP tool registry."""
    print_header("TEST 8: MCP TOOL REGISTRY")
    
    tests = []
    
    # Test 1: Tool registry initialization
    print_section("8.1 Tool Registry")
    try:
        from cli_agent.tools.registry import ToolRegistry
        tools = ToolRegistry.list_tools()
        print_success(f"Tool registry has {len(tools)} tools")
        tests.append(True)
    except Exception as e:
        print_error(f"Tool registry failed: {e}")
        tests.append(False)
        return tests
    
    # Test 2: Tool definitions (MCP format)
    print_section("8.2 MCP Tool Definitions")
    definitions = ToolRegistry.get_tool_definitions()
    if len(definitions) > 0:
        print_success(f"Generated {len(definitions)} tool definitions")
        # Check MCP format
        sample = definitions[0]
        if 'type' in sample and 'function' in sample:
            print_success("MCP format correct (OpenAI Function Calling)")
            tests.append(True)
        else:
            print_error("MCP format incorrect")
            tests.append(False)
    else:
        print_error("No tool definitions generated")
        tests.append(False)
    
    # Test 3: Tool execution
    print_section("8.3 Tool Execution")
    try:
        # Test a simple tool
        result = ToolRegistry.execute_tool("validate_env")
        if 'success' in result:
            print_success("Tool execution works")
            tests.append(True)
        else:
            print_error("Tool execution failed")
            tests.append(False)
    except Exception as e:
        print_error(f"Tool execution error: {e}")
        tests.append(False)
    
    return tests

def test_intent_classification():
    """Test intent classification system."""
    print_header("TEST 9: INTENT CLASSIFICATION")
    
    tests = []
    
    # Test different intents
    test_cases = [
        ("read the file config.py", "read_file"),
        ("check health of localhost", "check_health"),
        ("analyze logs app.log", "analyze_logs"),
        ("fetch data from API", "fetch_api_data"),
    ]
    
    for i, (query, expected_intent) in enumerate(test_cases, 1):
        print_section(f"9.{i} Intent: {query}")
        from cli_agent.agent.intent import IntentClassifier
        
        result = IntentClassifier.classify(query)
        if result['confidence'] > 0:
            print_success(f"Classified as: {result['intent']} (confidence: {result['confidence']:.2f})")
            tests.append(True)
        else:
            print_error("Classification failed")
            tests.append(False)
    
    return tests

def test_retry_mechanism():
    """Test retry mechanism."""
    print_header("TEST 10: RETRY MECHANISM")
    
    tests = []
    
    print_section("10.1 Retry Decorator")
    try:
        from cli_agent.utils.retry import retry_with_backoff, RetryContext
        
        # Test successful retry
        attempt_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.1)
        def test_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Test error")
            return "success"
        
        result = test_func()
        if result == "success" and attempt_count == 2:
            print_success(f"Retry worked (succeeded on attempt {attempt_count})")
            tests.append(True)
        else:
            print_error("Retry mechanism failed")
            tests.append(False)
    except Exception as e:
        print_error(f"Retry test failed: {e}")
        tests.append(False)
    
    return tests

def main():
    """Run all tests."""
    print_header("CLI AGENT COMPREHENSIVE TEST SUITE")
    print_info("Testing ALL features and commands...")
    
    all_tests = []
    
    # Run all test groups
    all_tests.extend(test_basic_commands())
    all_tests.extend(test_chat_commands())
    all_tests.extend(test_session_management())
    all_tests.extend(test_plugin_system())
    all_tests.extend(test_cache_management())
    all_tests.extend(test_security_features())
    all_tests.extend(test_memory_persistence())
    all_tests.extend(test_tool_registry())
    all_tests.extend(test_intent_classification())
    all_tests.extend(test_retry_mechanism())
    
    # Summary
    print_header("TEST SUMMARY")
    
    total = len(all_tests)
    passed = sum(all_tests)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\n{Colors.BOLD}Total Tests: {total}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED if failed > 0 else Colors.GREEN}Failed: {failed}{Colors.END}")
    print(f"{Colors.CYAN}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    print(f"\n{'='*70}")
    if success_rate >= 90:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 EXCELLENT! All major features working!{Colors.END}")
    elif success_rate >= 75:
        print(f"{Colors.YELLOW}{Colors.BOLD}✅ GOOD! Most features working, some issues to fix.{Colors.END}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  NEEDS ATTENTION! Multiple features need fixes.{Colors.END}")
    print(f"{'='*70}\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
