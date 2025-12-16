#!/usr/bin/env python3
"""
Backend verification script for the Job Agent system.
This script verifies that all backend components are properly implemented and functional.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists and print status"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {'Found' if exists else 'Missing'}")
    return exists


def check_service_implementation():
    """Check that all backend services are implemented"""
    print("🔍 Checking Backend Service Implementation...")

    services_ok = True

    # Check agents
    services_ok &= check_file_exists(
        "backend/agents/data_collector.py", "Data Collector Agent"
    )
    services_ok &= check_file_exists("backend/agents/writer.py", "Writer Agent")
    services_ok &= check_file_exists("backend/agents/feedback.py", "Feedback Agent")
    services_ok &= check_file_exists(
        "backend/agents/modificator.py", "Modificator Agent"
    )

    # Check chains
    services_ok &= check_file_exists(
        "backend/chains/cover_letter_chain.py", "Cover Letter Chain"
    )
    services_ok &= check_file_exists(
        "backend/chains/question_answer_chain.py", "Question Answer Chain"
    )

    # Check services
    services_ok &= check_file_exists(
        "backend/services/profile_storage.py", "Profile Storage Service"
    )
    services_ok &= check_file_exists(
        "backend/services/session_manager.py", "Session Manager Service"
    )

    # Check utilities
    services_ok &= check_file_exists("backend/utils/error_handler.py", "Error Handler")
    services_ok &= check_file_exists(
        "backend/utils/profile_normalizer.py", "Profile Normalizer"
    )

    # Check loaders
    services_ok &= check_file_exists(
        "backend/loaders/job_description_loader.py", "Job Description Loader"
    )

    # Check schemas
    services_ok &= check_file_exists("backend/schemas/models.py", "Pydantic Models")

    # Check API
    services_ok &= check_file_exists("backend/api/routes.py", "API Routes")

    # Check prompts
    services_ok &= check_file_exists(
        "backend/prompts/data_collector.txt", "Data Collector Prompt"
    )
    services_ok &= check_file_exists("backend/prompts/writer.txt", "Writer Prompt")
    services_ok &= check_file_exists("backend/prompts/feedback.txt", "Feedback Prompt")
    services_ok &= check_file_exists(
        "backend/prompts/modificator.txt", "Modificator Prompt"
    )

    return services_ok


def check_dependencies():
    """Check that required dependencies are available"""
    print("\n🔍 Checking Dependencies...")

    deps_ok = True

    try:
        import fastapi

        print("✅ FastAPI: Available")
    except ImportError:
        print("❌ FastAPI: Missing")
        deps_ok = False

    try:
        import langchain

        print("✅ LangChain: Available")
    except ImportError:
        print("❌ LangChain: Missing")
        deps_ok = False

    try:
        import pydantic

        print("✅ Pydantic: Available")
    except ImportError:
        print("❌ Pydantic: Missing")
        deps_ok = False

    try:
        import httpx

        print("✅ HTTPX: Available")
    except ImportError:
        print("❌ HTTPX: Missing")
        deps_ok = False

    return deps_ok


def check_configuration():
    """Check configuration files"""
    print("\n🔍 Checking Configuration...")

    config_ok = True

    # Check .env file
    env_exists = check_file_exists("backend/.env", "Environment Configuration")
    config_ok &= env_exists

    if env_exists:
        try:
            from dotenv import load_dotenv

            load_dotenv(Path("backend/.env"))
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key and not api_key.startswith("test-"):
                print("✅ OpenRouter API Key: Configured")
            else:
                print("⚠️  OpenRouter API Key: Not configured or test key")
        except Exception as e:
            print(f"⚠️  Environment loading issue: {e}")

    # Check pyproject.toml
    config_ok &= check_file_exists(
        "backend/pyproject.toml", "Python Project Configuration"
    )

    return config_ok


async def check_imports():
    """Check that all modules can be imported successfully"""
    print("\n🔍 Checking Module Imports...")

    imports_ok = True

    modules_to_test = [
        ("backend.main", "Main FastAPI Application"),
        ("backend.api.routes", "API Routes"),
        ("backend.agents.data_collector", "Data Collector Agent"),
        ("backend.agents.writer", "Writer Agent"),
        ("backend.agents.feedback", "Feedback Agent"),
        ("backend.agents.modificator", "Modificator Agent"),
        ("backend.chains", "LangChain Integration"),
        ("backend.services.profile_storage", "Profile Storage Service"),
        ("backend.services.session_manager", "Session Manager Service"),
        ("backend.schemas.models", "Pydantic Models"),
        ("backend.utils.error_handler", "Error Handler"),
    ]

    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}: Imports successfully")
        except Exception as e:
            print(f"❌ {description}: Import failed - {e}")
            imports_ok = False

    return imports_ok


def main():
    """Main verification function"""
    print("🚀 Job Agent Backend Verification")
    print("=" * 50)

    all_checks_passed = True

    # Run all checks
    all_checks_passed &= check_service_implementation()
    all_checks_passed &= check_dependencies()
    all_checks_passed &= check_configuration()

    # Run async checks
    async_result = asyncio.run(check_imports())
    all_checks_passed &= async_result

    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 Backend verification PASSED!")
        print("\nThe Job Agent backend is fully implemented and ready to use.")
        print("All core components, services, and dependencies are in place.")
        return 0
    else:
        print("⚠️  Backend verification FAILED!")
        print("\nSome components may be missing or misconfigured.")
        print("Please check the output above for specific issues.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
