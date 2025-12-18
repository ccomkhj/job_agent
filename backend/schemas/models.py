from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl
from pydantic.root_model import RootModel


class CareerStory(BaseModel):
    """Individual career story with achievement, education, and motivation"""

    initiator: Optional[str] = None
    achievement_sample: Optional[str] = None
    education_profile: Optional[str] = None
    motivation_goals: Optional[str] = None


class CareerBackground(BaseModel):
    """Career background with multiple career categories"""

    careers: Dict[str, CareerStory] = Field(default_factory=dict)


class UserProfile(BaseModel):
    """User profile with multiple career variants"""

    career_background: CareerBackground
    education_background: str = ""
    motivation: str = ""


class JobDescription(BaseModel):
    """Parsed job description data"""

    url: str  # Can be URL or "manual" for manual descriptions
    title: Optional[str] = None
    responsibilities: List[str]
    requirements: List[str]
    role_summary: str
    company_context: str


class DataCollectorOutput(BaseModel):
    """Output from Data Collector Agent"""

    selected_profile_version: str = Field(
        ..., description="Selected career variant (e.g., 'Data Engineer')"
    )
    relevant_skills: List[str] = Field(
        default_factory=list, description="Relevant skills for this job"
    )
    relevant_experience: List[str] = Field(
        default_factory=list, description="Relevant experience items"
    )
    relevant_education: List[str] = Field(
        default_factory=list, description="Relevant education items"
    )
    motivational_alignment: str = Field(
        ..., description="How motivation aligns with job"
    )
    content_guidance: str = Field(
        default="",
        description="Content guidance for the selected profile variant to enforce tone/angle",
    )


class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter"""

    job_description_url: Optional[str] = None
    job_description_text: Optional[str] = None
    user_profile: UserProfile


class CoverLetterResponse(BaseModel):
    """Response containing generated cover letter"""

    title: str = Field(..., description="Cover letter title")
    body: str = Field(..., description="Full cover letter text")
    key_points_used: List[str] = Field(
        ..., description="Key points from profile that were used"
    )


class QuestionAnswerRequest(BaseModel):
    """Request to answer an HR question"""

    job_description_url: Optional[str] = None
    job_description_text: Optional[str] = None
    hr_question: str
    user_profile: UserProfile


class QuestionAnswerResponse(BaseModel):
    """Response containing HR question answer"""

    answer: str
    assumptions: List[str] = Field(
        default_factory=list, description="Any assumptions made in the answer"
    )
    follow_up_question: Optional[str] = Field(
        None, description="Clarification question if needed"
    )


class FeedbackType(str, Enum):
    """Types of feedback"""

    TONE = "tone"
    ALIGNMENT = "alignment"
    CLARITY = "clarity"
    EMPHASIS = "emphasis"
    STRUCTURE = "structure"


class FeedbackItem(BaseModel):
    """Individual feedback item"""

    type: FeedbackType
    suggestion: str


class FeedbackRequest(BaseModel):
    """Request to generate feedback on output"""

    output: Dict[str, Any] = Field(..., description="The output to provide feedback on")
    output_type: str = Field(
        ..., description="Type of output: 'cover_letter' or 'question_answer'"
    )


class FeedbackResponse(BaseModel):
    """Response containing feedback suggestions"""

    feedback_items: List[FeedbackItem] = Field(default_factory=list)


class ModificationRequest(BaseModel):
    """Request to modify output based on selected feedback"""

    original_output: Dict[str, Any] = Field(
        ..., description="Original output to modify"
    )
    selected_feedback: List[FeedbackItem] = Field(
        ..., description="Selected feedback items to apply"
    )
    output_type: str = Field(
        ..., description="Type of output: 'cover_letter' or 'question_answer'"
    )


class ModificationResponse(BaseModel):
    """Response containing modified output"""

    modified_output: Union[
        CoverLetterResponse, QuestionAnswerResponse, Dict[str, Any]
    ] = Field(..., description="The modified output")


# Session management models
class MessageType(str, Enum):
    """Message types for chat"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message structure"""

    id: str
    type: str  # 'user', 'assistant', 'system'
    content: Any
    timestamp: datetime


class SessionDataResponse(BaseModel):
    """Session data response"""

    session_id: str
    current_job_url: Optional[str] = None
    current_profile_id: Optional[str] = None
    messages: List[ChatMessage] = []
    created_at: datetime
    updated_at: datetime


class SessionUpdateRequest(BaseModel):
    """Request to update session data"""

    current_job_url: Optional[str] = None
    current_profile_id: Optional[str] = None


class MessageCreateRequest(BaseModel):
    """Request to add a message to session"""

    type: str
    content: Any


# Profile storage models
class StoredUserProfile(BaseModel):
    """Stored user profile with metadata"""

    id: str = Field(..., description="Unique profile identifier")
    name: str = Field(..., description="Profile display name")
    user_profile: UserProfile
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_default: bool = Field(
        default=False, description="Whether this is the default profile"
    )


class ProfileCreateRequest(BaseModel):
    """Request to create a new profile"""

    name: str
    user_profile: UserProfile
    is_default: bool = False


class ProfileUpdateRequest(BaseModel):
    """Request to update an existing profile"""

    name: Optional[str] = None
    user_profile: Optional[UserProfile] = None
    is_default: Optional[bool] = None


class ProfileListResponse(BaseModel):
    """Response containing list of user profiles"""

    profiles: List[StoredUserProfile]
    default_profile_id: Optional[str] = None


# Error response models
class ErrorResponse(BaseModel):
    """Standard error response"""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
