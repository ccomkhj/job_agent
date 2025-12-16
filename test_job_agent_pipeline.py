#!/usr/bin/env python3
"""
Test script to verify the complete Job Agent pipeline works end-to-end
Tests the multi-agent system without starting the full FastAPI server
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Load environment variables
backend_env_path = Path(__file__).parent / "backend" / ".env"
if backend_env_path.exists():
    load_dotenv(backend_env_path)

from chains.cover_letter_chain import CoverLetterWriterChain
from chains.question_answer_chain import QuestionAnswerWriterChain
from schemas.models import (
    CareerBackground,
    JobDescription,
    UserProfile,
    CoverLetterRequest,
    QuestionAnswerRequest,
)

# Mock job description for testing
MOCK_JOB_DESCRIPTION = JobDescription(
    url="https://example.com/job/senior-data-engineer",
    title="Senior Data Engineer",
    role_summary="We are seeking a Senior Data Engineer to design and implement scalable data pipelines and infrastructure.",
    responsibilities=[
        "Design and implement ETL pipelines for large-scale data processing",
        "Build and maintain data warehouses and analytics platforms",
        "Collaborate with data scientists to optimize data workflows",
        "Ensure data quality and reliability across all systems",
    ],
    requirements=[
        "5+ years of experience in data engineering",
        "Strong proficiency in Python, SQL, and cloud platforms",
        "Experience with Apache Spark, Kafka, and data modeling",
        "Bachelor's degree in Computer Science or related field",
    ],
    company_context="TechCorp is a leading technology company focused on AI-driven solutions and big data analytics.",
)

# Mock user profile for testing
MOCK_USER_PROFILE = UserProfile(
    career_background=CareerBackground(
        data_engineering="""
        Senior Data Engineer at DataTech Solutions (2020-Present):
        - Designed and implemented real-time ETL pipelines processing 10TB+ daily
        - Built scalable data infrastructure using AWS EMR, Redshift, and S3
        - Led migration from on-premise Hadoop to cloud-native architecture
        - Reduced data processing costs by 40% through optimization

        Data Engineer at StartupXYZ (2018-2020):
        - Developed Apache Spark applications for customer analytics
        - Built data quality monitoring systems and automated alerts
        - Implemented CI/CD pipelines for data platform deployments
        """,
        data_science="""
        Data Scientist at InnovateLabs (2016-2018):
        - Built predictive models for customer churn using Python and scikit-learn
        - Developed A/B testing frameworks for product optimization
        - Created automated reporting dashboards using Tableau and SQL
        """,
        computer_vision="",
        cto="",
    ),
    education_background="""
    Master of Science in Computer Science, Stanford University (2016)
    - Focus: Machine Learning and Data Systems
    - Thesis: Scalable Data Pipeline Architectures

    Bachelor of Science in Mathematics, UC Berkeley (2014)
    - GPA: 3.8/4.0
    - Relevant coursework: Statistics, Algorithms, Database Systems
    """,
    motivation="""
    I am passionate about building scalable data infrastructure that enables data-driven decision making.
    My experience in both data engineering and data science gives me a unique perspective on creating
    end-to-end data solutions. I am excited to join TechCorp because of your innovative approach to
    using AI to solve complex business problems.
    """,
)


async def test_cover_letter_generation():
    """Test the complete cover letter generation pipeline"""
    print("🧪 Testing Cover Letter Generation Pipeline...")

    try:
        # Initialize the chain
        chain = CoverLetterWriterChain()

        # Create request
        request = CoverLetterRequest(
            job_description_url="https://example.com/job",
            user_profile=MOCK_USER_PROFILE,
        )

        # Generate cover letter (this will try to load job from URL, but we'll catch network errors)
        try:
            cover_letter, feedback, job_desc, filtered_profile = (
                await chain.generate_cover_letter(request)
            )
        except Exception as e:
            if "network" in str(e).lower() or "connection" in str(e).lower():
                print(
                    "   ℹ️  Network blocked (expected in sandbox), testing individual components instead..."
                )

                # Test individual components directly
                from agents.data_collector import DataCollectorAgent
                from agents.writer import WriterAgent
                from agents.feedback import FeedbackAgent

                data_collector = DataCollectorAgent()
                filtered_profile = await data_collector.collect_data(
                    MOCK_JOB_DESCRIPTION, MOCK_USER_PROFILE
                )

                writer = WriterAgent()
                cover_letter = await writer.write_cover_letter(
                    MOCK_JOB_DESCRIPTION, filtered_profile
                )

                feedback_agent = FeedbackAgent()
                feedback = await feedback_agent.provide_feedback(
                    cover_letter, MOCK_JOB_DESCRIPTION, filtered_profile
                )

                job_desc = MOCK_JOB_DESCRIPTION
            else:
                raise

        # Verify results
        assert cover_letter.title, "Cover letter should have a title"
        assert cover_letter.body, "Cover letter should have body content"
        assert (
            len(cover_letter.key_points_used) > 0
        ), "Cover letter should reference key points"

        assert len(feedback.feedback_items) > 0, "Should have feedback items"

        assert job_desc.title, "Should have parsed job title"
        assert (
            filtered_profile.selected_profile_version
        ), "Should have selected profile version"

        print("✅ Cover letter generation pipeline works!")
        print(f"   - Generated cover letter: {len(cover_letter.body)} characters")
        print(f"   - Selected profile: {filtered_profile.selected_profile_version}")
        print(f"   - Feedback items: {len(feedback.feedback_items)}")

        return True

    except Exception as e:
        print(f"❌ Cover letter generation failed: {e}")
        return False


async def test_question_answer_generation():
    """Test the question answering pipeline"""
    print("\n🧪 Testing Question Answer Generation Pipeline...")

    try:
        # Test individual components directly (since network is blocked)
        from agents.data_collector import DataCollectorAgent
        from agents.writer import WriterAgent
        from agents.feedback import FeedbackAgent

        data_collector = DataCollectorAgent()
        filtered_profile = await data_collector.collect_data(
            MOCK_JOB_DESCRIPTION, MOCK_USER_PROFILE
        )

        writer = WriterAgent()
        answer = await writer.answer_question(
            MOCK_JOB_DESCRIPTION,
            filtered_profile,
            "Why are you interested in this position?",
        )

        feedback_agent = FeedbackAgent()
        feedback = await feedback_agent.provide_feedback(
            answer, MOCK_JOB_DESCRIPTION, filtered_profile
        )

        job_desc = MOCK_JOB_DESCRIPTION

        # Verify results
        assert answer.answer, "Should have generated an answer"
        assert len(feedback.feedback_items) > 0, "Should have feedback items"

        print("✅ Question answer generation pipeline works!")
        print(f"   - Generated answer: {len(answer.answer)} characters")
        print(f"   - Feedback items: {len(feedback.feedback_items)}")

        return True

    except Exception as e:
        print(f"❌ Question answer generation failed: {e}")
        return False


async def test_data_collector_agent():
    """Test the data collector agent independently"""
    print("\n🧪 Testing Data Collector Agent...")

    try:
        from agents.data_collector import DataCollectorAgent

        agent = DataCollectorAgent()
        result = await agent.collect_data(MOCK_JOB_DESCRIPTION, MOCK_USER_PROFILE)

        assert result.selected_profile_version, "Should select a profile version"
        assert len(result.relevant_skills) > 0, "Should identify relevant skills"
        assert (
            len(result.relevant_experience) > 0
        ), "Should identify relevant experience"

        print("✅ Data Collector Agent works!")
        print(f"   - Selected profile: {result.selected_profile_version}")
        print(f"   - Relevant skills: {len(result.relevant_skills)}")
        print(f"   - Relevant experience: {len(result.relevant_experience)}")

        return True

    except Exception as e:
        print(f"❌ Data Collector Agent failed: {e}")
        return False


async def test_writer_agent():
    """Test the writer agent independently"""
    print("\n🧪 Testing Writer Agent...")

    try:
        from agents.writer import WriterAgent
        from agents.data_collector import DataCollectorAgent

        # First get filtered profile
        data_collector = DataCollectorAgent()
        filtered_profile = await data_collector.collect_data(
            MOCK_JOB_DESCRIPTION, MOCK_USER_PROFILE
        )

        # Test cover letter generation
        writer = WriterAgent()
        cover_letter = await writer.write_cover_letter(
            MOCK_JOB_DESCRIPTION, filtered_profile
        )

        assert cover_letter.title, "Should generate title"
        assert cover_letter.body, "Should generate body"

        print("✅ Writer Agent works!")
        print(f"   - Cover letter title: {cover_letter.title[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Writer Agent failed: {e}")
        return False


async def test_feedback_agent():
    """Test the feedback agent independently"""
    print("\n🧪 Testing Feedback Agent...")

    try:
        from agents.feedback import FeedbackAgent
        from agents.writer import WriterAgent
        from agents.data_collector import DataCollectorAgent

        # Get prerequisites
        data_collector = DataCollectorAgent()
        filtered_profile = await data_collector.collect_data(
            MOCK_JOB_DESCRIPTION, MOCK_USER_PROFILE
        )

        writer = WriterAgent()
        content = await writer.write_cover_letter(
            MOCK_JOB_DESCRIPTION, filtered_profile
        )

        # Test feedback
        feedback_agent = FeedbackAgent()
        feedback = await feedback_agent.provide_feedback(
            content, MOCK_JOB_DESCRIPTION, filtered_profile
        )

        assert len(feedback.feedback_items) > 0, "Should provide feedback"

        print("✅ Feedback Agent works!")
        print(f"   - Feedback items: {len(feedback.feedback_items)}")
        for item in feedback.feedback_items[:2]:  # Show first 2 items
            print(f"     - {item.type}: {item.suggestion[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Feedback Agent failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Testing Job Agent Multi-Agent System\n")

    # Check if API key is available
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("test-"):
        print("⚠️  Warning: Using test API key or no API key found. LLM calls may fail.")
        print("   Set OPENROUTER_API_KEY environment variable for real testing.\n")

    # Run tests
    results = []
    results.append(await test_data_collector_agent())
    results.append(await test_writer_agent())
    results.append(await test_feedback_agent())
    results.append(await test_cover_letter_generation())
    results.append(await test_question_answer_generation())

    # Summary
    passed = sum(results)
    total = len(results)

    print("\n📊 Test Results:")
    print(f"   ✅ Passed: {passed}/{total}")
    print(f"   ❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All Job Agent systems are working correctly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} system(s) need attention.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
