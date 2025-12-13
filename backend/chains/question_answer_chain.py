import logging
from typing import Tuple

from schemas.models import (
    JobDescription,
    UserProfile,
    QuestionAnswerRequest,
    QuestionAnswerResponse,
    FeedbackResponse,
    DataCollectorOutput
)
from agents.data_collector import DataCollectorAgent
from agents.writer import WriterAgent
from agents.feedback import FeedbackAgent
from loaders.job_description_loader import JobDescriptionLoader
from utils.profile_normalizer import ProfileNormalizer

logger = logging.getLogger(__name__)


class QuestionAnswerWriterChain:
    """Chain that orchestrates the HR question answering pipeline"""

    def __init__(self):
        self.job_loader = JobDescriptionLoader()
        self.profile_normalizer = ProfileNormalizer()
        self.data_collector = DataCollectorAgent()
        self.writer = WriterAgent()
        self.feedback_agent = FeedbackAgent()

    async def answer_question(self, request: QuestionAnswerRequest) -> Tuple[QuestionAnswerResponse, FeedbackResponse, JobDescription, DataCollectorOutput]:
        """
        Answer an HR question with feedback.

        Args:
            request: Question answer request

        Returns:
            Tuple of (answer, feedback, job_description, filtered_profile)
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

            # Step 4: Generate answer
            logger.info("Generating answer to HR question")
            answer = await self.writer.answer_question(job_description, filtered_profile, request.hr_question)

            # Step 5: Generate feedback
            logger.info("Generating feedback")
            feedback = await self.feedback_agent.provide_feedback(answer, job_description, filtered_profile)

            return answer, feedback, job_description, filtered_profile

        except Exception as e:
            logger.error(f"Error in question answer chain: {e}")
            raise
