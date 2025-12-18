import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from schemas.models import ChatMessage, MessageType


@dataclass
class SessionData:
    """Session data structure"""

    session_id: str
    current_job_url: Optional[str] = None
    current_profile_id: Optional[str] = None
    messages: List[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


class SessionManager:
    """Session management service for chat persistence"""

    def __init__(
        self, storage_path: Optional[str] = None, session_timeout_hours: int = 24
    ):
        if storage_path is None:
            # Default to backend/data directory
            backend_dir = Path(__file__).parent.parent
            self.storage_path = backend_dir / "data" / "sessions"
        else:
            self.storage_path = Path(storage_path)

        self.session_timeout = timedelta(hours=session_timeout_hours)

        # Ensure directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a session"""
        return self.storage_path / f"{session_id}.json"

    def create_session(self) -> SessionData:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session_data = SessionData(session_id=session_id)

        self._save_session(session_data)
        return session_data

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data by ID"""
        session_file = self._get_session_file(session_id)

        if not session_file.exists():
            return None

        try:
            with open(session_file, "r") as f:
                data = json.load(f)

            # Convert back to SessionData
            session_data = SessionData(
                session_id=data["session_id"],
                current_job_url=data.get("current_job_url"),
                current_profile_id=data.get("current_profile_id"),
                messages=data.get("messages", []),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )

            # Check if session has expired
            if datetime.utcnow() - session_data.updated_at > self.session_timeout:
                self.delete_session(session_id)
                return None

            return session_data

        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            # Invalid session file, clean it up
            self._cleanup_invalid_session(session_id)
            return None

    def update_session(self, session_data: SessionData) -> SessionData:
        """Update session data"""
        session_data.updated_at = datetime.utcnow()
        self._save_session(session_data)
        return session_data

    def set_current_job_url(
        self, session_id: str, job_url: str
    ) -> Optional[SessionData]:
        """Set the current job URL for a session"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data.current_job_url = job_url
            return self.update_session(session_data)
        return None

    def set_current_profile_id(
        self, session_id: str, profile_id: str
    ) -> Optional[SessionData]:
        """Set the current profile ID for a session"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data.current_profile_id = profile_id
            return self.update_session(session_data)
        return None

    def add_message(
        self,
        session_id: str,
        message_type: MessageType,
        content: Any,
        timestamp: Optional[datetime] = None,
    ) -> Optional[SessionData]:
        """Add a message to the session chat history"""
        session_data = self.get_session(session_id)
        if session_data:
            message = {
                "id": str(uuid.uuid4()),
                "type": message_type,
                "content": content,
                "timestamp": (timestamp or datetime.utcnow()).isoformat(),
            }
            session_data.messages.append(message)
            return self.update_session(session_data)
        return None

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat messages for a session"""
        session_data = self.get_session(session_id)
        return session_data.messages if session_data else []

    def clear_messages(self, session_id: str) -> Optional[SessionData]:
        """Clear chat messages for a session"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data.messages = []
            return self.update_session(session_data)
        return None

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session_file = self._get_session_file(session_id)
        try:
            session_file.unlink(missing_ok=True)
            return True
        except Exception:
            return False

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions, return number cleaned"""
        cleaned_count = 0

        if not self.storage_path.exists():
            return 0

        for session_file in self.storage_path.glob("*.json"):
            try:
                session_id = session_file.stem
                session_data = self.get_session(session_id)
                if session_data is None:
                    # Session was invalid/expired and already cleaned up
                    cleaned_count += 1
            except Exception:
                # Clean up corrupted files
                session_file.unlink(missing_ok=True)
                cleaned_count += 1

        return cleaned_count

    def _save_session(self, session_data: SessionData):
        """Save session data to file"""
        session_file = self._get_session_file(session_data.session_id)

        # Convert to dict for JSON serialization
        data = asdict(session_data)
        # Convert datetime objects to ISO strings
        data["created_at"] = session_data.created_at.isoformat()
        data["updated_at"] = session_data.updated_at.isoformat()

        with open(session_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _cleanup_invalid_session(self, session_id: str):
        """Clean up an invalid session file"""
        session_file = self._get_session_file(session_id)
        session_file.unlink(missing_ok=True)




