import axios, { type AxiosResponse } from 'axios';
import type {
    CoverLetterApiResponse,
    CoverLetterRequest,
    ErrorResponse,
    ModificationRequest,
    ModificationResponse,
    QuestionAnswerApiResponse,
    QuestionAnswerRequest,
    UserProfile
} from '../types';

// Configure axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data) {
      const errorData: ErrorResponse = error.response.data;
      throw new Error(errorData.detail || errorData.error || 'API request failed');
    }
    throw new Error(error.message || 'Network error');
  }
);

export class ApiService {
  /**
   * Generate a cover letter based on job description and user profile
   */
  static async generateCoverLetter(request: CoverLetterRequest): Promise<CoverLetterApiResponse> {
    const response: AxiosResponse<CoverLetterApiResponse> = await api.post('/generate/cover-letter', request);
    return response.data;
  }

  /**
   * Answer an HR question based on job description and user profile
   */
  static async generateAnswer(request: QuestionAnswerRequest): Promise<QuestionAnswerApiResponse> {
    const response: AxiosResponse<QuestionAnswerApiResponse> = await api.post('/generate/answer', request);
    return response.data;
  }

  /**
   * Apply selected feedback to modify generated content
   */
  static async modifyOutput(request: ModificationRequest): Promise<ModificationResponse> {
    const response: AxiosResponse<ModificationResponse> = await api.post('/modify', request);
    return response.data;
  }

  /**
   * Validate a job URL by attempting to fetch job description
   */
  static async validateJobUrl(url: string): Promise<boolean> {
    try {
      // This would ideally call a backend endpoint to validate the URL
      // For now, we'll do basic validation
      const urlPattern = /^https?:\/\/.+/i;
      return urlPattern.test(url);
    } catch (error) {
      console.error('URL validation error:', error);
      return false;
    }
  }

  /**
   * Save user profile to server-side local storage
   */
  static async saveProfile(profile: UserProfile): Promise<void> {
    const response: AxiosResponse<{ message: string }> = await api.post('/local-profile', profile);
    return response.data;
  }

  /**
   * Load user profile from server-side local storage
   */
  static async loadProfile(): Promise<UserProfile | null> {
    try {
      console.log('ApiService: Loading profile from server...');
      const response: AxiosResponse<UserProfile> = await api.get('/local-profile');
      console.log('ApiService: Profile loaded successfully', response.data);
      return response.data;
    } catch (error: any) {
      // If profile not found, return null (not an error)
      if (error.response?.status === 404) {
        console.log('ApiService: No profile found (404)');
        return null;
      }
      console.error('ApiService: Error loading profile:', error);
      return null;
    }
  }

}

// Utility functions for clipboard operations
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    // Fallback for older browsers
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return true;
    } catch (fallbackError) {
      console.error('Fallback copy failed:', fallbackError);
      return false;
    }
  }
};

// Format content for display
export const formatJsonForDisplay = (obj: any): string => {
  return JSON.stringify(obj, null, 2);
};

export default ApiService;
