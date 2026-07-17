"""Session manager for persistent conversations."""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.logger import get_logger
from .database import MemoryDB

logger = get_logger(__name__)


class SessionManager:
    """Manages conversation sessions with persistent storage."""

    def __init__(self, db: MemoryDB):
        """
        Initialize session manager.
        
        Args:
            db: MemoryDB instance
        """
        self.db = db
        self.current_session: Optional[str] = None
        logger.info("Session manager initialized")

    def create_session(self, topic: Optional[str] = None) -> str:
        """
        Create a new conversation session.
        
        Args:
            topic: Optional topic/title for the session
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())[:8]  # Short ID for usability
        
        success = self.db.create_session(session_id, topic)
        
        if success:
            self.current_session = session_id
            logger.info(f"New session created: {session_id}")
        else:
            # Session already exists, try again
            return self.create_session(topic)
        
        return session_id

    def load_session(self, session_id: str) -> bool:
        """
        Load an existing session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session loaded successfully
        """
        stats = self.db.get_session_stats(session_id)
        
        if not stats:
            logger.error(f"Session not found: {session_id}")
            return False
        
        self.current_session = session_id
        logger.info(f"Session loaded: {session_id} ({stats['message_count']} messages)")
        
        return True

    def get_current_session(self) -> Optional[str]:
        """Get current session ID."""
        return self.current_session

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List all sessions ordered by most recent.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries
        """
        return self.db.list_sessions(limit)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session deleted successfully
        """
        if self.current_session == session_id:
            self.current_session = None
        
        return self.db.delete_session(session_id)

    def save_message(self, role: str, content: str, 
                     tool_used: Optional[str] = None, 
                     metadata: Optional[Dict] = None) -> bool:
        """
        Save a message to the current session.
        
        Args:
            role: Message role (user, assistant, system, tool)
            content: Message content
            tool_used: Tool name if applicable
            metadata: Additional metadata
            
        Returns:
            True if message saved successfully
        """
        if not self.current_session:
            logger.warning("No active session, creating one")
            self.create_session()
        
        return self.db.save_message(
            self.current_session,
            role,
            content,
            tool_used,
            metadata
        )

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history for current session.
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of message dictionaries
        """
        if not self.current_session:
            return []
        
        return self.db.get_conversation_history(self.current_session, limit)

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversation history.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching messages
        """
        return self.db.search_conversations(query, limit)
