import React from 'react';
import type { ChatMessage, FeedbackItem } from '../types';
import AgentProgress from './AgentProgress';
import FeedbackSelector from './FeedbackSelector';
import OutputDisplay from './OutputDisplay';

interface MessageBubbleProps {
  message: ChatMessage;
  onFeedbackApply?: (selectedFeedback: FeedbackItem[], originalOutput: any, contentType: string) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onFeedbackApply }) => {
  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderContent = () => {
    if (typeof message.content === 'string') {
      return <div className="message-text" style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>;
    }

    if (typeof message.content === 'object' && message.content.type) {
      const contentData = message.content;

      if (contentData.type === 'cover_letter' || contentData.type === 'question_answer') {
        return (
          <OutputDisplay
            data={contentData.data}
            type={contentData.type}
            metadata={contentData.metadata}
          />
        );
      }

      if (contentData.type === 'feedback') {
        return (
          <FeedbackSelector
            feedback={contentData.data}
            contentType={contentData.contentType}
            originalOutput={contentData.originalOutput}
            onFeedbackApply={onFeedbackApply || ((selectedFeedback) => {
              console.log('Feedback selected:', selectedFeedback);
            })}
          />
        );
      }

      if (contentData.agentSteps) {
        return (
          <AgentProgress
            agentSteps={contentData.agentSteps}
            isComplete={contentData.isComplete}
          />
        );
      }
    }

    // Fallback for unknown content types
    return <div className="message-text">{JSON.stringify(message.content, null, 2)}</div>;
  };

  return (
    <div className={`message-bubble message-${message.type}`}>
      <div className="message-content">
        {renderContent()}
      </div>
      <div className="message-timestamp">
        {formatTimestamp(message.timestamp)}
      </div>
    </div>
  );
};

export default MessageBubble;
