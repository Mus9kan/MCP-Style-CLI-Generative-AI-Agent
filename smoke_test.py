"""
Quick Smoke Test - Tests all major features in under 2 minutes
"""

import subprocess
import sys
import time

def run_test(name, command, check=None, timeout=15):
    """Run a single test."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        start = time.time()
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        elapsed = time.time() - start
        
        if result.returncode == 0:
            if check is None or check(result.stdout):
                print(f"✅ PASSED ({elapsed:.2f}s)")
                if result.stdout:
                    # Print first 300 chars of output
                    output = result.stdout[:300]
                    print(output)
                    if len(result.stdout) > 300:
                        print("... [truncated]")
                return True
            else:
                print(f"❌ FAILED - Check didn't pass")
                return False
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ FAILED - Timeout ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def main():
    """Run smoke tests."""
    print("\n" + "="*60)
    print("CLI AGENT QUICK SMOKE TEST")
    print("="*60)
    print(f"Started at: {time.strftime('%H:%M:%S')}")
    
    tests = []
    
    # Test 1: Help
    tests.append(run_test(
        "Help Command",
        "python -m cli_agent.main --help",
        check=lambda out: "usage" in out.lower()
    ))
    
    # Test 2: Version
    tests.append(run_test(
        "Version Command",
        "python -m cli_agent.main version",
        check=lambda out: "version" in out.lower()
    ))
    
    # Test 3: Chat
    tests.append(run_test(
        "Basic Chat",
        'python -m cli_agent.main chat "Say hello in 3 words"',
        check=lambda out: len(out) > 0,
        timeout=20
    ))
    
    # Test 4: Streaming
    tests.append(run_test(
        "Streaming Chat",
        'python -m cli_agent.main chat --stream "What is 2+2?"',
        check=lambda out: "streaming response" in out.lower() or "result" in out.lower(),
        timeout=20
    ))
    
    # Test 5: Session List
    tests.append(run_test(
        "Session Listing",
        "python -m cli_agent.main session list",
        check=lambda out: "total sessions" in out.lower() or "sessions" in out.lower()
    ))
    
    # Test 6: Cache Stats
    tests.append(run_test(
        "Cache Statistics",
        "python -m cli_agent.main cache stats",
        check=lambda out: "total entries" in out.lower() or "cache" in out.lower()
    ))
    
    # Test 7: Plugin List
    tests.append(run_test(
        "Plugin Listing",
        "python -m cli_agent.main plugin list",
        check=lambda out: True  # Just needs to run without error
    ))
    
    # Test 8: Python API Test
    print(f"\n{'='*60}")
    print("TEST: Python API (Security, Memory, Tools)")
    print(f"{'='*60}")
    try:
        from cli_agent.agent.core import Agent
        from cli_agent.tools.registry import ToolRegistry
        from cli_agent.memory import MemoryDB
        
        agent = Agent()
        tools = ToolRegistry.list_tools()
        db = MemoryDB()
        
        print(f"✅ PASSED - Agent initialized")
        print(f"   - Tools registered: {len(tools)}")
        print(f"   - Session ID: {agent.session_mgr.get_current_session()}")
        print(f"   - Memory DB: {db.db_path}")
        print(f"   - Security: {agent.permission_mgr.get_security_report()['total_tools']} tools configured")
        tests.append(True)
    except Exception as e:
        print(f"❌ FAILED - {e}")
        tests.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("SMOKE TEST SUMMARY")
    print("="*60)
    
    total = len(tests)
    passed = sum(tests)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {success_rate:.1f}%")
    print(f"\nCompleted at: {time.strftime('%H:%M:%S')}")
    
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Core features working!")
        return 0
    else:
        print(f"\n⚠️  Some features need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
