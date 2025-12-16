#!/usr/bin/env python3
"""
Simple test script to verify the JobDescriptionLoader improvements
without running the full server.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from loaders.job_description_loader import JobDescriptionLoader

def test_authentication_detection():
    """Test that authentication redirects are properly detected"""
    loader = JobDescriptionLoader()

    print("Testing authentication detection logic...")

    # Test 1: URL redirect to login page
    mock_response_redirect = Mock()
    mock_response_redirect.url = "https://www.linkedin.com/uas/login?session_redirect=..."
    mock_response_redirect.text = "Please sign in to continue"

    result = loader._is_redirected_to_login(mock_response_redirect, "https://www.linkedin.com/jobs/123")
    if result:
        print("✅ Successfully detected URL redirect to login page")
    else:
        print("❌ Failed to detect URL redirect to login page")

    # Test 2: Content contains login indicators
    mock_response_content = Mock()
    mock_response_content.url = "https://www.linkedin.com/jobs/123"
    mock_response_content.text = "You must be logged in to view this job posting"

    result = loader._is_redirected_to_login(mock_response_content, "https://www.linkedin.com/jobs/123")
    if result:
        print("✅ Successfully detected login content in response")
    else:
        print("❌ Failed to detect login content in response")

    # Test 3: Normal response (no authentication)
    mock_response_normal = Mock()
    mock_response_normal.url = "https://www.indeed.com/jobs/123"
    mock_response_normal.text = "Senior Data Engineer position at Example Company"

    result = loader._is_redirected_to_login(mock_response_normal, "https://www.indeed.com/jobs/123")
    if not result:
        print("✅ Correctly identified normal response (no authentication)")
    else:
        print("❌ Incorrectly flagged normal response as requiring authentication")

    print("\nAll authentication detection tests completed!")

if __name__ == "__main__":
    print("Testing JobDescriptionLoader authentication detection...")
    test_authentication_detection()
