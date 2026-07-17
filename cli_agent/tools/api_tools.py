"""API operation tools for CLI AI Agent."""

from typing import Dict, Any, Optional
import requests
import time

from .base import BaseTool
from .registry import register_tool
from ..utils.exceptions import ToolError
from ..utils.logger import get_logger
from ..utils.retry import retry_with_backoff

logger = get_logger(__name__)


@register_tool
class FetchAPIDataTool(BaseTool):
    """Fetch data from an API endpoint."""

    name = "fetch_api_data"
    description = "Fetch data from a REST API endpoint using HTTP GET request"
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL of the API endpoint",
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds (default: 30)",
            },
        },
        "required": ["url"],
    }

    def execute(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute the API fetch operation with retry logic."""
        
        @retry_with_backoff(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
            jitter=True,
            retryable_exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError)
        )
        def make_request():
            logger.info(f"Fetching data from: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        
        try:
            response = make_request()
            
            # Try to parse as JSON
            try:
                data = response.json()
            except ValueError:
                data = {"text": response.text[:1000]}  # First 1000 chars
            
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "data": data,
                "content_length": len(response.content),
            }
        
        except requests.exceptions.Timeout:
            raise ToolError(self.name, f"Request timeout after {timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise ToolError(self.name, f"Connection error: {str(e)}", original_error=e)
        except requests.exceptions.HTTPError as e:
            raise ToolError(self.name, f"HTTP error: {str(e)}", original_error=e)
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class CheckHealthTool(BaseTool):
    """Check health/status of an API endpoint."""

    name = "check_health"
    description = "Check the health status of a web service or API endpoint"
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL of the service to check",
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds (default: 10)",
            },
        },
        "required": ["url"],
    }

    def execute(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Execute the health check operation with retry logic."""
        
        @retry_with_backoff(
            max_retries=2,
            base_delay=0.5,
            max_delay=10.0,
            jitter=True,
            retryable_exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError)
        )
        def make_request():
            response = requests.get(url, timeout=timeout)
            return response
        
        try:
            start_time = time.time()
            response = make_request()
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            # Determine health status
            status = "healthy" if response.status_code < 400 else "unhealthy"
            
            return {
                "success": True,
                "url": url,
                "status": status,
                "http_status": response.status_code,
                "response_time_ms": response_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "url": url,
                "status": "timeout",
                "error": f"Request timed out after {timeout}s",
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "url": url,
                "status": "unreachable",
                "error": f"Connection failed: {str(e)}",
            }
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)


@register_tool
class TestEndpointTool(BaseTool):
    """Test an API endpoint with various HTTP methods."""

    name = "test_endpoint"
    description = "Test an API endpoint with HTTP methods and validate responses"
    parameters = {
        "type": "object",
        "properties": {
            "endpoint": {
                "type": "string",
                "description": "API endpoint path (e.g., '/api/users')",
            },
            "base_url": {
                "type": "string",
                "description": "Base URL (e.g., 'http://localhost:5000')",
            },
            "method": {
                "type": "string",
                "description": "HTTP method (GET, POST, PUT, DELETE)",
            },
        },
        "required": ["endpoint", "base_url"],
    }

    def execute(
        self,
        endpoint: str,
        base_url: str,
        method: str = "GET",
    ) -> Dict[str, Any]:
        """Execute the endpoint test operation with retry logic."""
        url = f"{base_url.rstrip('/')}{endpoint}"
        method = method.upper()
        
        logger.info(f"Testing {method} {url}")
        
        @retry_with_backoff(
            max_retries=2,
            base_delay=1.0,
            max_delay=20.0,
            jitter=True,
            retryable_exceptions=(requests.exceptions.Timeout, requests.exceptions.ConnectionError)
        )
        def make_request():
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json={}, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json={}, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, timeout=30)
            else:
                raise ToolError(self.name, f"Unsupported HTTP method: {method}")
            
            response_time = round((time.time() - start_time) * 1000, 2)
            return response, response_time
        
        try:
            response, response_time = make_request()
            
            # Analyze response
            issues = []
            if response.status_code >= 500:
                issues.append("Server error (5xx)")
            elif response.status_code >= 400:
                issues.append("Client error (4xx)")
            
            # Check response time
            if response_time > 1000:
                issues.append(f"Slow response: {response_time}ms")
            
            return {
                "success": response.status_code < 400,
                "endpoint": endpoint,
                "base_url": base_url,
                "method": method,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "issues": issues,
                "headers": dict(response.headers),
            }
        
        except Exception as e:
            raise ToolError(self.name, str(e), original_error=e)
