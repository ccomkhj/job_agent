from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from schemas.models import (
    CoverLetterRequest,
    CoverLetterResponse,
    QuestionAnswerRequest,
    QuestionAnswerResponse,
    ModificationRequest,
    ModificationResponse,
    ErrorResponse
)
from chains import CoverLetterWriterChain, QuestionAnswerWriterChain
from agents.modificator import ModificatorAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# Global chain instances
_cover_letter_chain = None
_question_answer_chain = None
_modificator_agent = None

def get_cover_letter_chain() -> CoverLetterWriterChain:
    global _cover_letter_chain
    if _cover_letter_chain is None:
        _cover_letter_chain = CoverLetterWriterChain()
    return _cover_letter_chain

def get_question_answer_chain() -> QuestionAnswerWriterChain:
    global _question_answer_chain
    if _question_answer_chain is None:
        _question_answer_chain = QuestionAnswerWriterChain()
    return _question_answer_chain

def get_modificator_agent() -> ModificatorAgent:
    global _modificator_agent
    if _modificator_agent is None:
        _modificator_agent = ModificatorAgent()
    return _modificator_agent


@router.post(
    "/generate/cover-letter",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Cover letter generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def generate_cover_letter(request: CoverLetterRequest, background_tasks: BackgroundTasks):
    """
    Generate a tailored cover letter based on job description and user profile.

    Returns cover letter, feedback suggestions, and metadata for further processing.
    """
    try:
        logger.info(f"Generating cover letter for job: {request.job_description_url}")

        chain = get_cover_letter_chain()
        cover_letter, feedback, job_description, filtered_profile = await chain.generate_cover_letter(request)

        response = {
            "cover_letter": cover_letter.dict(),
            "feedback": feedback.dict(),
            "job_summary": {
                "title": job_description.title,
                "role_summary": job_description.role_summary,
                "company_context": job_description.company_context
            },
            "filtered_profile": filtered_profile.dict()
        }

        logger.info("Cover letter generated successfully")
        return response

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/generate/answer",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "HR question answered successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def generate_answer(request: QuestionAnswerRequest, background_tasks: BackgroundTasks):
    """
    Answer an HR question based on job description and user profile.

    Returns answer, feedback suggestions, and metadata for further processing.
    """
    try:
        logger.info(f"Answering HR question for job: {request.job_description_url}")

        chain = get_question_answer_chain()
        answer, feedback, job_description, filtered_profile = await chain.answer_question(request)

        response = {
            "answer": answer.dict(),
            "feedback": feedback.dict(),
            "job_summary": {
                "title": job_description.title,
                "role_summary": job_description.role_summary,
                "company_context": job_description.company_context
            },
            "filtered_profile": filtered_profile.dict()
        }

        logger.info("HR question answered successfully")
        return response

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/modify",
    response_model=ModificationResponse,
    responses={
        200: {"description": "Content modified successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def modify_output(request: ModificationRequest):
    """
    Apply selected feedback to modify the generated output.

    Returns the modified content.
    """
    try:
        logger.info(f"Applying {len(request.selected_feedback)} feedback items")

        # Reconstruct the original content object
        original_content = request.original_output
        content_type = request.output_type

        # Convert dict back to appropriate model
        if content_type == "cover_letter":
            from schemas.models import CoverLetterResponse
            original_obj = CoverLetterResponse(**original_content)
        elif content_type == "question_answer":
            from schemas.models import QuestionAnswerResponse
            original_obj = QuestionAnswerResponse(**original_content)
        else:
            raise ValueError(f"Unknown output type: {content_type}")

        # We need job description and filtered profile for context
        # For now, we'll use minimal context - in a full implementation,
        # these would be stored/retrieved from session state
        from schemas.models import JobDescription, DataCollectorOutput

        # Placeholder - in real implementation, retrieve from session/cache
        job_desc = JobDescription(
            url="https://example.com/job",
            responsibilities=[],
            requirements=[],
            role_summary="Job role",
            company_context="Company context"
        )

        filtered_profile = DataCollectorOutput(
            selected_profile_version="General",
            relevant_skills=[],
            relevant_experience=[],
            relevant_education=[],
            motivational_alignment="Motivated to contribute"
        )

        agent = get_modificator_agent()
        result = await agent.apply_modifications(
            original_obj,
            request.selected_feedback,
            filtered_profile,
            job_desc
        )

        logger.info("Content modified successfully")
        return result

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error modifying content: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
