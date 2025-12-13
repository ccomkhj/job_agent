import logging
from typing import Tuple

from schemas.models import (
    JobDescription,
    UserProfile,
    CoverLetterRequest,
    CoverLetterResponse,
    FeedbackResponse,
    DataCollectorOutput
)
from agents.data_collector import DataCollectorAgent
from agents.writer import WriterAgent
from agents.feedback import FeedbackAgent
from loaders.job_description_loader import JobDescriptionLoader
from utils.profile_normalizer import ProfileNormalizer

logger = logging.getLogger(__name__)


class CoverLetterWriterChain:
    """Chain that orchestrates the cover letter generation pipeline"""

    def __init__(self):
        self.job_loader = JobDescriptionLoader()
        self.profile_normalizer = ProfileNormalizer()
        self.data_collector = DataCollectorAgent()
        self.writer = WriterAgent()
        self.feedback_agent = FeedbackAgent()

    async def generate_cover_letter(self, request: CoverLetterRequest) -> Tuple[CoverLetterResponse, FeedbackResponse, JobDescription, DataCollectorOutput]:
        """
        Generate a cover letter with feedback.

        Args:
            request: Cover letter generation request

        Returns:
            Tuple of (cover_letter, feedback, job_description, filtered_profile)
        """
        try:
            # Step 1: Load and parse job description
            logger.info(f"Loading job description from {request.job_description_url}")
            job_description = await self.job_loader.load(str(request.job_description_url))

            # Step 2: Normalize user profile
            logger.info("Normalizing user profile")
            normalized_profile = self.profile_normalizer.normalize(request.user_profile.dict())

            # Step 3: Collect relevant profile data
            logger.info("Collecting relevant profile data")
            filtered_profile = await self.data_collector.collect_data(job_description, normalized_profile)

            # Step 4: Generate cover letter
            logger.info("Generating cover letter")
            cover_letter = await self.writer.write_cover_letter(job_description, filtered_profile)

            # Step 5: Generate feedback
            logger.info("Generating feedback")
            feedback = await self.feedback_agent.provide_feedback(cover_letter, job_description, filtered_profile)

            return cover_letter, feedback, job_description, filtered_profile

        except Exception as e:
            logger.error(f"Error in cover letter generation chain: {e}")
            raise
