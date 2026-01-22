"""Session manager for conversational context in chat API."""
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ChatSession:
    """Represents a chat session with conversation history."""
    session_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    last_law_id: Optional[str] = None  # Track last queried law for context
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_accessed = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.last_accessed + timedelta(minutes=timeout_minutes)


class SessionManager:
    """Manages chat sessions for the API."""
    
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Minutes before a session expires
        """
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout_minutes = session_timeout_minutes
        logger.info(f"SessionManager initialized with {session_timeout_minutes}min timeout")
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """
        Get existing session or create a new one.
        
        Args:
            session_id: Optional session ID, generates new one if None
            
        Returns:
            ChatSession instance
        """
        # Clean expired sessions periodically
        self._cleanup_expired_sessions()
        
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            if not session.is_expired(self.session_timeout_minutes):
                session.last_accessed = datetime.now()
                logger.info(f"Retrieved existing session: {session_id}")
                return session
            else:
                logger.info(f"Session {session_id} expired, creating new one")
                del self.sessions[session_id]
        
        # Create new session
        new_session_id = session_id or self._generate_session_id()
        session = ChatSession(session_id=new_session_id)
        self.sessions[new_session_id] = session
        logger.info(f"Created new session: {new_session_id}")
        return session
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return f"session_{uuid.uuid4().hex[:12]}"
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from memory."""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout_minutes)
        ]
        for sid in expired:
            del self.sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")
    
    def get_session_count(self) -> int:
        """Get count of active sessions."""
        self._cleanup_expired_sessions()
        return len(self.sessions)
