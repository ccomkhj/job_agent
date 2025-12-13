import React, { useState } from 'react';
import type { FeedbackResponse, FeedbackItem } from '../types';

interface FeedbackSelectorProps {
  feedback: FeedbackResponse;
  contentType: 'cover_letter' | 'question_answer';
  originalOutput: any;
  onFeedbackApply: (selectedFeedback: FeedbackItem[], originalOutput: any, contentType: string) => void;
}

const FeedbackSelector: React.FC<FeedbackSelectorProps> = ({
  feedback,
  contentType,
  originalOutput,
  onFeedbackApply,
}) => {
  const [selectedFeedback, setSelectedFeedback] = useState<Set<string>>(new Set());

  const handleFeedbackToggle = (feedbackId: string) => {
    const newSelected = new Set(selectedFeedback);
    if (newSelected.has(feedbackId)) {
      newSelected.delete(feedbackId);
    } else {
      newSelected.add(feedbackId);
    }
    setSelectedFeedback(newSelected);
  };

  const handleApplyFeedback = () => {
    const selectedItems = feedback.feedback_items.filter((_, index) =>
      selectedFeedback.has(`feedback-${index}`)
    );

    if (selectedItems.length > 0) {
      onFeedbackApply(selectedItems, originalOutput, contentType);
      // Reset selection after applying
      setSelectedFeedback(new Set());
    }
  };

  const getFeedbackIcon = (type: string) => {
    switch (type) {
      case 'tone': return '🎭';
      case 'alignment': return '🎯';
      case 'clarity': return '💡';
      case 'emphasis': return '⭐';
      case 'structure': return '🏗️';
      default: return '💭';
    }
  };

  const getFeedbackTypeLabel = (type: string) => {
    switch (type) {
      case 'tone': return 'Tone';
      case 'alignment': return 'Job Alignment';
      case 'clarity': return 'Clarity';
      case 'emphasis': return 'Emphasis';
      case 'structure': return 'Structure';
      default: return 'General';
    }
  };

  if (!feedback.feedback_items || feedback.feedback_items.length === 0) {
    return (
      <div className="feedback-selector">
        <div className="feedback-header">
          <h4>✨ No feedback suggestions</h4>
          <p>The generated content looks good as-is!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-selector">
      <div className="feedback-header">
        <h4>💡 Suggested Improvements</h4>
        <p>Select the feedback items you'd like to apply:</p>
      </div>

      <div className="feedback-list">
        {feedback.feedback_items.map((item, index) => {
          const feedbackId = `feedback-${index}`;
          const isSelected = selectedFeedback.has(feedbackId);

          return (
            <div key={feedbackId} className={`feedback-item ${isSelected ? 'selected' : ''}`}>
              <label className="feedback-checkbox">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleFeedbackToggle(feedbackId)}
                />
                <span className="checkmark"></span>
              </label>

              <div className="feedback-content">
                <div className="feedback-type">
                  {getFeedbackIcon(item.type)} {getFeedbackTypeLabel(item.type)}
                </div>
                <div className="feedback-suggestion">
                  {item.suggestion}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="feedback-actions">
        <button
          onClick={handleApplyFeedback}
          disabled={selectedFeedback.size === 0}
          className="apply-feedback-button"
        >
          Apply Selected Feedback ({selectedFeedback.size})
        </button>

        <div className="selection-summary">
          {selectedFeedback.size > 0 ? (
            <span>{selectedFeedback.size} item{selectedFeedback.size > 1 ? 's' : ''} selected</span>
          ) : (
            <span>No items selected</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeedbackSelector;
