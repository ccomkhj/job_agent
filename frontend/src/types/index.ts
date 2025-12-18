// TypeScript type definitions matching backend Pydantic models

export interface CareerStory {
  initiator?: string;
  achievement_sample?: string;
  education_profile?: string;
  motivation_goals?: string;
}

export interface CareerBackground {
  careers: {
    [categoryName: string]: CareerStory;
  };
}

export interface UserProfile {
  career_background: CareerBackground;
  education_background: string;
  motivation: string;
}

export interface JobDescription {
  url: string;
  title?: string;
  responsibilities: string[];
  requirements: string[];
  role_summary: string;
  company_context: string;
}

export interface DataCollectorOutput {
  selected_profile_version: string;
  relevant_skills: string[];
  relevant_experience: string[];
  relevant_education: string[];
  motivational_alignment: string;
  content_guidance?: string;
}

export interface CoverLetterRequest {
  job_description_url?: string;
  job_description_text?: string;
  user_profile: UserProfile;
}

export interface CoverLetterResponse {
  title: string;
  body: string;
  key_points_used: string[];
}

export interface QuestionAnswerRequest {
  job_description_url?: string;
  job_description_text?: string;
  hr_question: string;
  user_profile: UserProfile;
}

export interface QuestionAnswerResponse {
  answer: string;
  assumptions: string[];
  follow_up_question?: string;
}

export type FeedbackType = 'tone' | 'alignment' | 'clarity' | 'emphasis' | 'structure';

export interface FeedbackItem {
  type: FeedbackType;
  suggestion: string;
}

export interface FeedbackResponse {
  feedback_items: FeedbackItem[];
}

export interface ModificationRequest {
  original_output: any; // CoverLetterResponse or QuestionAnswerResponse as dict
  selected_feedback: FeedbackItem[];
  output_type: 'cover_letter' | 'question_answer';
}

export interface ModificationResponse {
  modified_output: any; // CoverLetterResponse or QuestionAnswerResponse
}

// API Response types
export interface AgentStep {
  agent: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  description: string;
  result?: any;
  timestamp?: Date;
}

export interface CoverLetterApiResponse {
  cover_letter: CoverLetterResponse;
  feedback: FeedbackResponse;
  job_summary: {
    title?: string;
    role_summary: string;
    company_context: string;
  };
  filtered_profile: DataCollectorOutput;
  agent_steps?: AgentStep[];
}

export interface QuestionAnswerApiResponse {
  answer: QuestionAnswerResponse;
  feedback: FeedbackResponse;
  job_summary: {
    title?: string;
    role_summary: string;
    company_context: string;
  };
  filtered_profile: DataCollectorOutput;
  agent_steps?: AgentStep[];
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  code?: string;
}

// Chat message types
export type MessageType = 'user' | 'system' | 'assistant' | 'agent_progress';

export interface ChatMessage {
  id: string;
  type: MessageType;
  content: any; // Can be string, object, or component-specific data
  timestamp: Date;
}

// Application state
export interface AppState {
  currentJobUrl?: string;
  currentProfile?: UserProfile;
  manualJobDescription?: string;
  messages: ChatMessage[];
  isLoading: boolean;
  error?: string;
}


