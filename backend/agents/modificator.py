import json
import logging
from typing import Any, Dict, Union

from chains import get_llm, load_prompt_template
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from schemas.models import (
    CoverLetterResponse,
    DataCollectorOutput,
    FeedbackItem,
    JobDescription,
    ModificationResponse,
    QuestionAnswerResponse,
)

logger = logging.getLogger(__name__)


class ModificatorAgent:
    """Agent responsible for applying user-selected feedback to modify generated content"""

    def __init__(self):
        self.output_parser = JsonOutputParser()
        self._chain = None

    @property
    def chain(self):
        """Lazy-load the LangChain chain"""
        if self._chain is None:
            llm = get_llm()
            prompt_text = load_prompt_template("modificator")
            prompt = PromptTemplate(
                template=prompt_text,
                input_variables=[
                    "original_content",
                    "selected_feedback",
                    "filtered_profile",
                    "job_description",
                ],
            )
            self._chain = prompt | llm | self.output_parser
        return self._chain

    async def apply_modifications(
        self,
        original_content: Union[CoverLetterResponse, QuestionAnswerResponse],
        selected_feedback: list[FeedbackItem],
        filtered_profile: DataCollectorOutput,
        job_description: JobDescription,
    ) -> ModificationResponse:
        """
        Apply selected feedback to modify the original content.

        Args:
            original_content: The original generated content
            selected_feedback: List of feedback items selected by user
            filtered_profile: Job-specific profile data
            job_description: Parsed job description

        Returns:
            ModificationResponse: Modified content
        """
        try:
            logger.info(
                f"Starting modification with {len(selected_feedback)} feedback items"
            )
            logger.info(f"Original content type: {type(original_content)}")

            # Format inputs for the prompt
            content_text = self._format_original_content(original_content)
            feedback_text = self._format_selected_feedback(selected_feedback)
            profile_text = self._format_filtered_profile(filtered_profile)
            job_desc_text = self._format_job_description(job_description)

            logger.info(f"Formatted feedback: {feedback_text[:200]}...")

            # Run the chain
            result = await self.chain.ainvoke(
                {
                    "original_content": content_text,
                    "selected_feedback": feedback_text,
                    "filtered_profile": profile_text,
                    "job_description": job_desc_text,
                }
            )

            logger.info(f"Modificator received result: {result}")

            # Determine the output type and validate
            if isinstance(original_content, CoverLetterResponse):
                # Should return CoverLetterResponse format
                validated_result = CoverLetterResponse(**result)
                logger.info(f"Created modified cover letter: {validated_result.title}")
                logger.info(
                    f"Original body length: {len(original_content.body)}, Modified body length: {len(validated_result.body)}"
                )
                if original_content.body == validated_result.body:
                    logger.warning(
                        "WARNING: Modified content is identical to original!"
                    )
            elif isinstance(original_content, QuestionAnswerResponse):
                # Should return QuestionAnswerResponse format
                validated_result = QuestionAnswerResponse(**result)
                logger.info(
                    f"Created modified answer: {validated_result.answer[:100]}..."
                )
                if original_content.answer == validated_result.answer:
                    logger.warning("WARNING: Modified answer is identical to original!")
            else:
                # Fallback
                validated_result = result
                logger.info(f"Using fallback result: {validated_result}")

            return ModificationResponse(modified_output=validated_result)

        except Exception as e:
            logger.error(f"Error applying modifications: {e}")
            # Return original content as fallback
            return ModificationResponse(modified_output=original_content)

    def _format_original_content(
        self, content: Union[CoverLetterResponse, QuestionAnswerResponse]
    ) -> str:
        """Format original content for the prompt"""
        if isinstance(content, CoverLetterResponse):
            return f"""Cover Letter:

Title: {content.title}

Body:
{content.body}

Key Points Used:
{chr(10).join(f"- {point}" for point in content.key_points_used)}"""

        elif isinstance(content, QuestionAnswerResponse):
            formatted = f"""HR Question Answer:

Answer: {content.answer}
"""

            if content.assumptions:
                formatted += f"""
Assumptions:
{chr(10).join(f"- {assumption}" for assumption in content.assumptions)}"""

            if content.follow_up_question:
                formatted += f"""
Follow-up Question: {content.follow_up_question}"""

            return formatted

        else:
            return str(content)

    def _format_selected_feedback(self, feedback_items: list[FeedbackItem]) -> str:
        """Format selected feedback items for the prompt"""
        if not feedback_items:
            return "No feedback selected for application."

        formatted_items = []
        for i, item in enumerate(feedback_items, 1):
            formatted_items.append(f"{i}. {item.type.title()}: {item.suggestion}")

        return "Selected Feedback to Apply:\n" + "\n".join(formatted_items)

    def _format_filtered_profile(self, filtered_profile: DataCollectorOutput) -> str:
        """Format filtered profile data for the prompt"""
        sections = []

        sections.append(
            f"Selected Profile Version: {filtered_profile.selected_profile_version}"
        )

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
