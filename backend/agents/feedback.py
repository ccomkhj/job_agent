import json
import logging
from typing import Dict, Any, Union

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from chains import get_llm, load_prompt_template
from schemas.models import (
    JobDescription,
    DataCollectorOutput,
    CoverLetterResponse,
    QuestionAnswerResponse,
    FeedbackResponse
)

logger = logging.getLogger(__name__)


class FeedbackAgent:
    """Agent responsible for reviewing generated content and providing feedback"""

    def __init__(self):
        self.output_parser = JsonOutputParser(pydantic_object=FeedbackResponse)
        self._chain = None

    @property
    def chain(self):
        """Lazy-load the LangChain chain"""
        if self._chain is None:
            llm = get_llm()
            prompt_text = load_prompt_template("feedback")
            prompt = PromptTemplate(
                template=prompt_text,
                input_variables=["generated_content", "job_description", "filtered_profile"],
            )
            self._chain = prompt | llm | self.output_parser
        return self._chain

    async def provide_feedback(
        self,
        generated_content: Union[CoverLetterResponse, QuestionAnswerResponse],
        job_description: JobDescription,
        filtered_profile: DataCollectorOutput
    ) -> FeedbackResponse:
        """
        Review generated content and provide constructive feedback.

        Args:
            generated_content: The generated cover letter or question answer
            job_description: Parsed job description
            filtered_profile: Job-specific profile data

        Returns:
            FeedbackResponse: List of feedback suggestions
        """
        try:
            # Format inputs for the prompt
            content_text = self._format_generated_content(generated_content)
            job_desc_text = self._format_job_description(job_description)
            profile_text = self._format_filtered_profile(filtered_profile)

            # Run the chain
            result = await self.chain.ainvoke({
                "generated_content": content_text,
                "job_description": job_desc_text,
                "filtered_profile": profile_text
            })

            # Validate and return structured output
            return FeedbackResponse(**result)

        except Exception as e:
            logger.error(f"Error providing feedback: {e}")
            # Return a minimal valid response as fallback
            return FeedbackResponse(feedback_items=[])

    def _format_generated_content(self, content: Union[CoverLetterResponse, QuestionAnswerResponse]) -> str:
        """Format generated content for the prompt"""
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

    def _format_filtered_profile(self, filtered_profile: DataCollectorOutput) -> str:
        """Format filtered profile data for the prompt"""
        sections = []

        sections.append(f"Selected Profile Version: {filtered_profile.selected_profile_version}")

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

        sections.append(f"Motivational Alignment: {filtered_profile.motivational_alignment}")

        return "\n\n".join(sections)
