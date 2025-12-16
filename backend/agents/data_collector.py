import json
import logging
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from chains import get_llm, load_prompt_template
from schemas.models import JobDescription, UserProfile, DataCollectorOutput
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

    async def collect_data(self, job_description: JobDescription, user_profile: UserProfile) -> DataCollectorOutput:
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

            # Run the chain
            result = await self.chain.ainvoke({
                "job_description": job_desc_text,
                "user_profile": profile_text
            })

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
                motivational_alignment="Seeking to apply skills to this role."
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

        career_variants = {
            "Data Science": profile.career_background.data_science,
            "Data Engineering": profile.career_background.data_engineering,
            "Computer Vision": profile.career_background.computer_vision,
            "CTO/Technical Leadership": profile.career_background.cto
        }

        for variant_name, content in career_variants.items():
            if content:
                sections.append(f"\n{variant_name}:")
                sections.append(content)
            else:
                sections.append(f"\n{variant_name}: Not provided")

        return "\n".join(sections)
