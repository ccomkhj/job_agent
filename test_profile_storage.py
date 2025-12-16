#!/usr/bin/env python3
"""
Test script for the profile storage functionality
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from schemas.models import (
    CareerBackground,
    ProfileCreateRequest,
    ProfileUpdateRequest,
    UserProfile,
)
from services.profile_storage import ProfileStorageService


def test_profile_storage():
    """Test the profile storage service"""
    print("🧪 Testing Profile Storage Service")
    print("=" * 50)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "test_profiles.json"
        storage = ProfileStorageService(str(storage_path))

        try:
            # Test 1: Create a profile
            print("📝 Test 1: Creating a profile...")
            user_profile = UserProfile(
                career_background=CareerBackground(
                    data_science="Machine Learning Engineer with 5+ years experience",
                    data_engineering="Data Engineer specializing in ETL pipelines",
                    computer_vision="Computer Vision experience with OpenCV",
                    cto="Technical leadership and team management",
                ),
                education_background="MS in Computer Science from Stanford",
                motivation="Passionate about data-driven solutions",
            )

            create_request = ProfileCreateRequest(
                name="Test Profile", user_profile=user_profile, is_default=True
            )

            created_profile = storage.create_profile(create_request)
            print("✅ Profile created successfully")
            print(f"   ID: {created_profile.id}")
            print(f"   Name: {created_profile.name}")
            print(f"   Is Default: {created_profile.is_default}")

            profile_id = created_profile.id

            # Test 2: Retrieve the profile
            print("\n📖 Test 2: Retrieving the profile...")
            retrieved_profile = storage.get_profile(profile_id)
            if retrieved_profile and retrieved_profile.id == profile_id:
                print("✅ Profile retrieved successfully")
            else:
                print("❌ Profile retrieval failed")
                return False

            # Test 3: Update the profile
            print("\n✏️  Test 3: Updating the profile...")
            update_request = ProfileUpdateRequest(
                name="Updated Test Profile", is_default=False
            )
            updated_profile = storage.update_profile(profile_id, update_request)
            if (
                updated_profile
                and updated_profile.name == "Updated Test Profile"
                and not updated_profile.is_default
            ):
                print("✅ Profile updated successfully")
            else:
                print("❌ Profile update failed")
                return False

            # Test 4: Create another profile and test default switching
            print("\n📝 Test 4: Creating second profile and testing default...")
            create_request2 = ProfileCreateRequest(
                name="Second Profile", user_profile=user_profile, is_default=True
            )
            created_profile2 = storage.create_profile(create_request2)

            # Check that default switched
            default_profile = storage.get_default_profile()
            if default_profile and default_profile.id == created_profile2.id:
                print("✅ Default profile switched correctly")
            else:
                print("❌ Default profile switching failed")
                return False

            # Test 5: List all profiles
            print("\n📋 Test 5: Listing all profiles...")
            all_profiles = storage.get_all_profiles()
            if len(all_profiles) == 2:
                print(f"✅ Retrieved {len(all_profiles)} profiles")
            else:
                print(f"❌ Expected 2 profiles, got {len(all_profiles)}")
                return False

            # Test 6: Delete a profile
            print("\n🗑️  Test 6: Deleting a profile...")
            deleted = storage.delete_profile(profile_id)
            if deleted:
                # Check it's gone
                retrieved_after_delete = storage.get_profile(profile_id)
                if retrieved_after_delete is None:
                    print("✅ Profile deleted successfully")
                else:
                    print("❌ Profile still exists after deletion")
                    return False
            else:
                print("❌ Profile deletion failed")
                return False

            print("\n🎉 All profile storage tests passed!")
            return True

        except Exception as e:
            print(f"\n❌ Profile storage test failed: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = test_profile_storage()
    sys.exit(0 if success else 1)
