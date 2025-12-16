#!/usr/bin/env python3
"""
End-to-end test script for the Job Agent system
Tests the complete user flow from job URL submission to content generation and modification
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from agents.modificator import ModificatorAgent
from chains import CoverLetterWriterChain, QuestionAnswerWriterChain
from schemas.models import (
    CareerBackground,
    CoverLetterRequest,
    JobDescription,
    QuestionAnswerRequest,
    UserProfile,
)

# Mock job description for testing
MOCK_JOB_DESCRIPTION = JobDescription(
    url="https://example.com/job/senior-data-engineer",
    title="Senior Data Engineer",
    responsibilities=[
        "Design and implement scalable data pipelines using Apache Spark and Kafka",
        "Build ETL processes for processing large datasets from multiple sources",
        "Collaborate with data scientists and analysts to optimize data workflows",
        "Optimize database performance and query efficiency for analytical workloads",
    ],
    requirements=[
        "5+ years of data engineering experience",
        "Strong proficiency in Python and SQL",
        "Experience with Apache Spark, Kafka, and cloud platforms (AWS/GCP)",
        "Bachelor's degree in Computer Science or related field",
    ],
    role_summary="We are looking for a Senior Data Engineer to join our growing data platform team. You will be responsible for building and maintaining the data infrastructure that powers our analytics, machine learning, and business intelligence systems.",
    company_context="TechCorp is a leading technology company focused on AI-driven solutions for enterprise customers. We process petabytes of data daily and are looking for engineers passionate about building scalable data systems.",
)


async def test_complete_cover_letter_flow():
    """Test the complete cover letter generation flow"""
    print("🧪 Testing Complete Cover Letter Flow")
    print("=" * 50)

    try:
        # Step 1: Create a sample user profile
        print("📝 Step 1: Creating sample user profile...")
        user_profile = UserProfile(
            career_background=CareerBackground(
                data_science="""Machine Learning Engineer with 5+ years of experience in:
                - Building and deploying ML models for recommendation systems
                - Python, TensorFlow, PyTorch, scikit-learn
                - Big data processing with Spark and Hadoop
                - A/B testing and model evaluation""",
                data_engineering="""Data Engineer with expertise in:
                - ETL pipeline development using Apache Airflow
                - Data warehousing with Redshift and Snowflake
                - SQL optimization and database design
                - Real-time data streaming with Kafka""",
                computer_vision="""Computer Vision Engineer specializing in:
                - Deep learning for image classification and object detection
                - OpenCV and TensorFlow/Keras for CV applications
                - Medical image analysis and autonomous vehicle perception""",
                cto="""Technical leadership experience:
                - Led engineering teams of 15+ developers
                - Product strategy and roadmap planning
                - Stakeholder management and cross-functional collaboration""",
            ),
            education_background="""MS in Computer Science from Stanford University
            BS in Mathematics from UC Berkeley
            Relevant coursework: Machine Learning, Data Structures, Algorithms""",
            motivation="""Passionate about using data and AI to solve complex business problems.
            Excited to work on scalable systems that impact millions of users.
            Committed to continuous learning and technical excellence.""",
        )
        print("✅ User profile created")

        # Step 2: Test the cover letter chain
        print("\n📄 Step 2: Testing cover letter generation...")
        chain = CoverLetterWriterChain()

        # Mock the job loader to return our test job description
        with patch.object(
            chain.job_loader, "load", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = MOCK_JOB_DESCRIPTION

            # Test the chain
            request = CoverLetterRequest(
                job_description_url="https://example.com/job/senior-data-engineer",
                user_profile=user_profile,
            )
            cover_letter, feedback, job_description, filtered_profile = (
                await chain.generate_cover_letter(request)
            )

            print("✅ Cover letter generated successfully")
            print(f"   Title: {cover_letter.title}")
            print(f"   Length: {len(cover_letter.body)} characters")
            print(f"   Key points used: {len(cover_letter.key_points_used)}")

            # Step 3: Test feedback generation
            print("\n💬 Step 3: Testing feedback generation...")
            print(f"   Feedback items: {len(feedback.feedback_items)}")
            if feedback.feedback_items:
                print(
                    f"   Sample feedback: {feedback.feedback_items[0].suggestion[:50]}..."
                )

            # Step 4: Test content modification
            print("\n🔄 Step 4: Testing content modification...")
            if feedback.feedback_items:
                modificator = ModificatorAgent()
                modified_content = await modificator.apply_modifications(
                    cover_letter,
                    feedback.feedback_items[:1],  # Apply just the first feedback item
                    filtered_profile,
                    MOCK_JOB_DESCRIPTION,
                )
                print("✅ Content modification successful")
                print(f"   Original length: {len(cover_letter.body)}")
                print(
                    f"   Modified length: {len(modified_content.modified_output.body)}"
                )

        print("\n🎉 Cover letter flow test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Cover letter flow test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_question_answer_flow():
    """Test the HR question answering flow"""
    print("\n🧪 Testing HR Question Answer Flow")
    print("=" * 50)

    try:
        # Step 1: Create sample user profile (reuse from above)
        user_profile = UserProfile(
            career_background=CareerBackground(
                data_science="""Data Scientist with expertise in predictive modeling,
                statistical analysis, and machine learning algorithms.""",
                data_engineering="""ETL pipeline development, data warehousing,
                and real-time streaming architectures.""",
                computer_vision="""Image processing, deep learning for computer vision,
                and autonomous systems development.""",
                cto="""Technical leadership, team management,
                and strategic technology planning.""",
            ),
            education_background="MS in Computer Science",
            motivation="Passionate about data-driven solutions",
        )

        # Step 2: Test question answering
        print("❓ Step 2: Testing HR question answering...")
        chain = QuestionAnswerWriterChain()

        hr_question = "Why are you interested in this position?"

        # Mock the job loader
        with patch.object(
            chain.job_loader, "load", new_callable=AsyncMock
        ) as mock_load:
            mock_load.return_value = MOCK_JOB_DESCRIPTION

            # Test the chain
            request = QuestionAnswerRequest(
                job_description_url="https://example.com/job/data-scientist",
                hr_question=hr_question,
                user_profile=user_profile,
            )
            answer, feedback, job_description, filtered_profile = (
                await chain.answer_question(request)
            )

            print("✅ HR question answered successfully")
            print(f"   Question: {hr_question}")
            print(f"   Answer length: {len(answer.answer)} characters")

            if answer.follow_up_question:
                print(f"   Follow-up question: {answer.follow_up_question}")

        print("\n🎉 Question answer flow test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Question answer flow test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)

    try:
        print("🚨 Step 1: Testing invalid job URL...")
        chain = CoverLetterWriterChain()

        # Test with invalid data
        try:
            invalid_request = CoverLetterRequest(
                job_description_url="invalid-url",
                user_profile=user_profile,  # Valid profile, invalid URL
            )
            await chain.generate_cover_letter(invalid_request)
            print("❌ Should have failed with invalid URL")
            return False
        except Exception as e:
            print(f"✅ Correctly handled invalid URL: {type(e).__name__}")

        print("\n🎉 Error handling test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error handling test failed: {e}")
        return False


async def main():
    """Run all end-to-end tests"""
    print("🚀 Starting Job Agent End-to-End Tests")
    print("=" * 60)

    results = []

    # Test cover letter flow
    results.append(await test_complete_cover_letter_flow())

    # Test question answer flow
    results.append(await test_question_answer_flow())

    # Test error handling
    results.append(await test_error_handling())

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All tests passed! The Job Agent system is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. System needs additional work.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

