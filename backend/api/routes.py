import logging
from typing import Any, Dict, Optional

from agents.modificator import ModificatorAgent
from chains import CoverLetterWriterChain, QuestionAnswerWriterChain
from fastapi import APIRouter, BackgroundTasks, HTTPException
from loaders.job_description_loader import JobDescriptionLoader
from schemas.models import (
    CoverLetterRequest,
    CoverLetterResponse,
    ErrorResponse,
    MessageCreateRequest,
    ModificationRequest,
    ModificationResponse,
    ProfileCreateRequest,
    ProfileListResponse,
    ProfileUpdateRequest,
    QuestionAnswerRequest,
    QuestionAnswerResponse,
    SessionDataResponse,
    SessionUpdateRequest,
    StoredUserProfile,
    UserProfile,
)
from services.profile_storage import LocalProfileService, ProfileStorageService
from services.session_manager import SessionManager
from utils.error_handler import JobAgentError

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances
_cover_letter_chain = None
_question_answer_chain = None
_modificator_agent = None
_profile_storage = None
_session_manager = None
_local_profile_service = None


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


def get_profile_storage() -> ProfileStorageService:
    global _profile_storage
    if _profile_storage is None:
        _profile_storage = ProfileStorageService()
    return _profile_storage


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def get_local_profile_service() -> LocalProfileService:
    global _local_profile_service
    if _local_profile_service is None:
        _local_profile_service = LocalProfileService()
    return _local_profile_service


def get_job_loader() -> JobDescriptionLoader:
    # Job loader is stateless, so we can create a new instance each time
    # In production, this could be cached if needed
    return JobDescriptionLoader()


@router.post(
    "/generate/cover-letter",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "Cover letter generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def generate_cover_letter(
    request: CoverLetterRequest, background_tasks: BackgroundTasks
):
    """
    Generate a tailored cover letter based on job description and user profile.

    Returns cover letter, feedback suggestions, and metadata for further processing.
    """
    try:
        logger.info(
            f"Generating cover letter - URL: {request.job_description_url}, Text: {bool(request.job_description_text)}"
        )

        chain = get_cover_letter_chain()
        cover_letter, feedback, job_description, filtered_profile = (
            await chain.generate_cover_letter(request)
        )

        # Create agent steps for visualization
        agent_steps = [
            {
                "agent": "Job Description Loader",
                "status": "completed",
                "description": f"Loaded and parsed job description from {request.job_description_url or 'manual input'}",
                "result": {
                    "title": job_description.title,
                    "company": "Extracted from job posting",
                    "key_requirements": len(job_description.requirements),
                    "responsibilities": len(job_description.responsibilities),
                },
            },
            {
                "agent": "Data Collector",
                "status": "completed",
                "description": "Analyzed user profile and selected the most relevant experience for this role",
                "result": {
                    "selected_profile": filtered_profile.selected_profile_version,
                    "relevant_skills": len(filtered_profile.relevant_skills),
                    "relevant_experience": len(filtered_profile.relevant_experience),
                    "top_skills": (
                        filtered_profile.relevant_skills[:3]
                        if filtered_profile.relevant_skills
                        else []
                    ),
                    "motivational_alignment": (
                        filtered_profile.motivational_alignment[:100] + "..."
                        if len(filtered_profile.motivational_alignment) > 100
                        else filtered_profile.motivational_alignment
                    ),
                },
            },
            {
                "agent": "Writer Agent",
                "status": "completed",
                "description": "Crafted personalized content using selected profile data and job requirements",
                "result": {
                    "title": cover_letter.title,
                    "body_length": len(cover_letter.body),
                    "word_count": len(cover_letter.body.split()),
                    "key_points_used": len(cover_letter.key_points_used),
                    "key_points": (
                        cover_letter.key_points_used[:3]
                        if cover_letter.key_points_used
                        else []
                    ),
                },
            },
            {
                "agent": "Feedback Agent",
                "status": "completed",
                "description": "Analyzed content and provided specific improvement suggestions",
                "result": {
                    "feedback_items": len(feedback.feedback_items),
                    "categories": list(
                        set(item.type.value for item in feedback.feedback_items)
                    ),
                    "suggestions": [
                        {"type": item.type.value, "suggestion": item.suggestion}
                        for item in feedback.feedback_items[
                            :3
                        ]  # Show top 3 suggestions
                    ],
                },
            },
        ]

        response = {
            "cover_letter": cover_letter.dict(),
            "feedback": feedback.dict(),
            "job_summary": {
                "title": job_description.title,
                "role_summary": job_description.role_summary,
                "company_context": job_description.company_context,
            },
            "filtered_profile": filtered_profile.dict(),
            "agent_steps": agent_steps,
        }

        logger.info("Cover letter generated successfully")
        return response

    except JobAgentError as e:
        logger.warning(f"JobAgent error: {e.category} - {str(e)}")
        raise HTTPException(status_code=400, detail=e.user_message)
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating cover letter: {e}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred. Please try again."
        )


@router.post(
    "/generate/answer",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "HR question answered successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def generate_answer(
    request: QuestionAnswerRequest, background_tasks: BackgroundTasks
):
    """
    Answer an HR question based on job description and user profile.

    Returns answer, feedback suggestions, and metadata for further processing.
    """
    try:
        logger.info(f"Answering HR question for job: {request.job_description_url}")

        chain = get_question_answer_chain()
        answer, feedback, job_description, filtered_profile = (
            await chain.answer_question(request)
        )

        # Create agent steps for visualization
        agent_steps = [
            {
                "agent": "Job Description Loader",
                "status": "completed",
                "description": f"Loaded and parsed job description from {request.job_description_url or 'manual input'}",
                "result": {
                    "title": job_description.title,
                    "company": "Extracted from job posting",
                    "key_requirements": len(job_description.requirements),
                    "responsibilities": len(job_description.responsibilities),
                },
            },
            {
                "agent": "Data Collector",
                "status": "completed",
                "description": "Analyzed user profile and selected the most relevant experience for this role",
                "result": {
                    "selected_profile": filtered_profile.selected_profile_version,
                    "relevant_skills": len(filtered_profile.relevant_skills),
                    "relevant_experience": len(filtered_profile.relevant_experience),
                    "top_skills": (
                        filtered_profile.relevant_skills[:3]
                        if filtered_profile.relevant_skills
                        else []
                    ),
                    "motivational_alignment": (
                        filtered_profile.motivational_alignment[:100] + "..."
                        if len(filtered_profile.motivational_alignment) > 100
                        else filtered_profile.motivational_alignment
                    ),
                },
            },
            {
                "agent": "Writer Agent",
                "status": "completed",
                "description": "Crafted thoughtful, personalized answer based on profile and job context",
                "result": {
                    "answer_length": len(answer.answer),
                    "word_count": len(answer.answer.split()),
                    "assumptions": len(answer.assumptions),
                    "follow_up_question": answer.follow_up_question is not None,
                    "key_assumptions": (
                        answer.assumptions[:2] if answer.assumptions else []
                    ),
                },
            },
            {
                "agent": "Feedback Agent",
                "status": "completed",
                "description": "Analyzed content and provided specific improvement suggestions",
                "result": {
                    "feedback_items": len(feedback.feedback_items),
                    "categories": list(
                        set(item.type.value for item in feedback.feedback_items)
                    ),
                    "suggestions": [
                        {"type": item.type.value, "suggestion": item.suggestion}
                        for item in feedback.feedback_items[
                            :3
                        ]  # Show top 3 suggestions
                    ],
                },
            },
        ]

        response = {
            "answer": answer.dict(),
            "feedback": feedback.dict(),
            "job_summary": {
                "title": job_description.title,
                "role_summary": job_description.role_summary,
                "company_context": job_description.company_context,
            },
            "filtered_profile": filtered_profile.dict(),
            "agent_steps": agent_steps,
        }

        logger.info("HR question answered successfully")
        return response

    except JobAgentError as e:
        logger.warning(f"JobAgent error: {e.category} - {str(e)}")
        raise HTTPException(status_code=400, detail=e.user_message)
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error answering question: {e}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred. Please try again."
        )


@router.post(
    "/modify",
    response_model=ModificationResponse,
    responses={
        200: {"description": "Content modified successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
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
        from schemas.models import DataCollectorOutput, JobDescription

        # Placeholder - in real implementation, retrieve from session/cache
        job_desc = JobDescription(
            url="https://example.com/job",
            responsibilities=[],
            requirements=[],
            role_summary="Job role",
            company_context="Company context",
        )

        filtered_profile = DataCollectorOutput(
            selected_profile_version="General",
            relevant_skills=[],
            relevant_experience=[],
            relevant_education=[],
            motivational_alignment="Motivated to contribute",
        )

        agent = get_modificator_agent()
        result = await agent.apply_modifications(
            original_obj, request.selected_feedback, filtered_profile, job_desc
        )

        logger.info("Content modified successfully")
        return result

    except JobAgentError as e:
        logger.warning(f"JobAgent error: {e.category} - {str(e)}")
        raise HTTPException(status_code=400, detail=e.user_message)
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error modifying content: {e}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred. Please try again."
        )


# Profile Management Endpoints


@router.post(
    "/profiles",
    response_model=StoredUserProfile,
    responses={
        201: {"description": "Profile created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_profile(request: ProfileCreateRequest):
    """
    Create a new user profile.

    Returns the created profile with generated ID and timestamps.
    """
    try:
        logger.info(f"Creating profile: {request.name}")

        storage = get_profile_storage()
        profile = storage.create_profile(request)

        logger.info(f"Profile created successfully: {profile.id}")
        return profile

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/profiles",
    response_model=ProfileListResponse,
    responses={
        200: {"description": "Profiles retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_profiles():
    """
    Get all user profiles.

    Returns a list of all stored profiles and the default profile ID.
    """
    try:
        logger.info("Listing all profiles")

        storage = get_profile_storage()
        profiles = storage.get_all_profiles()
        default_profile = storage.get_default_profile()

        response = ProfileListResponse(
            profiles=profiles,
            default_profile_id=default_profile.id if default_profile else None,
        )

        logger.info(f"Retrieved {len(profiles)} profiles")
        return response

    except Exception as e:
        logger.error(f"Error listing profiles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/profiles/{profile_id}",
    response_model=StoredUserProfile,
    responses={
        200: {"description": "Profile retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_profile(profile_id: str):
    """
    Get a specific user profile by ID.

    Returns the profile if found.
    """
    try:
        logger.info(f"Getting profile: {profile_id}")

        storage = get_profile_storage()
        profile = storage.get_profile(profile_id)

        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        logger.info(f"Profile retrieved: {profile_id}")
        return profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/profiles/{profile_id}",
    response_model=StoredUserProfile,
    responses={
        200: {"description": "Profile updated successfully"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_profile(profile_id: str, request: ProfileUpdateRequest):
    """
    Update an existing user profile.

    Returns the updated profile.
    """
    try:
        logger.info(f"Updating profile: {profile_id}")

        storage = get_profile_storage()
        profile = storage.update_profile(profile_id, request)

        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        logger.info(f"Profile updated: {profile_id}")
        return profile

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/profiles/{profile_id}",
    responses={
        204: {"description": "Profile deleted successfully"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_profile(profile_id: str):
    """
    Delete a user profile.

    Returns 204 No Content on success.
    """
    try:
        logger.info(f"Deleting profile: {profile_id}")

        storage = get_profile_storage()
        deleted = storage.delete_profile(profile_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Profile not found")

        logger.info(f"Profile deleted: {profile_id}")
        return {"message": "Profile deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/profiles/{profile_id}/default",
    responses={
        200: {"description": "Default profile set successfully"},
        404: {"model": ErrorResponse, "description": "Profile not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def set_default_profile(profile_id: str):
    """
    Set a profile as the default profile.

    Returns success message.
    """
    try:
        logger.info(f"Setting default profile: {profile_id}")

        storage = get_profile_storage()
        success = storage.set_default_profile(profile_id)

        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")

        logger.info(f"Default profile set: {profile_id}")
        return {"message": "Default profile set successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting default profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/profiles/default",
    response_model=Optional[StoredUserProfile],
    responses={
        200: {"description": "Default profile retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_default_profile():
    """
    Get the default user profile.

    Returns the default profile if one exists, null otherwise.
    """
    try:
        logger.info("Getting default profile")

        storage = get_profile_storage()
        profile = storage.get_default_profile()

        if profile:
            logger.info(f"Default profile retrieved: {profile.id}")
        else:
            logger.info("No default profile set")

        return profile

    except Exception as e:
        logger.error(f"Error getting default profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Local Profile Storage Endpoints


@router.post(
    "/local-profile",
    response_model=Dict[str, str],
    responses={
        200: {"description": "Profile saved successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def save_local_profile(profile: UserProfile):
    """
    Save a user profile to local server storage.

    The profile will persist across server restarts and be available
    to all users of this server instance.
    """
    try:
        logger.info("Saving local profile")

        local_service = get_local_profile_service()
        local_service.save_profile(profile)

        logger.info("Local profile saved successfully")
        return {"message": "Profile saved successfully"}

    except Exception as e:
        logger.error(f"Error saving local profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/local-profile",
    response_model=UserProfile,
    responses={
        200: {"description": "Profile retrieved successfully"},
        404: {"model": ErrorResponse, "description": "No profile found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_local_profile():
    """
    Get the locally stored user profile.

    Returns the profile that was previously saved to local server storage.
    """
    try:
        logger.info("Getting local profile")

        local_service = get_local_profile_service()
        profile = local_service.load_profile()

        if profile is None:
            raise HTTPException(status_code=404, detail="No local profile found")

        logger.info("Local profile retrieved successfully")
        return profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting local profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/local-profile",
    response_model=Dict[str, str],
    responses={
        200: {"description": "Profile deleted successfully"},
        404: {"model": ErrorResponse, "description": "No profile found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_local_profile():
    """
    Delete the locally stored user profile.
    """
    try:
        logger.info("Deleting local profile")

        local_service = get_local_profile_service()
        deleted = local_service.delete_profile()

        if not deleted:
            raise HTTPException(status_code=404, detail="No local profile found")

        logger.info("Local profile deleted successfully")
        return {"message": "Profile deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting local profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# URL Validation Endpoints


@router.post(
    "/validate-url",
    response_model=Dict[str, Any],
    responses={
        200: {"description": "URL validation completed"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def validate_url(request: Dict[str, str]):
    """
    Validate a job URL and provide analysis before attempting to load job description.

    Returns validation results and platform-specific recommendations.
    """
    try:
        url = request.get("url", "").strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        logger.info(f"Validating URL: {url}")

        job_loader = get_job_loader()
        result = job_loader.validate_and_analyze_url(url)

        if not result["valid"]:
            raise HTTPException(status_code=400, detail=result["error"])

        logger.info(f"URL validation successful for: {url}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating URL: {e}")
        raise HTTPException(
            status_code=500, detail="URL validation failed. Please try again."
        )


# Session Management Endpoints


@router.post(
    "/sessions",
    response_model=SessionDataResponse,
    responses={
        201: {"description": "Session created successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_session():
    """
    Create a new chat session.

    Returns the created session data.
    """
    try:
        logger.info("Creating new session")

        session_manager = get_session_manager()
        session_data = session_manager.create_session()

        response = SessionDataResponse(
            session_id=session_data.session_id,
            current_job_url=session_data.current_job_url,
            current_profile_id=session_data.current_profile_id,
            messages=[],
            created_at=session_data.created_at,
            updated_at=session_data.updated_at,
        )

        logger.info(f"Session created: {session_data.session_id}")
        return response

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/sessions/{session_id}",
    response_model=SessionDataResponse,
    responses={
        200: {"description": "Session retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_session(session_id: str):
    """
    Get session data by ID.

    Returns the session data including chat history.
    """
    try:
        logger.info(f"Getting session: {session_id}")

        session_manager = get_session_manager()
        session_data = session_manager.get_session(session_id)

        if session_data is None:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert messages to ChatMessage objects
        messages = []
        for msg_data in session_data.messages:
            messages.append(ChatMessage(**msg_data))

        response = SessionDataResponse(
            session_id=session_data.session_id,
            current_job_url=session_data.current_job_url,
            current_profile_id=session_data.current_profile_id,
            messages=messages,
            created_at=session_data.created_at,
            updated_at=session_data.updated_at,
        )

        logger.info(f"Session retrieved: {session_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/sessions/{session_id}",
    response_model=SessionDataResponse,
    responses={
        200: {"description": "Session updated successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_session(session_id: str, request: SessionUpdateRequest):
    """
    Update session data.

    Updates current job URL and/or profile ID.
    """
    try:
        logger.info(f"Updating session: {session_id}")

        session_manager = get_session_manager()
        session_data = session_manager.get_session(session_id)

        if session_data is None:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update fields
        if request.current_job_url is not None:
            session_data.current_job_url = request.current_job_url
        if request.current_profile_id is not None:
            session_data.current_profile_id = request.current_profile_id

        updated_session = session_manager.update_session(session_data)

        # Convert messages to ChatMessage objects
        messages = []
        for msg_data in updated_session.messages:
            messages.append(ChatMessage(**msg_data))

        response = SessionDataResponse(
            session_id=updated_session.session_id,
            current_job_url=updated_session.current_job_url,
            current_profile_id=updated_session.current_profile_id,
            messages=messages,
            created_at=updated_session.created_at,
            updated_at=updated_session.updated_at,
        )

        logger.info(f"Session updated: {session_id}")
        return response

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/sessions/{session_id}/messages",
    response_model=SessionDataResponse,
    responses={
        201: {"description": "Message added successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def add_message(session_id: str, request: MessageCreateRequest):
    """
    Add a message to the session chat history.

    Returns the updated session data.
    """
    try:
        logger.info(f"Adding message to session: {session_id}")

        session_manager = get_session_manager()
        session_data = session_manager.add_message(
            session_id, request.type, request.content
        )

        if session_data is None:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert messages to ChatMessage objects
        messages = []
        for msg_data in session_data.messages:
            messages.append(ChatMessage(**msg_data))

        response = SessionDataResponse(
            session_id=session_data.session_id,
            current_job_url=session_data.current_job_url,
            current_profile_id=session_data.current_profile_id,
            messages=messages,
            created_at=session_data.created_at,
            updated_at=session_data.updated_at,
        )

        logger.info(f"Message added to session: {session_id}")
        return response

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding message to session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/sessions/{session_id}/messages",
    response_model=SessionDataResponse,
    responses={
        200: {"description": "Messages cleared successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def clear_messages(session_id: str):
    """
    Clear all messages from the session chat history.

    Returns the updated session data.
    """
    try:
        logger.info(f"Clearing messages from session: {session_id}")

        session_manager = get_session_manager()
        session_data = session_manager.clear_messages(session_id)

        if session_data is None:
            raise HTTPException(status_code=404, detail="Session not found")

        response = SessionDataResponse(
            session_id=session_data.session_id,
            current_job_url=session_data.current_job_url,
            current_profile_id=session_data.current_profile_id,
            messages=[],  # Cleared
            created_at=session_data.created_at,
            updated_at=session_data.updated_at,
        )

        logger.info(f"Messages cleared from session: {session_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing messages from session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/sessions/{session_id}",
    responses={
        204: {"description": "Session deleted successfully"},
        404: {"model": ErrorResponse, "description": "Session not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_session(session_id: str):
    """
    Delete a session and all its data.

    Returns 204 No Content on success.
    """
    try:
        logger.info(f"Deleting session: {session_id}")

        session_manager = get_session_manager()
        deleted = session_manager.delete_session(session_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Session deleted: {session_id}")
        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/sessions/cleanup",
    responses={
        200: {"description": "Session cleanup completed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def cleanup_sessions():
    """
    Clean up expired sessions.

    Returns the number of sessions cleaned up.
    """
    try:
        logger.info("Running session cleanup")

        session_manager = get_session_manager()
        cleaned_count = session_manager.cleanup_expired_sessions()

        logger.info(f"Session cleanup completed: {cleaned_count} sessions cleaned")
        return {"message": f"Cleaned up {cleaned_count} expired sessions"}

    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
