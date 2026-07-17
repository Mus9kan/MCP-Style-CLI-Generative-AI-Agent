"""SQLite database for persistent conversation memory."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MemoryDB:
    """SQLite-based persistent memory storage for conversations."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize memory database.
        
        Args:
            db_path: Path to SQLite database file (default: ~/.cli_agent/memory.db)
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.home() / ".cli_agent" / "memory.db"
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"Memory database initialized: {self.db_path}")

    def _init_db(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    topic TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tool_used TEXT,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)
            
            # Context table for storing user preferences and facts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id, timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_context_key 
                ON context(key)
            """)
            
            conn.commit()
        
        logger.debug("Database tables initialized")

    def create_session(self, session_id: str, topic: Optional[str] = None) -> bool:
        """
        Create a new conversation session.
        
        Args:
            session_id: Unique session identifier
            topic: Optional topic/title for the session
            
        Returns:
            True if session created successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sessions (session_id, topic) VALUES (?, ?)",
                    (session_id, topic)
                )
                conn.commit()
            
            logger.info(f"Session created: {session_id}")
            return True
        
        except sqlite3.IntegrityError:
            logger.warning(f"Session already exists: {session_id}")
            return False

    def save_message(self, session_id: str, role: str, content: str, 
                     tool_used: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Save a message to a session.
        
        Args:
            session_id: Session identifier
            role: Message role (user, assistant, system, tool)
            content: Message content
            tool_used: Tool name if applicable
            metadata: Additional metadata as dict
            
        Returns:
            True if message saved successfully
        """
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert message
                cursor.execute(
                    """INSERT INTO messages 
                       (session_id, role, content, tool_used, metadata) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, role, content, tool_used, 
                     json.dumps(metadata) if metadata else None)
                )
                
                # Update session stats
                cursor.execute(
                    """UPDATE sessions 
                       SET updated_at = CURRENT_TIMESTAMP, 
                           message_count = message_count + 1 
                       WHERE session_id = ?""",
                    (session_id,)
                )
                
                conn.commit()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return False

    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """SELECT * FROM messages 
                       WHERE session_id = ? 
                       ORDER BY timestamp DESC 
                       LIMIT ?""",
                    (session_id, limit)
                )
                
                rows = cursor.fetchall()
                
                # Convert to list of dicts and reverse to chronological order
                messages = []
                for row in reversed(rows):
                    msg = dict(row)
                    if msg.get("metadata"):
                        msg["metadata"] = json.loads(msg["metadata"])
                    messages.append(msg)
                
                return messages
        
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversation history for relevant messages.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            List of matching message dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Simple text search (can be enhanced with full-text search)
                cursor.execute(
                    """SELECT m.*, s.topic 
                       FROM messages m
                       JOIN sessions s ON m.session_id = s.session_id
                       WHERE m.content LIKE ? 
                       ORDER BY m.timestamp DESC 
                       LIMIT ?""",
                    (f"%{query}%", limit)
                )
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []

    def save_context(self, key: str, value: str, category: Optional[str] = None) -> bool:
        """
        Save contextual information (user preferences, facts, etc.).
        
        Args:
            key: Context key
            value: Context value
            category: Optional category for organization
            
        Returns:
            True if context saved successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO context (key, value, category) 
                       VALUES (?, ?, ?)
                       ON CONFLICT(key) 
                       DO UPDATE SET value = ?, 
                                   updated_at = CURRENT_TIMESTAMP""",
                    (key, value, category, value)
                )
                conn.commit()
            
            logger.debug(f"Context saved: {key}={value}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            return False

    def get_context(self, key: str) -> Optional[str]:
        """
        Retrieve a context value by key.
        
        Args:
            key: Context key
            
        Returns:
            Context value or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value FROM context WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return None

    def get_all_context(self, category: Optional[str] = None) -> Dict[str, str]:
        """
        Retrieve all context values, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of key-value pairs
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if category:
                    cursor.execute(
                        "SELECT key, value FROM context WHERE category = ?",
                        (category,)
                    )
                else:
                    cursor.execute("SELECT key, value FROM context")
                
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}
        
        except Exception as e:
            logger.error(f"Failed to get all context: {e}")
            return {}

    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """SELECT session_id, topic, created_at, updated_at, message_count 
                       FROM sessions 
                       WHERE session_id = ?""",
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        "session_id": row[0],
                        "topic": row[1],
                        "created_at": row[2],
                        "updated_at": row[3],
                        "message_count": row[4],
                    }
                return None
        
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return None

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List all sessions ordered by most recent.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    """SELECT * FROM sessions 
                       ORDER BY updated_at DESC 
                       LIMIT ?""",
                    (limit,)
                )
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session deleted successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first (foreign key constraint)
                cursor.execute(
                    "DELETE FROM messages WHERE session_id = ?",
                    (session_id,)
                )
                
                # Delete session
                cursor.execute(
                    "DELETE FROM sessions WHERE session_id = ?",
                    (session_id,)
                )
                
                conn.commit()
            
            logger.info(f"Session deleted: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
