import json
import logging
from typing import Any, Dict

from chains import get_llm, load_prompt_template
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from schemas.models import DataCollectorOutput, JobDescription, UserProfile
from utils.profile_normalizer import ProfileNormalizer

logger = logging.getLogger(__name__)


class DataCollectorAgent:
    """Agent responsible for analyzing job descriptions and selecting relevant profile data"""

    def __init__(self):
        self.profile_normalizer = ProfileNormalizer()
        self.output_parser = JsonOutputParser(pydantic_object=DataCollectorOutput)
        self._chain = None

    @property
    def chain(self):
        """Lazy-load the LangChain chain"""
        if self._chain is None:
            llm = get_llm()
            prompt_text = load_prompt_template("data_collector")
            prompt = PromptTemplate(
                template=prompt_text,
                input_variables=["job_description", "user_profile"],
            )
            self._chain = prompt | llm | self.output_parser
        return self._chain

    async def collect_data(
        self, job_description: JobDescription, user_profile: UserProfile
    ) -> DataCollectorOutput:
        """
        Analyze job description and select the most relevant profile data.

        Args:
            job_description: Parsed job description
            user_profile: Normalized user profile with career variants

        Returns:
            DataCollectorOutput: Filtered profile data relevant to the job
        """
        try:
            # Convert inputs to strings for the prompt
            job_desc_text = self._format_job_description(job_description)
            profile_text = self._format_user_profile(user_profile)

            logger.info("Data Collector processing job")
            if "CONTENT GUIDANCE" in profile_text:
                logger.info("Data Collector: CONTENT GUIDANCE included in profile text")
            else:
                logger.info("Data Collector: No CONTENT GUIDANCE in profile text")

            # Run the chain
            result = await self.chain.ainvoke(
                {"job_description": job_desc_text, "user_profile": profile_text}
            )

            # Validate and return structured output
            return DataCollectorOutput(**result)

        except Exception as e:
            logger.error(f"Error in data collection: {e}")
            # Return a minimal valid response as fallback
            return DataCollectorOutput(
                selected_profile_version="General",
                relevant_skills=[],
                relevant_experience=[],
                relevant_education=[],
                motivational_alignment="Seeking to apply skills to this role.",
            )

    def _format_job_description(self, job_desc: JobDescription) -> str:
        """Format job description for the prompt"""
        sections = []

        if job_desc.title:
            sections.append(f"Title: {job_desc.title}")

        sections.append(f"Role Summary: {job_desc.role_summary}")

        if job_desc.responsibilities:
            sections.append("Responsibilities:")
            for resp in job_desc.responsibilities[:5]:  # Limit to top 5
                sections.append(f"- {resp}")

        if job_desc.requirements:
            sections.append("Requirements:")
            for req in job_desc.requirements[:5]:  # Limit to top 5
                sections.append(f"- {req}")

        sections.append(f"Company Context: {job_desc.company_context}")

        return "\n\n".join(sections)

    def _format_user_profile(self, profile: UserProfile) -> str:
        """Format user profile for the prompt"""
        sections = []

        sections.append("Education Background:")
        sections.append(profile.education_background)

        sections.append("\nMotivation:")
        sections.append(profile.motivation)

        sections.append("\nCareer Background Variants:")

        # Handle dynamic career categories
        career_categories = profile.career_background.careers

        for category_name, career_story in career_categories.items():
            if career_story:
                sections.append(f"\n{category_name}:")
                if career_story.initiator:
                    sections.append(f"  CONTENT GUIDANCE: {career_story.initiator}")
                    sections.append(
                        f"  IMPORTANT: Follow this guidance when generating content for {category_name}"
                    )
                if career_story.achievement_sample:
                    sections.append(
                        f"  Achievements: {career_story.achievement_sample}"
                    )
                if career_story.education_profile:
                    sections.append(f"  Education: {career_story.education_profile}")
                if career_story.motivation_goals:
                    sections.append(f"  Motivation: {career_story.motivation_goals}")
            else:
                sections.append(f"\n{category_name}: Not provided")

        return "\n".join(sections)
