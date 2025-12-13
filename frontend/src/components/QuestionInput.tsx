import React, { useState } from 'react';

interface QuestionInputProps {
  onSubmit: (question: string) => void;
  disabled?: boolean;
}

const QuestionInput: React.FC<QuestionInputProps> = ({ onSubmit, disabled = false }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedQuestion = question.trim();
    if (!trimmedQuestion) {
      return;
    }

    onSubmit(trimmedQuestion);
    setQuestion(''); // Clear input after submission
  };

  const commonQuestions = [
    "Why are you interested in this position?",
    "What makes you a good fit for our team?",
    "Tell us about a challenging project you've worked on.",
    "Where do you see yourself in 5 years?",
    "What are your salary expectations?",
    "Why do you want to leave your current role?",
  ];

  const handleQuestionSelect = (selectedQuestion: string) => {
    setQuestion(selectedQuestion);
  };

  return (
    <div className="question-input">
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-group">
          <label htmlFor="hr-question">HR Question</label>
          <textarea
            id="hr-question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter the HR question you need help answering..."
            disabled={disabled}
            rows={3}
            required
          />
        </div>

        <div className="quick-questions">
          <label>Quick select common questions:</label>
          <div className="question-buttons">
            {commonQuestions.map((q, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleQuestionSelect(q)}
                disabled={disabled}
                className="question-button"
                title={q}
              >
                {q.length > 40 ? q.substring(0, 37) + '...' : q}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={disabled || !question.trim()}
          className="submit-button answer-button"
        >
          Answer Question
        </button>
      </form>
    </div>
  );
};

export default QuestionInput;
