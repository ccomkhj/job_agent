import json
import logging
from typing import Any, Dict, Union

from chains import get_llm, load_prompt_template
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from schemas.models import (
    CoverLetterResponse,
    DataCollectorOutput,
    JobDescription,
    QuestionAnswerResponse,
)
from utils.error_handler import LLMError, handle_llm_errors

logger = logging.getLogger(__name__)


class WriterAgent:
    """Agent responsible for generating cover letters and answering HR questions"""

    def __init__(self):
        self._cover_letter_chain = None
        self._question_answer_chain = None

    def _build_chain(self, output_model):
        """Create a chain with format instructions for the target output model"""
        llm = get_llm()
        parser = JsonOutputParser(pydantic_object=output_model)
        prompt_text = load_prompt_template("writer")
        prompt = PromptTemplate(
            template=prompt_text,
            input_variables=[
                "filtered_profile",
                "job_description",
                "task_type",
                "additional_context",
            ],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        return prompt | llm | parser

    @property
    def cover_letter_chain(self):
        """Lazy-load chain for cover letters"""
        if self._cover_letter_chain is None:
            self._cover_letter_chain = self._build_chain(CoverLetterResponse)
        return self._cover_letter_chain

    @property
    def question_answer_chain(self):
        """Lazy-load chain for HR questions"""
        if self._question_answer_chain is None:
            self._question_answer_chain = self._build_chain(QuestionAnswerResponse)
        return self._question_answer_chain

    @handle_llm_errors
    async def write_cover_letter(
        self, job_description: JobDescription, filtered_profile: DataCollectorOutput
    ) -> CoverLetterResponse:
        """
        Generate a tailored cover letter.

        Args:
            job_description: Parsed job description
            filtered_profile: Job-specific profile data from Data Collector

        Returns:
            CoverLetterResponse: Generated cover letter
        """
        try:
            # Format inputs for the prompt
            profile_text = self._format_filtered_profile(filtered_profile)
            job_desc_text = self._format_job_description(job_description)

            logger.info(f"Writer generating cover letter")
            if "CONTENT GUIDANCE" in profile_text:
                logger.info("CONTENT GUIDANCE found in profile text")
                # Show the guidance section
                for line in profile_text.split("\n"):
                    if "CONTENT GUIDANCE" in line:
                        logger.info(f"Guidance line: {line}")
            else:
                logger.info("No CONTENT GUIDANCE found in profile text")

            logger.info(f"Profile text preview: {profile_text[:500]}...")

            # Run the chain
            result = await self.cover_letter_chain.ainvoke(
                {
                    "filtered_profile": profile_text,
                    "job_description": job_desc_text,
                    "task_type": "cover_letter",
                    "additional_context": "",
                }
            )

            # Validate and return structured output
            return CoverLetterResponse(**result)

        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            # Return a minimal valid response as fallback
            return CoverLetterResponse(
                title="Cover Letter",
                body="I am writing to express my interest in this position. Please see my resume for details of my qualifications.",
                key_points_used=[],
            )

    @handle_llm_errors
    async def answer_question(
        self,
        job_description: JobDescription,
        filtered_profile: DataCollectorOutput,
        question: str,
    ) -> QuestionAnswerResponse:
        """
        Answer an HR question.

        Args:
            job_description: Parsed job description
            filtered_profile: Job-specific profile data from Data Collector
            question: The HR question to answer

        Returns:
            QuestionAnswerResponse: Generated answer
        """
        try:
            # Format inputs for the prompt
            profile_text = self._format_filtered_profile(filtered_profile)
            job_desc_text = self._format_job_description(job_description)

            # Run the chain
            result = await self.question_answer_chain.ainvoke(
                {
                    "filtered_profile": profile_text,
                    "job_description": job_desc_text,
                    "task_type": "question_answer",
                    "additional_context": f"HR Question: {question}",
                }
            )

            # Validate and return structured output
            return QuestionAnswerResponse(**result)

        except Exception as e:
            logger.error(f"Error answering question: {e}")
            # Return a minimal valid response as fallback
            return QuestionAnswerResponse(
                answer="I don't have sufficient information to answer this question based on my provided profile.",
                assumptions=[],
                follow_up_question="Could you please provide more context about what specific information you're looking for?",
            )

    def _format_filtered_profile(self, filtered_profile: DataCollectorOutput) -> str:
        """Format filtered profile data for the prompt"""
        sections = []

        sections.append(
            f"Selected Profile Version: {filtered_profile.selected_profile_version}"
        )

        if filtered_profile.content_guidance:
            sections.append("Content Guidance (must follow):")
            sections.append(filtered_profile.content_guidance)

        if filtered_profile.relevant_skills:
            sections.append("Relevant Skills:")
            for skill in filtered_profile.relevant_skills:
                sections.append(f"- {skill}")

        if filtered_profile.relevant_experience:
            sections.append("Relevant Experience:")
            for exp in filtered_profile.relevant_experience:
                sections.append(f"- {exp}")

        if filtered_profile.relevant_education:
            sections.append("Relevant Education:")
            for edu in filtered_profile.relevant_education:
                sections.append(f"- {edu}")

        sections.append(
            f"Motivational Alignment: {filtered_profile.motivational_alignment}"
        )

        return "\n\n".join(sections)

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
