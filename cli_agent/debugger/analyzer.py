"""Debug analysis engine for detecting common issues."""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re

from ..utils.logger import get_logger
from ..utils.formatter import print_debug_report

logger = get_logger(__name__)


class DebugAnalyzer:
    """Analyzer for debugging backend systems and detecting issues."""

    # Issue patterns
    ISSUE_PATTERNS = {
        "cors": {
            "patterns": [
                r"Access-Control-Allow-Origin",
                r"CORS.*(?:policy|error)",
                r"cross.origin.*request",
                r"No\s*['\"]Access-Control-Allow-Origin['\"]",
            ],
            "root_causes": [
                "Server not configured to send CORS headers",
                "Missing Access-Control-Allow-Origin header in response",
                "Preflight OPTIONS request not handled",
                "Origin not whitelisted in server configuration",
            ],
            "fixes": [
                "Add CORS middleware to your server",
                "Set header: Access-Control-Allow-Origin: * (or specific origin)",
                "Handle OPTIONS preflight requests",
                "Configure allowed origins in server settings",
            ],
        },
        "api_failure": {
            "patterns": [
                r"(?:API|endpoint).*(?:fail|error|timeout)",
                r"HTTP\s+(?:5\d{2}|4\d{2})",
                r"Connection\s+(?:refused|reset|timed out)",
                r"503\s+Service\s+Unavailable",
            ],
            "root_causes": [
                "Backend service is down or unreachable",
                "API endpoint returning error status",
                "Network connectivity issues",
                "Rate limiting or authentication failure",
            ],
            "fixes": [
                "Check if backend service is running",
                "Verify API endpoint URL and method",
                "Check network/firewall settings",
                "Review API authentication credentials",
            ],
        },
        "missing_headers": {
            "patterns": [
                r"(?:missing|required)\s+header",
                r"Header\s+\w+\s+(?:not\s+)?found",
                r"(?:Content-Type|Authorization).*(?:missing|required)",
            ],
            "root_causes": [
                "Required HTTP header not sent with request",
                "Incorrect Content-Type header",
                "Missing Authorization header",
                "Custom headers not forwarded by proxy",
            ],
            "fixes": [
                "Add required headers to HTTP request",
                "Set Content-Type: application/json for JSON payloads",
                "Include Authorization: Bearer <token> for auth",
                "Configure proxy to forward custom headers",
            ],
        },
        "authentication": {
            "patterns": [
                r"(?:401|Unauthorized|Authentication)\s+(?:failed|required)?",
                r"(?:Invalid|Expired)\s+(?:token|credentials)",
                r"Bearer\s+(?:token\s+)?(?:invalid|expired|missing)",
            ],
            "root_causes": [
                "Invalid or expired authentication token",
                "Missing credentials in request",
                "Token format incorrect",
                "API key invalid or revoked",
            ],
            "fixes": [
                "Refresh or regenerate authentication token",
                "Include valid credentials in request",
                "Check token expiration and renew if needed",
                "Verify API key is correct and active",
            ],
        },
        "database": {
            "patterns": [
                r"(?:Database|DB|SQL).*(?:error|connection|timeout)",
                r"(?:Query|Transaction)\s+(?:failed|error)",
                r"Cannot\s+connect\s+to\s+(?:database|DB)",
            ],
            "root_causes": [
                "Database connection pool exhausted",
                "Database server unreachable",
                "Query syntax error or constraint violation",
                "Connection timeout or network issue",
            ],
            "fixes": [
                "Check database server status",
                "Increase connection pool size",
                "Review and optimize slow queries",
                "Check database credentials and connection string",
            ],
        },
    }

    def __init__(self):
        """Initialize the debug analyzer."""
        self.detected_issues: List[Dict[str, Any]] = []

    def analyze_logs(self, log_content: str) -> Dict[str, Any]:
        """
        Analyze log content for common issues.

        Args:
            log_content: Log file content as string

        Returns:
            Dictionary with analysis results
        """
        self.detected_issues.clear()
        
        lines = log_content.split("\n")
        
        # Check each issue type
        for issue_type, config in self.ISSUE_PATTERNS.items():
            matches = []
            
            for pattern in config["patterns"]:
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        matches.append({
                            "line_number": i + 1,
                            "line": line.strip(),
                            "pattern": pattern,
                        })
            
            if matches:
                # Determine most likely root cause
                root_cause_idx = min(len(matches) - 1, len(config["root_causes"]) - 1)
                fix_idx = root_cause_idx
                
                issue = {
                    "type": issue_type,
                    "severity": self._calculate_severity(issue_type, len(matches)),
                    "occurrences": len(matches),
                    "root_cause": config["root_causes"][root_cause_idx],
                    "suggested_fix": config["fixes"][fix_idx],
                    "sample_lines": [m["line"] for m in matches[:5]],
                }
                
                self.detected_issues.append(issue)
        
        # Sort by severity
        self.detected_issues.sort(key=lambda x: x["severity"], reverse=True)
        
        return {
            "success": True,
            "total_issues": len(self.detected_issues),
            "issues": self.detected_issues,
            "analyzed_lines": len(lines),
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a log file for issues.

        Args:
            file_path: Path to log file

        Returns:
            Dictionary with analysis results
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                }
            
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            result = self.analyze_logs(content)
            result["file"] = str(path.absolute())
            
            return result
        
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _calculate_severity(self, issue_type: str, occurrences: int) -> int:
        """Calculate issue severity (1-10)."""
        base_severity = {
            "authentication": 9,
            "database": 8,
            "api_failure": 7,
            "cors": 6,
            "missing_headers": 5,
        }
        
        base = base_severity.get(issue_type, 5)
        
        # Increase severity with more occurrences
        occurrence_bonus = min(occurrences // 10, 2)
        
        return min(base + occurrence_bonus, 10)

    def print_report(self, issue_index: int = 0) -> None:
        """
        Print formatted debug report for an issue.

        Args:
            issue_index: Index of issue to display
        """
        if not self.detected_issues or issue_index >= len(self.detected_issues):
            print("No issues to display")
            return
        
        issue = self.detected_issues[issue_index]
        
        print_debug_report(
            problem=f"{issue['type'].upper()} detected ({issue['occurrences']} occurrences)",
            root_cause=issue["root_cause"],
            suggested_fix=issue["suggested_fix"],
        )

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Get all detected issues as structured reports."""
        reports = []
        
        for issue in self.detected_issues:
            reports.append({
                "problem": f"{issue['type'].upper()} detected ({issue['occurrences']} occurrences)",
                "root_cause": issue["root_cause"],
                "suggested_fix": issue["suggested_fix"],
                "severity": issue["severity"],
                "samples": issue["sample_lines"],
            })
        
        return reports


def analyze_logs_quick(log_content: str) -> List[Dict[str, Any]]:
    """
    Quick function to analyze logs and return reports.

    Args:
        log_content: Log content to analyze

    Returns:
        List of issue reports
    """
    analyzer = DebugAnalyzer()
    analyzer.analyze_logs(log_content)
    return analyzer.get_all_reports()
