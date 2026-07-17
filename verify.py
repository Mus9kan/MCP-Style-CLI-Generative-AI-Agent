"""Quick verification script for CLI AI Agent."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("CLI AI Agent - Verification Script")
print("=" * 60)

# Test 1: Import all modules
print("\n1. Testing imports...")
try:
    from cli_agent.agent.core import Agent
    from cli_agent.agent.intent import IntentClassifier
    from cli_agent.tools.registry import ToolRegistry
    from cli_agent.debugger.analyzer import DebugAnalyzer
    # Import all tool modules to register them
    from cli_agent.tools import file_tools, api_tools, log_tools, system_tools
    print("   ✓ All modules imported successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: List tools
print("\n2. Listing available tools...")
tools = ToolRegistry.list_tools()
print(f"   ✓ Found {len(tools)} tools:")
for tool in sorted(tools):
    print(f"      - {tool}")

# Test 3: Test intent classification
print("\n3. Testing intent classification...")
test_cases = [
    ("read file app.py", "read_file"),
    ("check health http://localhost:5000", "check_health"),
    ("debug CORS issue", "detect_cors_issue"),
    ("analyze logs test.log", "analyze_logs"),
]

for query, expected_tool in test_cases:
    result = IntentClassifier.classify(query)
    actual_tool = result.get("tool", "none")
    status = "✓" if actual_tool == expected_tool else "✗"
    print(f"   {status} '{query}' → {actual_tool}")

# Test 4: Initialize agent
print("\n4. Testing agent initialization...")
try:
    agent = Agent()
    print("   ✓ Agent initialized")
    print(f"   ✓ Available tools: {len(agent.get_available_tools())}")
except Exception as e:
    print(f"   ✗ Agent initialization failed: {e}")

# Test 5: Debug analyzer
print("\n5. Testing debug analyzer...")
try:
    analyzer = DebugAnalyzer()
    sample_log = """
    INFO: Starting server
    ERROR: CORS policy blocked request
    WARNING: Access-Control-Allow-Origin header missing
    """
    result = analyzer.analyze_logs(sample_log)
    print(f"   ✓ Analyzed sample log")
    print(f"   ✓ Detected {result['total_issues']} issue(s)")
except Exception as e:
    print(f"   ✗ Debug analyzer failed: {e}")

print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Run 'agent setup' to configure your OpenAI API key")
print("2. Try commands like:")
print("   - agent read README.md")
print("   - agent find 'TODO' in .")
print("   - agent health-check http://localhost:5000")
print("   - agent debug cors issue")
print()
