import React, { useState } from 'react';
import type { CoverLetterResponse, QuestionAnswerResponse } from '../types';
import { copyToClipboard } from '../services/api';

interface OutputDisplayProps {
  data: CoverLetterResponse | QuestionAnswerResponse;
  type: 'cover_letter' | 'question_answer';
  metadata?: any;
}

const OutputDisplay: React.FC<OutputDisplayProps> = ({ data, type, metadata }) => {
  const [copyStatus, setCopyStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleCopy = async () => {
    let textToCopy = '';

    if (type === 'cover_letter') {
      const coverLetter = data as CoverLetterResponse;
      textToCopy = coverLetter.body;
    } else {
      const answer = data as QuestionAnswerResponse;
      textToCopy = answer.answer;
    }

    const success = await copyToClipboard(textToCopy);
    setCopyStatus(success ? 'success' : 'error');

    // Reset status after 2 seconds
    setTimeout(() => setCopyStatus('idle'), 2000);
  };

  const renderCoverLetter = (coverLetter: CoverLetterResponse) => (
    <div className="output-content cover-letter">
      <div className="output-header">
        <h3>{coverLetter.title}</h3>
        <button
          onClick={handleCopy}
          className={`copy-button ${copyStatus}`}
          title="Copy to clipboard"
        >
          {copyStatus === 'success' ? '✅' : copyStatus === 'error' ? '❌' : '📋'}
        </button>
      </div>

      <div className="cover-letter-body">
        {coverLetter.body.split('\n').map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>

      {coverLetter.key_points_used.length > 0 && (
        <div className="key-points">
          <h4>Key Points Used:</h4>
          <ul>
            {coverLetter.key_points_used.map((point, index) => (
              <li key={index}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      {metadata?.isModified && (
        <div className="modification-notice">
          ✏️ Content has been modified based on feedback
        </div>
      )}
    </div>
  );

  const renderQuestionAnswer = (answer: QuestionAnswerResponse) => (
    <div className="output-content question-answer">
      <div className="output-header">
        <h3>Answer</h3>
        <button
          onClick={handleCopy}
          className={`copy-button ${copyStatus}`}
          title="Copy to clipboard"
        >
          {copyStatus === 'success' ? '✅' : copyStatus === 'error' ? '❌' : '📋'}
        </button>
      </div>

      <div className="answer-body">
        <p>{answer.answer}</p>
      </div>

      {answer.assumptions.length > 0 && (
        <div className="assumptions">
          <h4>Assumptions Made:</h4>
          <ul>
            {answer.assumptions.map((assumption, index) => (
              <li key={index}>{assumption}</li>
            ))}
          </ul>
        </div>
      )}

      {answer.follow_up_question && (
        <div className="follow-up">
          <h4>Follow-up Question:</h4>
          <p>{answer.follow_up_question}</p>
        </div>
      )}

      {metadata?.isModified && (
        <div className="modification-notice">
          ✏️ Content has been modified based on feedback
        </div>
      )}
    </div>
  );

  return (
    <div className="output-display">
      {type === 'cover_letter'
        ? renderCoverLetter(data as CoverLetterResponse)
        : renderQuestionAnswer(data as QuestionAnswerResponse)
      }

      {metadata?.filteredProfile && (
        <details className="metadata-section">
          <summary>Profile Used</summary>
          <div className="profile-summary">
            <p><strong>Selected Version:</strong> {metadata.filteredProfile.selected_profile_version}</p>
            <p><strong>Relevant Skills:</strong> {metadata.filteredProfile.relevant_skills.join(', ')}</p>
            <p><strong>Motivational Alignment:</strong> {metadata.filteredProfile.motivational_alignment}</p>
          </div>
        </details>
      )}
    </div>
  );
};

export default OutputDisplay;
