import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from schemas.models import (
    ProfileCreateRequest,
    ProfileUpdateRequest,
    StoredUserProfile,
    UserProfile,
)


class ProfileStorageService:
    """Simple JSON-based profile storage service"""

    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            # Default to backend/data directory
            backend_dir = Path(__file__).parent.parent
            self.storage_path = backend_dir / "data" / "profiles.json"
        else:
            self.storage_path = Path(storage_path)

        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize storage if it doesn't exist
        if not self.storage_path.exists():
            self._initialize_storage()

    def _initialize_storage(self):
        """Initialize the storage file with empty structure"""
        initial_data = {"profiles": [], "default_profile_id": None}
        with open(self.storage_path, "w") as f:
            json.dump(initial_data, f, indent=2, default=str)

    def _load_data(self) -> Dict[str, Any]:
        """Load data from storage file"""
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Reinitialize if corrupted
            self._initialize_storage()
            return {"profiles": [], "default_profile_id": None}

    def _save_data(self, data: Dict[str, Any]):
        """Save data to storage file"""
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def create_profile(self, request: ProfileCreateRequest) -> StoredUserProfile:
        """Create a new profile"""
        data = self._load_data()

        # Generate unique ID
        profile_id = str(uuid.uuid4())

        # If this is set as default, unset other defaults
        if request.is_default:
            for profile in data["profiles"]:
                profile["is_default"] = False
            data["default_profile_id"] = profile_id

        # Create stored profile
        stored_profile = StoredUserProfile(
            id=profile_id,
            name=request.name,
            user_profile=request.user_profile,
            is_default=request.is_default,
        )

        # Add to storage
        profile_dict = stored_profile.dict()
        data["profiles"].append(profile_dict)

        self._save_data(data)
        return stored_profile

    def get_profile(self, profile_id: str) -> Optional[StoredUserProfile]:
        """Get a profile by ID"""
        data = self._load_data()

        for profile_data in data["profiles"]:
            if profile_data["id"] == profile_id:
                return StoredUserProfile(**profile_data)

        return None

    def get_all_profiles(self) -> List[StoredUserProfile]:
        """Get all profiles"""
        data = self._load_data()

        profiles = []
        for profile_data in data["profiles"]:
            profiles.append(StoredUserProfile(**profile_data))

        return profiles

    def get_default_profile(self) -> Optional[StoredUserProfile]:
        """Get the default profile"""
        data = self._load_data()
        default_id = data.get("default_profile_id")

        if default_id:
            return self.get_profile(default_id)

        return None

    def update_profile(
        self, profile_id: str, request: ProfileUpdateRequest
    ) -> Optional[StoredUserProfile]:
        """Update an existing profile"""
        data = self._load_data()

        for i, profile_data in enumerate(data["profiles"]):
            if profile_data["id"] == profile_id:
                # Update fields
                if request.name is not None:
                    profile_data["name"] = request.name
                if request.user_profile is not None:
                    profile_data["user_profile"] = request.user_profile.dict()
                if request.is_default is not None:
                    profile_data["is_default"] = request.is_default
                    if request.is_default:
                        # Unset other defaults
                        for j, other_profile in enumerate(data["profiles"]):
                            if i != j:
                                other_profile["is_default"] = False
                        data["default_profile_id"] = profile_id

                profile_data["updated_at"] = datetime.utcnow().isoformat()

                self._save_data(data)
                return StoredUserProfile(**profile_data)

        return None

    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        data = self._load_data()

        for i, profile_data in enumerate(data["profiles"]):
            if profile_data["id"] == profile_id:
                # If this was the default, clear default
                if profile_data.get("is_default"):
                    data["default_profile_id"] = None

                # Remove from list
                data["profiles"].pop(i)
                self._save_data(data)
                return True

        return False

    def set_default_profile(self, profile_id: str) -> bool:
        """Set a profile as the default"""
        data = self._load_data()

        # Check if profile exists
        profile_exists = any(p["id"] == profile_id for p in data["profiles"])
        if not profile_exists:
            return False

        # Unset all defaults and set new one
        for profile_data in data["profiles"]:
            profile_data["is_default"] = profile_data["id"] == profile_id

        data["default_profile_id"] = profile_id
        self._save_data(data)
        return True


class LocalProfileService:
    """Service for simple local profile storage (single profile)"""

    def __init__(self, storage_file: str = "data/local_profile.json"):
        self.storage_file = storage_file
        # Ensure directory exists
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)

    def save_profile(self, profile: UserProfile) -> None:
        """Save a single profile to local file"""
        # Convert to dict for JSON serialization
        data = profile.dict()

        with open(self.storage_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def load_profile(self) -> Optional[UserProfile]:
        """Load the single profile from local file"""
        if not os.path.exists(self.storage_file):
            return None

        try:
            with open(self.storage_file, "r") as f:
                data = json.load(f)
                return UserProfile(**data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading local profile: {e}")
            return None

    def has_profile(self) -> bool:
        """Check if a profile exists"""
        return os.path.exists(self.storage_file)

    def delete_profile(self) -> bool:
        """Delete the local profile"""
        if os.path.exists(self.storage_file):
            os.remove(self.storage_file)
            return True
        return False
