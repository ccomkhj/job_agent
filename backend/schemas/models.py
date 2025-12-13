from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Optional, Any
from enum import Enum


class CareerBackground(BaseModel):
    """Career background with multiple variants per user"""
    data_science: Optional[str] = None
    data_engineering: Optional[str] = None
    computer_vision: Optional[str] = None
    cto: Optional[str] = None


class UserProfile(BaseModel):
    """User profile with multiple career variants"""
    career_background: CareerBackground
    education_background: str
    motivation: str


class JobDescription(BaseModel):
    """Parsed job description data"""
    url: HttpUrl
    title: Optional[str] = None
    responsibilities: List[str]
    requirements: List[str]
    role_summary: str
    company_context: str


class DataCollectorOutput(BaseModel):
    """Output from Data Collector Agent"""
    selected_profile_version: str = Field(..., description="Selected career variant (e.g., 'Data Engineer')")
    relevant_skills: List[str] = Field(default_factory=list, description="Relevant skills for this job")
    relevant_experience: List[str] = Field(default_factory=list, description="Relevant experience items")
    relevant_education: List[str] = Field(default_factory=list, description="Relevant education items")
    motivational_alignment: str = Field(..., description="How motivation aligns with job")


class CoverLetterRequest(BaseModel):
    """Request to generate a cover letter"""
    job_description_url: HttpUrl
    user_profile: UserProfile


class CoverLetterResponse(BaseModel):
    """Response containing generated cover letter"""
    title: str = Field(..., description="Cover letter title")
    body: str = Field(..., description="Full cover letter text")
    key_points_used: List[str] = Field(..., description="Key points from profile that were used")


class QuestionAnswerRequest(BaseModel):
    """Request to answer an HR question"""
    job_description_url: HttpUrl
    hr_question: str
    user_profile: UserProfile


class QuestionAnswerResponse(BaseModel):
    """Response containing HR question answer"""
    answer: str
    assumptions: List[str] = Field(default_factory=list, description="Any assumptions made in the answer")
    follow_up_question: Optional[str] = Field(None, description="Clarification question if needed")


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
    output_type: str = Field(..., description="Type of output: 'cover_letter' or 'question_answer'")


class FeedbackResponse(BaseModel):
    """Response containing feedback suggestions"""
    feedback_items: List[FeedbackItem] = Field(default_factory=list)


class ModificationRequest(BaseModel):
    """Request to modify output based on selected feedback"""
    original_output: Dict[str, Any] = Field(..., description="Original output to modify")
    selected_feedback: List[FeedbackItem] = Field(..., description="Selected feedback items to apply")
    output_type: str = Field(..., description="Type of output: 'cover_letter' or 'question_answer'")


class ModificationResponse(BaseModel):
    """Response containing modified output"""
    modified_output: Dict[str, Any] = Field(..., description="The modified output")


# Error response models
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
