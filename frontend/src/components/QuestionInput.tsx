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



