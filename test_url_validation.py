#!/usr/bin/env python3
"""
Test script for URL validation and job platform detection
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from loaders.job_description_loader import JobDescriptionLoader


def test_url_validation():
    """Test URL validation functionality"""
    print("🧪 Testing URL Validation")
    print("=" * 50)

    loader = JobDescriptionLoader()

    # Test cases
    test_cases = [
        # Valid job URLs
        ("https://www.indeed.com/viewjob?jk=123456789", True, "Indeed"),
        ("https://www.glassdoor.com/job-listing/software-engineer", True, "Glassdoor"),
        ("https://www.linkedin.com/jobs/view/senior-data-scientist", True, "LinkedIn"),
        (
            "https://careers.google.com/jobs/results/123456789",
            True,
            "Company Career Page",
        ),
        ("https://jobs.monster.com/senior-developer", True, "Monster"),
        # Invalid URLs
        ("not-a-url", False, None),
        ("", False, None),
        ("https://facebook.com/jobs/post123", False, None),  # Social media
        # Edge cases
        ("https://unknown-job-site.com/job/123", True, "Unknown Platform"),
    ]

    success_count = 0

    for url, expected_valid, expected_provider in test_cases:
        try:
            result = loader.validate_and_analyze_url(url)

            if result["valid"] == expected_valid:
                if expected_provider:
                    actual_provider = result.get("platform_info", {}).get(
                        "provider", "Unknown"
                    )
                    # More flexible matching
                    provider_match = (
                        actual_provider.lower() == expected_provider.lower()
                        or (
                            expected_provider == "Company Career Page"
                            and "career" in actual_provider.lower()
                        )
                        or (
                            expected_provider == "LinkedIn"
                            and "linkedin" in actual_provider.lower()
                        )
                    )
                    if provider_match:
                        print(f"✅ {url[:50]}... -> {actual_provider}")
                        success_count += 1
                    else:
                        print(
                            f"❌ {url[:50]}... -> Expected {expected_provider}, got {actual_provider}"
                        )
                else:
                    print(
                        f"✅ {url[:30] if url else 'Empty URL'} -> Correctly {'valid' if expected_valid else 'invalid'}"
                    )
                    success_count += 1
            else:
                print(
                    f"❌ {url[:50]}... -> Expected {'valid' if expected_valid else 'invalid'}, got {'valid' if result['valid'] else 'invalid'}"
                )

        except Exception as e:
            print(f"❌ {url[:50]}... -> Exception: {e}")

    print(f"\nResults: {success_count}/{len(test_cases)} tests passed")

    # Test platform-specific recommendations
    print("\n🧪 Testing Platform Recommendations")
    print("=" * 50)

    recommendation_tests = [
        ("https://www.linkedin.com/jobs/view/123", "requires login"),
        ("https://www.indeed.com/viewjob?jk=123", "works reliably"),
        ("https://careers.microsoft.com/job/123", "direct company sites"),
    ]

    for url, expected_keyword in recommendation_tests:
        result = loader.validate_and_analyze_url(url)
        if result["valid"] and result["platform_info"]:
            recommendation = result["platform_info"]["recommendation"]
            if expected_keyword.lower() in recommendation.lower():
                print(f"✅ {result['platform_info']['provider']} -> {recommendation}")
            else:
                print(
                    f"❌ {result['platform_info']['provider']} -> Expected '{expected_keyword}' in recommendation"
                )

    return success_count == len(test_cases)


if __name__ == "__main__":
    success = test_url_validation()
    sys.exit(0 if success else 1)


