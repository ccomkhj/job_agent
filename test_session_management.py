#!/usr/bin/env python3
"""
Test script for the session management functionality
"""

import asyncio
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from schemas.models import MessageType
from services.session_manager import SessionData, SessionManager


def test_session_management():
    """Test the session management service"""
    print("🧪 Testing Session Management Service")
    print("=" * 50)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "test_sessions"
        session_manager = SessionManager(str(storage_path))

        try:
            # Test 1: Create a session
            print("📝 Test 1: Creating a session...")
            session_data = session_manager.create_session()
            print("✅ Session created successfully")
            print(f"   ID: {session_data.session_id}")
            print(f"   Created: {session_data.created_at}")
            print(f"   Messages: {len(session_data.messages)}")

            session_id = session_data.session_id

            # Test 2: Retrieve the session
            print("\n📖 Test 2: Retrieving the session...")
            retrieved_session = session_manager.get_session(session_id)
            if retrieved_session and retrieved_session.session_id == session_id:
                print("✅ Session retrieved successfully")
            else:
                print("❌ Session retrieval failed")
                return False

            # Test 3: Update session data
            print("\n✏️  Test 3: Updating session data...")
            updated_session = session_manager.set_current_job_url(
                session_id, "https://example.com/job"
            )
            if (
                updated_session
                and updated_session.current_job_url == "https://example.com/job"
            ):
                print("✅ Job URL updated successfully")
            else:
                print("❌ Job URL update failed")
                return False

            updated_session2 = session_manager.set_current_profile_id(
                session_id, "profile-123"
            )
            if (
                updated_session2
                and updated_session2.current_profile_id == "profile-123"
            ):
                print("✅ Profile ID updated successfully")
            else:
                print("❌ Profile ID update failed")
                return False

            # Test 4: Add messages
            print("\n💬 Test 4: Adding messages...")
            message_session = session_manager.add_message(
                session_id,
                MessageType.USER,
                "Hello, I need help with a job application",
            )
            if message_session and len(message_session.messages) == 1:
                print("✅ First message added successfully")
            else:
                print("❌ First message addition failed")
                return False

            message_session2 = session_manager.add_message(
                session_id,
                MessageType.ASSISTANT,
                {"type": "cover_letter", "data": {"title": "Test"}},
            )
            if message_session2 and len(message_session2.messages) == 2:
                print("✅ Second message added successfully")
            else:
                print("❌ Second message addition failed")
                return False

            # Test 5: Get messages
            print("\n📋 Test 5: Retrieving messages...")
            messages = session_manager.get_messages(session_id)
            if len(messages) == 2:
                print(f"✅ Retrieved {len(messages)} messages")
                print(f"   First message type: {messages[0]['type']}")
                print(f"   Second message type: {messages[1]['type']}")
            else:
                print(f"❌ Expected 2 messages, got {len(messages)}")
                return False

            # Test 6: Clear messages
            print("\n🧹 Test 6: Clearing messages...")
            cleared_session = session_manager.clear_messages(session_id)
            if cleared_session and len(cleared_session.messages) == 0:
                print("✅ Messages cleared successfully")
            else:
                print("❌ Message clearing failed")
                return False

            # Test 7: Session cleanup (expired sessions)
            print("\n🧽 Test 7: Testing session cleanup...")
            # Create a session manager with very short timeout for testing
            short_timeout_manager = SessionManager(
                str(storage_path), session_timeout_hours=0
            )
            expired_count = short_timeout_manager.cleanup_expired_sessions()
            print(f"✅ Cleanup completed: {expired_count} sessions cleaned")

            # Test 8: Delete session
            print("\n🗑️  Test 8: Deleting session...")
            deleted = session_manager.delete_session(session_id)
            if deleted:
                # Check it's gone
                retrieved_after_delete = session_manager.get_session(session_id)
                if retrieved_after_delete is None:
                    print("✅ Session deleted successfully")
                else:
                    print("❌ Session still exists after deletion")
                    return False
            else:
                print("❌ Session deletion failed")
                return False

            print("\n🎉 All session management tests passed!")
            return True

        except Exception as e:
            print(f"\n❌ Session management test failed: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = test_session_management()
    sys.exit(0 if success else 1)


