"""Core agent logic for LLM interaction and tool orchestration."""

from typing import Dict, Any, List, Optional
import json

from openai import OpenAI

from ..utils.config import get_config
from ..utils.logger import get_logger
from ..utils.exceptions import APIError, ToolError
from ..utils.formatter import print_tool_execution
from ..utils.retry import retry_with_backoff, RetryContext
from ..utils.cache import get_cache
from .intent import IntentClassifier
from ..tools.registry import ToolRegistry
from ..memory import MemoryDB, SessionManager
from ..security import PermissionManager

logger = get_logger(__name__)


class Agent:
    """Main agent class for handling LLM interactions and tool execution."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0, session_id: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            max_retries: Maximum number of retries for failed operations
            retry_delay: Base delay between retries in seconds
            session_id: Optional session ID to load existing session
        """
        self.config = get_config()
        self.client = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if self.config.is_configured():
            self.client = OpenAI(api_key=self.config.api_key)
        
        # Initialize persistent memory
        self.memory_db = MemoryDB()
        self.session_mgr = SessionManager(self.memory_db)
        
        # Initialize security manager
        self.permission_mgr = PermissionManager()
        
        # Initialize response cache
        self.cache = get_cache()
        
        if session_id:
            self.session_mgr.load_session(session_id)
        else:
            self.session_mgr.create_session()
        
        logger.debug(f"Agent initialized with max_retries={max_retries}, retry_delay={retry_delay}s, session={self.session_mgr.get_current_session()}")

    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        return """You are a helpful CLI assistant that helps users with various tasks.
You have access to tools that can:
- Read and search files
- Make API calls and check service health
- Analyze logs and detect issues
- Execute system commands (safely)
- Check environment variables

When a user asks you to do something:
1. Determine if you need to use a tool
2. If yes, call the appropriate tool with correct parameters
3. Use the tool result to provide a helpful response
4. Be concise but informative
5. Format your responses clearly

If you're not sure about something, ask for clarification."""

    def process_request(self, user_input: str, use_llm: bool = True, stream: bool = False) -> Dict[str, Any]:
        """
        Process a user request.

        Args:
            user_input: User's input text
            use_llm: Whether to use LLM for processing
            stream: Whether to stream the response

        Returns:
            Dictionary with response and metadata
        """
        try:
            # First, try rule-based intent classification
            intent = IntentClassifier.classify(user_input)
            
            logger.debug(f"Classified intent: {intent}")
            
            # Save user message to persistent memory
            self.session_mgr.save_message("user", user_input)
            
            # If high confidence tool match, use it directly
            if intent["intent"] == "tool_call" and intent["confidence"] > 0.3:
                tool_name = intent["tool"]
                params = IntentClassifier.extract_parameters(user_input, tool_name)
                
                logger.debug(f"Direct tool call: {tool_name} with params: {params}")
                
                # Execute tool
                result = self._execute_tool(tool_name, params)
                
                # Save response to persistent memory
                response_text = self._format_tool_result(tool_name, result)
                self.session_mgr.save_message("assistant", response_text, tool_used=tool_name)
                
                return {
                    "success": True,
                    "response": response_text,
                    "tool_used": tool_name,
                    "parameters": params,
                    "used_llm": False,
                    "streamed": False,
                    "session_id": self.session_mgr.get_current_session(),
                }
            
            # Otherwise, use LLM if available and requested
            if use_llm and self.client:
                if stream:
                    return self._process_with_llm_stream(user_input)
                return self._process_with_llm(user_input)
            
            # Fallback: simple response
            return {
                "success": True,
                "response": f"I understood: '{user_input}'. Configure OpenAI API key for advanced features.",
                "tool_used": None,
                "used_llm": False,
                "streamed": False,
            }
        
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "error": str(e),
            }

    def _process_with_llm(self, user_input: str) -> Dict[str, Any]:
        """Process request using LLM with tool calling."""
        try:
            # Check cache first
            cached_response = self.cache.get("llm_response", user_input=user_input)
            if cached_response:
                logger.info("Returning cached LLM response")
                cached_response["from_cache"] = True
                return cached_response
            
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
            })
            
            # Get tool definitions
            tools = ToolRegistry.get_tool_definitions()
            
            # Call LLM with retry
            @retry_with_backoff(
                max_retries=self.max_retries,
                base_delay=self.retry_delay,
                max_delay=60.0,
                jitter=True
            )
            def call_llm_api():
                return self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        *self.conversation_history,
                    ],
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=1000,
                )
            
            response = call_llm_api()
            
            assistant_message = response.choices[0].message
            
            # Check if tool call requested
            if assistant_message.tool_calls:
                tool_call = assistant_message.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"LLM requested tool call: {tool_name}")
                
                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)
                
                # Send tool result back to LLM
                self.conversation_history.append(assistant_message.to_dict())
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })
                
                # Get final response from LLM with retry
                @retry_with_backoff(
                    max_retries=self.max_retries,
                    base_delay=self.retry_delay,
                    max_delay=60.0,
                    jitter=True
                )
                def call_llm_final():
                    return self.client.chat.completions.create(
                        model=self.config.model,
                        messages=[
                            {"role": "system", "content": self._get_system_prompt()},
                            *self.conversation_history,
                        ],
                        max_tokens=1000,
                    )
                
                final_response = call_llm_final()
                
                response_text = final_response.choices[0].message.content
                
                result = {
                    "success": True,
                    "response": response_text,
                    "tool_used": tool_name,
                    "parameters": tool_args,
                    "tool_result": result,
                    "used_llm": True,
                    "streamed": False,
                }
                
                # Cache the response
                self.cache.set("llm_response", result, user_input=user_input)
                
                return result
            
            # No tool call, just response
            response_text = assistant_message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text,
            })
            
            result = {
                "success": True,
                "response": response_text,
                "tool_used": None,
                "used_llm": True,
                "streamed": False,
            }
            
            # Cache the response
            self.cache.set("llm_response", result, user_input=user_input)
            
            return result
        
        except Exception as e:
            logger.error(f"LLM processing error: {e}", exc_info=True)
            raise APIError(f"Failed to process with LLM: {str(e)}")

    def _process_with_llm_stream(self, user_input: str) -> Dict[str, Any]:
        """
        Process request using LLM with streaming response.
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with response generator and metadata
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
            })
            
            # Get tool definitions
            tools = ToolRegistry.get_tool_definitions()
            
            # Call LLM with streaming
            @retry_with_backoff(
                max_retries=self.max_retries,
                base_delay=self.retry_delay,
                max_delay=60.0,
                jitter=True
            )
            def call_llm_stream():
                return self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        *self.conversation_history,
                    ],
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=1000,
                    stream=True,  # Enable streaming
                )
            
            response = call_llm_stream()
            
            # Check if LLM wants to use tools
            # For streaming, we need to collect the first chunk to check for tool_calls
            first_chunk = next(response)
            
            if hasattr(first_chunk.choices[0].delta, 'tool_calls') and first_chunk.choices[0].delta.tool_calls:
                # Tool call requested - fall back to non-streaming for tool execution
                logger.info("Tool call requested, falling back to non-streaming mode")
                return self._process_with_llm(user_input)
            
            # No tool calls, stream the response
            def generate_response():
                """Generator that yields text chunks."""
                # Yield first chunk content if present
                if first_chunk.choices[0].delta.content:
                    yield first_chunk.choices[0].delta.content
                
                # Yield remaining chunks
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            return {
                "success": True,
                "response_generator": generate_response(),
                "tool_used": None,
                "used_llm": True,
                "streamed": True,
            }
        
        except Exception as e:
            logger.error(f"LLM streaming error: {e}", exc_info=True)
            raise APIError(f"Failed to stream with LLM: {str(e)}")

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters and retry on failure."""
        try:
            # Security check
            permission = self.permission_mgr.check_permission(tool_name, params)
            
            if not permission["allowed"]:
                logger.warning(f"Tool execution blocked: {tool_name} - {permission['reason']}")
                return {
                    "success": False,
                    "error": f"Permission denied: {permission['reason']}",
                    "blocked_by_security": True,
                }
            
            logger.debug(f"Executing tool: {tool_name}")
            print_tool_execution(tool_name, params)
            
            # Execute tool with retry context
            retry_ctx = RetryContext(
                max_retries=self.max_retries,
                base_delay=self.retry_delay,
                max_delay=30.0,
                operation_name=tool_name
            )
            
            def execute():
                return ToolRegistry.execute_tool(tool_name, **params)
            
            result = retry_ctx.execute(execute)
            
            logger.debug(f"Tool result: {result}")
            
            return result
        
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(tool_name, str(e), original_error=e)

    def _format_tool_result(
        self, tool_name: str, result: Dict[str, Any]
    ) -> str:
        """Format tool result for display."""
        if not result.get("success"):
            return f"❌ Tool '{tool_name}' failed: {result.get('error', 'Unknown error')}"
        
        # Format based on tool type
        formatters = {
            "read_file": lambda r: f"📄 File contents:\n{r.get('content', '')}",
            "check_health": lambda r: (
                f"✅ Status: {r['status'].upper()}\n"
                f"HTTP Code: {r['http_status']}\n"
                f"Response Time: {r['response_time_ms']}ms"
            ),
            "analyze_logs": lambda r: (
                f"📊 Log Analysis:\n"
                f"Total Lines: {r['total_lines']}\n"
                f"Errors: {r['error_count']}\n"
                f"Warnings: {r['warning_count']}"
            ),
            "detect_cors_issue": lambda r: (
                f"{'⚠️' if r['cors_detected'] else '✅'} CORS Analysis:\n"
                f"Issues Found: {r['issue_count']}\n"
                f"Recommendation: {r['recommendation']}"
            ),
            "validate_env": lambda r: (
                f"{'✅' if r['success'] else '⚠️'} Environment Check:\n"
                f"Set: {len(r['set'])}\n"
                f"Missing: {len(r['missing'])}"
            ),
        }
        
        formatter = formatters.get(tool_name, lambda r: str(r))
        return formatter(result)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return ToolRegistry.list_tools()
