import React, { useEffect, useRef, useState } from 'react';
import ApiService from '../services/api';
import type {
  AppState,
  ChatMessage,
  CoverLetterApiResponse,
  FeedbackItem,
  MessageType,
  QuestionAnswerApiResponse,
  UserProfile
} from '../types';
import ActionButtons from './ActionButtons';
import JobUrlInput from './JobUrlInput';
import MessageBubble from './MessageBubble';
import ProfileInput from './ProfileInput';
import QuestionInput from './QuestionInput';

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

  // Load saved profile on component mount (guard against StrictMode double-invoke)
  const hasLoadedProfile = useRef(false);
  useEffect(() => {
    const loadSavedProfile = async () => {
      if (hasLoadedProfile.current) return;
      hasLoadedProfile.current = true;

      try {
        console.log('ChatInterface: Loading saved profile...');
        const savedProfile = await ApiService.loadProfile();
        console.log('ChatInterface: Loaded profile', savedProfile);

        if (savedProfile) {
          console.log('ChatInterface: Setting currentProfile in state');
          setState(prev => ({ ...prev, currentProfile: savedProfile }));

          // Count how many career categories have content
          const careers = savedProfile.career_background.careers || {};
          const careerCount = Object.keys(careers).length;
          const hasDataScience = Object.keys(careers).some(
            key => key.toLowerCase() === 'data science' || key.toLowerCase() === 'data_science'
          );

          let profileType = 'Empty profile';
          if (careerCount > 0) {
            profileType = `${careerCount} career categorie${careerCount > 1 ? 's' : ''}`;
            if (hasDataScience) {
              profileType += ' (includes Data Science)';
            }
          }

          addMessage('system', `✅ Loaded saved profile: ${profileType}`);
        } else {
          console.log('ChatInterface: No saved profile found');
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

  const handleManualJobDescriptionSubmit = async (description: string) => {
    setLoading(true);
    setError(undefined);

    try {
      // Process manual job description
      setState(prev => ({ ...prev, currentJobUrl: 'manual', manualJobDescription: description }));
      addMessage('user', `Manual Job Description (${description.length} characters)`);

      // Show job summary from manual description
      addMessage('system', `📄 Manual job description submitted\n\nPlease provide your profile information or load a saved profile to continue.`);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to process manual job description';
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
    if ((!state.currentJobUrl && !state.manualJobDescription) || !state.currentProfile) {
      setError('Please provide both job description and profile first');
      return;
    }

    setLoading(true);
    setError(undefined);

    try {
      addMessage('user', 'Generate Cover Letter');

      const request: any = {
        user_profile: state.currentProfile,
      };

      console.log('Building request - currentJobUrl:', state.currentJobUrl, 'manualJobDescription:', !!state.manualJobDescription);

      // Only include job description fields if they exist
      // Don't include URL if it's the placeholder "manual" value
      if (state.currentJobUrl && state.currentJobUrl.trim() && state.currentJobUrl !== 'manual') {
        request.job_description_url = state.currentJobUrl.trim();
        console.log('Including job_description_url:', request.job_description_url);
      }
      if (state.manualJobDescription && state.manualJobDescription.trim()) {
        request.job_description_text = state.manualJobDescription.trim();
        console.log('Including job_description_text, length:', request.job_description_text.length);
      }

      console.log('Final request keys:', Object.keys(request));

      const response: CoverLetterApiResponse = await ApiService.generateCoverLetter(request);

      // Show agent progress visualization
      if (response.agent_steps) {
        addMessage('agent_progress', {
          agentSteps: response.agent_steps,
          isComplete: true,
        });
      }

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
    if ((!state.currentJobUrl && !state.manualJobDescription) || !state.currentProfile) {
      setError('Please provide both job description and profile first');
      return;
    }

    setLoading(true);
    setError(undefined);

    try {
      addMessage('user', `Question: ${question}`);

      const request: any = {
        hr_question: question,
        user_profile: state.currentProfile,
      };

      console.log('Building QA request - currentJobUrl:', state.currentJobUrl, 'manualJobDescription:', !!state.manualJobDescription);

      // Only include job description fields if they exist
      // Don't include URL if it's the placeholder "manual" value
      if (state.currentJobUrl && state.currentJobUrl.trim() && state.currentJobUrl !== 'manual') {
        request.job_description_url = state.currentJobUrl.trim();
        console.log('Including job_description_url:', request.job_description_url);
      }
      if (state.manualJobDescription && state.manualJobDescription.trim()) {
        request.job_description_text = state.manualJobDescription.trim();
        console.log('Including job_description_text, length:', request.job_description_text.length);
      }

      console.log('Final QA request keys:', Object.keys(request));

      const response: QuestionAnswerApiResponse = await ApiService.generateAnswer(request);

      // Show agent progress visualization
      if (response.agent_steps) {
        addMessage('agent_progress', {
          agentSteps: response.agent_steps,
          isComplete: true,
        });
      }

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
          onManualSubmit={handleManualJobDescriptionSubmit}
          disabled={state.isLoading}
        />

        <ProfileInput
          onSubmit={handleProfileSubmit}
          currentProfile={state.currentProfile}
          disabled={state.isLoading}
        />

        <ActionButtons
          onCoverLetterClick={handleCoverLetterRequest}
          disabled={state.isLoading || (!state.currentJobUrl && !state.manualJobDescription) || !state.currentProfile}
        />

        <QuestionInput
          onSubmit={handleQuestionSubmit}
          disabled={state.isLoading || (!state.currentJobUrl && !state.manualJobDescription) || !state.currentProfile}
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
