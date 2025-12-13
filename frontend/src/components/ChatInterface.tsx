import React, { useState, useEffect, useRef } from 'react';
import type {
  ChatMessage,
  MessageType,
  AppState,
  UserProfile,
  CoverLetterApiResponse,
  QuestionAnswerApiResponse,
  FeedbackItem
} from '../types';
import ApiService from '../services/api';
import MessageBubble from './MessageBubble';
import JobUrlInput from './JobUrlInput';
import ProfileInput from './ProfileInput';
import QuestionInput from './QuestionInput';
import ActionButtons from './ActionButtons';

const ChatInterface: React.FC = () => {
  const [state, setState] = useState<AppState>({
    messages: [],
    isLoading: false,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages]);

  // Load saved profile on component mount
  useEffect(() => {
    const loadSavedProfile = async () => {
      try {
        const savedProfile = await ApiService.loadProfile();
        if (savedProfile) {
          setState(prev => ({ ...prev, currentProfile: savedProfile }));
          addMessage('system', `Loaded saved profile: ${savedProfile.career_background.data_science ? 'Data Science focus' : 'General profile'}`);
        }
      } catch (error) {
        console.error('Error loading saved profile:', error);
      }
    };

    loadSavedProfile();
  }, []);

  const addMessage = (type: MessageType, content: any, timestamp?: Date) => {
    const message: ChatMessage = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      type,
      content,
      timestamp: timestamp || new Date(),
    };

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, message],
    }));
  };

  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  };

  const setError = (error: string | undefined) => {
    setState(prev => ({ ...prev, error }));
  };

  const handleJobUrlSubmit = async (url: string) => {
    setLoading(true);
    setError(undefined);

    try {
      const isValid = await ApiService.validateJobUrl(url);
      if (!isValid) {
        throw new Error('Invalid job URL format');
      }

      setState(prev => ({ ...prev, currentJobUrl: url }));
      addMessage('user', `Job URL: ${url}`);

      // Show job summary (placeholder - in real implementation, fetch from backend)
      addMessage('system', `📄 Job URL submitted: ${url}\n\nPlease provide your profile information or load a saved profile to continue.`);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to process job URL';
      setError(errorMessage);
      addMessage('system', `❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (profile: UserProfile) => {
    try {
      await ApiService.saveProfile(profile);
      setState(prev => ({ ...prev, currentProfile: profile }));
      addMessage('user', 'Profile updated');
      addMessage('system', '✅ Profile saved successfully! You can now generate cover letters or answer HR questions.');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save profile';
      setError(errorMessage);
      addMessage('system', `❌ Error: ${errorMessage}`);
    }
  };

  const handleCoverLetterRequest = async () => {
    if (!state.currentJobUrl || !state.currentProfile) {
      setError('Please provide both job URL and profile first');
      return;
    }

    setLoading(true);
    setError(undefined);

    try {
      addMessage('user', 'Generate Cover Letter');

      const request = {
        job_description_url: state.currentJobUrl,
        user_profile: state.currentProfile,
      };

      const response: CoverLetterApiResponse = await ApiService.generateCoverLetter(request);

      // Show job summary
      addMessage('system', `📋 Job Summary:\n${response.job_summary.role_summary}\n\n🏢 Company: ${response.job_summary.company_context}`);

      // Show generated cover letter
      addMessage('assistant', {
        type: 'cover_letter',
        data: response.cover_letter,
        metadata: {
          filteredProfile: response.filtered_profile,
          jobSummary: response.job_summary,
        },
      });

      // Show feedback
      if (response.feedback.feedback_items.length > 0) {
        addMessage('system', {
          type: 'feedback',
          data: response.feedback,
          contentType: 'cover_letter',
          originalOutput: response.cover_letter,
        });
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate cover letter';
      setError(errorMessage);
      addMessage('system', `❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleQuestionSubmit = async (question: string) => {
    if (!state.currentJobUrl || !state.currentProfile) {
      setError('Please provide both job URL and profile first');
      return;
    }

    setLoading(true);
    setError(undefined);

    try {
      addMessage('user', `Question: ${question}`);

      const request = {
        job_description_url: state.currentJobUrl,
        hr_question: question,
        user_profile: state.currentProfile,
      };

      const response: QuestionAnswerApiResponse = await ApiService.generateAnswer(request);

      // Show generated answer
      addMessage('assistant', {
        type: 'question_answer',
        data: response.answer,
        metadata: {
          filteredProfile: response.filtered_profile,
          jobSummary: response.job_summary,
        },
      });

      // Show feedback
      if (response.feedback.feedback_items.length > 0) {
        addMessage('system', {
          type: 'feedback',
          data: response.feedback,
          contentType: 'question_answer',
          originalOutput: response.answer,
        });
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to answer question';
      setError(errorMessage);
      addMessage('system', `❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackApply = async (selectedFeedback: FeedbackItem[], originalOutput: any, contentType: string) => {
    setLoading(true);
    setError(undefined);

    try {
      addMessage('user', `Apply ${selectedFeedback.length} feedback item(s)`);

      // Ensure contentType is valid
      const validContentTypes = ['cover_letter', 'question_answer'] as const;
      const outputType = validContentTypes.includes(contentType as any) ? contentType as 'cover_letter' | 'question_answer' : 'cover_letter';

      const request = {
        original_output: originalOutput,
        selected_feedback: selectedFeedback,
        output_type: outputType,
      };

      const response = await ApiService.modifyOutput(request);

      // Show modified output
      addMessage('assistant', {
        type: contentType,
        data: response.modified_output,
        metadata: {
          isModified: true,
          appliedFeedback: selectedFeedback,
        },
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to apply feedback';
      setError(errorMessage);
      addMessage('system', `❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Job Agent Assistant</h1>
        <p>AI-powered cover letter and HR question assistance</p>
      </div>

      <div className="chat-messages">
        {state.messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onFeedbackApply={handleFeedbackApply}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {state.error && (
        <div className="error-banner">
          {state.error}
        </div>
      )}

      <div className="chat-inputs">
        <JobUrlInput
          onSubmit={handleJobUrlSubmit}
          disabled={state.isLoading}
        />

        <ProfileInput
          onSubmit={handleProfileSubmit}
          currentProfile={state.currentProfile}
          disabled={state.isLoading}
        />

        <ActionButtons
          onCoverLetterClick={handleCoverLetterRequest}
          disabled={state.isLoading || !state.currentJobUrl || !state.currentProfile}
        />

        <QuestionInput
          onSubmit={handleQuestionSubmit}
          disabled={state.isLoading || !state.currentJobUrl || !state.currentProfile}
        />
      </div>

      {state.isLoading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          Processing...
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
