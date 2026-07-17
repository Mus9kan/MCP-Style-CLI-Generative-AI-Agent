"""Main entry point for CLI AI Agent."""

import argparse
import sys
from typing import Optional

# Import tools to register them (MUST be before other imports that use tools)
from .tools import file_tools, api_tools, log_tools, system_tools

from .utils.config import get_config, ConfigError
from .utils.formatter import (
    print_header,
    print_section,
    print_success,
    print_error,
    print_info,
    print_warning,
    print_result,
)
from .agent.core import Agent
from .debugger.analyzer import DebugAnalyzer
from .tools.registry import ToolRegistry

def setup_wizard():
    """Interactive setup wizard for API key configuration."""
    print_header("CLI AI Agent Setup", "Configuration Wizard")
    
    config = get_config()
    
    if config.is_configured():
        print_success("OpenAI API key is already configured!")
        response = input("\nDo you want to update it? (y/n): ")
        if response.lower() != "y":
            return
    
    print("\nPlease enter your OpenAI API key:")
    print("You can get one from: https://platform.openai.com/api-keys\n")
    
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print_error("No API key provided. Setup cancelled.")
        return
    
    config.setup_api_key(api_key)
    print_success("API key saved successfully!")
    print_info(f"Using model: {config.model}")


def cmd_debug(args):
    """Handle debug command."""
    agent = Agent()
    analyzer = DebugAnalyzer()
    
    query = " ".join(args.query) if args.query else ""
    
    if args.issue_type:
        query = f"{args.issue_type} issue {query}"
    
    # Special handling for CORS
    if "cors" in query.lower():
        print_section("Debugging CORS Issue")
        
        if args.file:
            result = agent.process_request(f"detect CORS issues in {args.file}")
        else:
            result = agent.process_request("detect CORS issues in logs")
        
        if result["success"]:
            print_result(result["response"], title="CORS Analysis")
        else:
            print_error(result.get("response", "Debug failed"))
    
    elif args.file:
        # Analyze log file
        print_section(f"Analyzing Log File: {args.file}")
        
        try:
            from pathlib import Path
            with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            analysis = analyzer.analyze_logs(content)
            
            if analysis["total_issues"] > 0:
                print_info(f"Found {analysis['total_issues']} issue(s)")
                
                for i, report in enumerate(analyzer.get_all_reports()):
                    analyzer.print_report(i)
            else:
                print_success("No common issues detected in logs")
        
        except Exception as e:
            print_error(str(e))
    
    else:
        # General debug query
        print_section("Debug Query")
        result = agent.process_request(f"debug {query}")
        
        if result["success"]:
            print_result(result["response"])
        else:
            print_error(result.get("response", "Debug failed"))


def cmd_analyze(args):
    """Handle analyze command."""
    print_section(f"Analyzing Log File: {args.file}")
    
    agent = Agent()
    result = agent.process_request(f"analyze logs {args.file}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Analysis failed"))


def cmd_health_check(args):
    """Handle health-check command."""
    print_section(f"Health Check: {args.url}")
    
    agent = Agent()
    result = agent.process_request(f"check health of {args.url}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Health check failed"))


def cmd_read(args):
    """Handle read command."""
    print_section(f"Reading File: {args.file}")
    
    agent = Agent()
    result = agent.process_request(f"read file {args.file}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Failed to read file"))


def cmd_find(args):
    """Handle find command."""
    print_section(f"Searching for: {args.keyword}")
    
    directory = args.directory if args.directory else "."
    
    agent = Agent()
    result = agent.process_request(f"find '{args.keyword}' in {directory}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Search failed"))


def cmd_fetch_api(args):
    """Handle fetch-api command."""
    print_section(f"Fetching API: {args.url}")
    
    agent = Agent()
    result = agent.process_request(f"fetch data from {args.url}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "API fetch failed"))


def cmd_test_api(args):
    """Handle test-api command."""
    print_section(f"Testing API Endpoint: {args.endpoint}")
    
    base_url = args.base_url if args.base_url else "http://localhost:5000"
    
    agent = Agent()
    result = agent.process_request(
        f"test endpoint {args.endpoint} at {base_url}"
    )
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "API test failed"))


def cmd_validate_env(args):
    """Handle validate-env command."""
    print_section("Environment Validation")
    
    agent = Agent()
    result = agent.process_request("validate environment variables")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Validation failed"))


def cmd_exec(args):
    """Handle exec command."""
    command = " ".join(args.cmd)
    
    print_section(f"Executing Command: {command}")
    print_warning("Use with caution - system commands can be dangerous")
    
    agent = Agent()
    result = agent.process_request(f"execute command: {command}")
    
    if result["success"]:
        print_result(result["response"])
    else:
        print_error(result.get("response", "Command execution failed"))


def cmd_tools(args):
    """List available tools."""
    print_header("Available Tools", "MCP-Style Tool Registry")
    
    tools = ToolRegistry.get_all_tools()
    
    print_section(f"Total Tools: {len(tools)}")
    
    for tool in tools:
        print(f"\n[bold cyan]{tool.name}[/bold cyan]")
        print(f"  {tool.description}")
        if tool.parameters.get("properties"):
            params = list(tool.parameters["properties"].keys())
            print(f"  Parameters: {', '.join(params)}")


def cmd_version(args):
    """Show version info."""
    from cli_agent import __version__
    
    print_header("CLI AI Agent", f"Version {__version__}")
    print_info("Production-ready CLI agent with MCP-style tool calling")


def cmd_chat(args):
    """Handle chat command with optional streaming."""
    query = " ".join(args.query) if args.query else ""
    
    if not query:
        print_error("Please provide a message to chat about")
        return
    
    agent = Agent()
    
    if args.stream:
        # Streaming mode
        result = agent.process_request(query, use_llm=True, stream=True)
        
        if result["success"]:
            if result.get("streamed"):
                # Stream the response
                from .utils.formatter import print_streaming
                print_streaming(
                    result["response_generator"],
                    title="Streaming Response"
                )
            else:
                # Fell back to non-streaming (tool call)
                print_result(result["response"])
        else:
            print_error(result.get("response", "Chat failed"))
    else:
        # Non-streaming mode
        result = agent.process_request(query, use_llm=True, stream=False)
        
        if result["success"]:
            print_result(result["response"])
        else:
            print_error(result.get("response", "Chat failed"))


def cmd_plugin(args):
    """Handle plugin management commands."""
    from .tools.plugin_manager import PluginManager
    
    plugin_mgr = PluginManager()
    
    if args.plugin_command == "list":
        print_header("Installed Plugins", "Plugin Manager")
        
        plugins = plugin_mgr.list_plugins()
        
        if not plugins:
            print_info("No plugins installed yet")
            print_info(f"Plugin directory: {plugin_mgr.plugin_dir}")
            return
        
        print_section(f"Total Plugins: {len(plugins)}")
        
        for plugin in plugins:
            print(f"\n[bold cyan]{plugin['name']}[/bold cyan]")
            print(f"  File: {plugin['file']}")
            print(f"  Tools: {', '.join(plugin['tools'])}")
            print(f"  Status: {plugin['status']}")
    
    elif args.plugin_command == "install":
        plugin_name = args.name
        print_section(f"Installing Plugin: {plugin_name}")
        
        success = plugin_mgr.install_plugin(plugin_name)
        
        if success:
            print_success(f"Plugin '{plugin_name}' installed successfully")
            print_info(f"Location: {plugin_mgr.plugin_dir / f'{plugin_name}.py'}")
        else:
            print_error(f"Failed to install plugin '{plugin_name}'")
            print_info(f"Make sure the plugin file exists in: {plugin_mgr.plugin_dir}")
    
    elif args.plugin_command == "uninstall":
        plugin_name = args.name
        print_section(f"Uninstalling Plugin: {plugin_name}")
        
        success = plugin_mgr.uninstall_plugin(plugin_name)
        
        if success:
            print_success(f"Plugin '{plugin_name}' uninstalled successfully")
        else:
            print_error(f"Failed to uninstall plugin '{plugin_name}'")
    
    else:
        print_error(f"Unknown plugin command: {args.plugin_command}")
        print_info("Available commands: list, install, uninstall")


def cmd_session(args):
    """Handle session management commands."""
    from .memory import MemoryDB, SessionManager
    
    memory_db = MemoryDB()
    session_mgr = SessionManager(memory_db)
    
    if args.session_command == "new":
        session_id = session_mgr.create_session(args.topic if hasattr(args, 'topic') else None)
        print_section("New Session Created")
        print_success(f"Session ID: {session_id}")
        print_info(f"Use 'agent session load {session_id}' to return to this session")
    
    elif args.session_command == "list":
        print_header("Conversation Sessions", "Session Manager")
        
        sessions = session_mgr.list_sessions(limit=20)
        
        if not sessions:
            print_info("No sessions found")
            return
        
        print_section(f"Total Sessions: {len(sessions)}")
        
        for session in sessions:
            print(f"\n[bold cyan]{session['session_id']}[/bold cyan]")
            if session.get('topic'):
                print(f"  Topic: {session['topic']}")
            print(f"  Messages: {session['message_count']}")
            print(f"  Created: {session['created_at']}")
            print(f"  Updated: {session['updated_at']}")
    
    elif args.session_command == "load":
        session_id = args.session_id
        success = session_mgr.load_session(session_id)
        
        if success:
            stats = memory_db.get_session_stats(session_id)
            print_section("Session Loaded")
            print_success(f"Session ID: {session_id}")
            print_info(f"Messages: {stats['message_count']}")
            print_info(f"Topic: {stats.get('topic', 'N/A')}")
        else:
            print_error(f"Session not found: {session_id}")
    
    elif args.session_command == "delete":
        session_id = args.session_id
        success = session_mgr.delete_session(session_id)
        
        if success:
            print_success(f"Session deleted: {session_id}")
        else:
            print_error(f"Failed to delete session: {session_id}")
    
    elif args.session_command == "search":
        query = " ".join(args.query) if args.query else ""
        
        if not query:
            print_error("Please provide a search query")
            return
        
        print_section(f"Searching for: {query}")
        
        results = session_mgr.search(query, limit=10)
        
        if not results:
            print_info("No matching conversations found")
            return
        
        print_success(f"Found {len(results)} matching messages")
        
        for i, msg in enumerate(results[:5], 1):
            print(f"\n[bold]{i}. Session: {msg['session_id']}[/bold]")
            print(f"   Role: {msg['role']}")
            print(f"   Content: {msg['content'][:100]}...")
            print(f"   Time: {msg['timestamp']}")


def cmd_cache(args):
    """Handle cache management commands."""
    from .utils.cache import get_cache
    from .utils.formatter import print_header, print_section, print_data, print_success
    
    cache = get_cache()
    
    if args.cache_command == "stats":
        print_header("Cache Statistics", "Performance")
        
        stats = cache.get_stats()
        
        print_data({
            "Total Entries": stats['total_entries'],
            "Cache Size": f"{stats['total_size_mb']:.2f} MB / {stats['max_size_mb']:.0f} MB",
            "TTL": f"{stats['ttl_hours']:.0f} hours",
            "Location": stats['cache_dir'],
        })
    
    elif args.cache_command == "clear":
        print_section("Clearing Cache")
        
        older_than = args.older_than if hasattr(args, 'older_than') else None
        cleared = cache.clear(older_than)
        
        print_success(f"Cleared {cleared} cache entries")
    
    elif args.cache_command == "cleanup":
        print_section("Running Cache Cleanup")
        
        removed = cache.cleanup()
        
        print_success(f"Removed {removed} expired/old entries")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="agent",
        description="CLI AI Agent - Intelligent assistant with tool calling capabilities",
        epilog="Examples:\n"
        "  agent debug cors issue\n"
        "  agent analyze logs app.log\n"
        "  agent health-check http://localhost:5000\n"
        "  agent read app.py\n"
        "  agent find 'TODO' in ./src\n"
        "  agent fetch-api http://localhost:5000/data\n"
        "  agent test-api /users --base-url http://localhost:5000\n"
        "  agent validate-env\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Configure API key and settings")
    
    # Debug command
    debug_parser = subparsers.add_parser("debug", help="Debug an issue")
    debug_parser.add_argument("query", nargs="*", help="Debug query")
    debug_parser.add_argument("--issue-type", "-t", help="Issue type (e.g., cors, api)")
    debug_parser.add_argument("--file", "-f", help="Log file to analyze")
    debug_parser.set_defaults(func=cmd_debug)
    
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
    exec_parser.set_defaults(func=cmd_exec)
    
    # Tools command
    tools_parser = subparsers.add_parser("tools", help="List available tools")
    tools_parser.set_defaults(func=lambda args: print("\n".join(ToolRegistry.list_tools())))
    
    # Version command
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=cmd_version)
    
    # Chat command (with streaming support)
    chat_parser = subparsers.add_parser("chat", help="Chat with AI agent")
    chat_parser.add_argument("query", nargs="*", help="Your message")
    chat_parser.add_argument("--stream", "-s", action="store_true", help="Stream response in real-time")
    chat_parser.set_defaults(func=cmd_chat)
    
    # Plugin management command
    plugin_parser = subparsers.add_parser("plugin", help="Manage plugins")
    plugin_parser.add_argument("plugin_command", choices=["list", "install", "uninstall"], help="Plugin command")
    plugin_parser.add_argument("--name", "-n", help="Plugin name (for install/uninstall)")
    plugin_parser.set_defaults(func=cmd_plugin)
    
    # Session management command
    session_parser = subparsers.add_parser("session", help="Manage conversation sessions")
    session_parser.add_argument("session_command", choices=["new", "list", "load", "delete", "search"], help="Session command")
    session_parser.add_argument("--session-id", "-s", help="Session ID (for load/delete)")
    session_parser.add_argument("--topic", "-t", help="Session topic (for new)")
    session_parser.add_argument("query", nargs="*", help="Search query (for search)")
    session_parser.set_defaults(func=cmd_session)
    
    # Cache management command
    cache_parser = subparsers.add_parser("cache", help="Manage response cache")
    cache_parser.add_argument("cache_command", choices=["stats", "clear", "cleanup"], help="Cache command")
    cache_parser.add_argument("--older-than", type=int, help="Clear entries older than X hours")
    cache_parser.set_defaults(func=cmd_cache)
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "setup":
        setup_wizard()
    elif hasattr(args, "func"):
        try:
            # Validate config for commands that need it
            config = get_config()
            if args.command not in ["version", "tools", "setup"]:
                try:
                    config.validate()
                except ConfigError as e:
                    print_error(str(e))
                    print_info("Run 'agent setup' to configure your API key")
                    sys.exit(1)
            
            args.func(args)
        except KeyboardInterrupt:
            print("\n")
            print_warning("Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print_error(f"Error: {str(e)}")
            if config.debug_mode:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
