import React from 'react';

interface ActionButtonsProps {
  onCoverLetterClick: () => void;
  disabled?: boolean;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
  onCoverLetterClick,
  disabled = false
}) => {
  return (
    <div className="action-buttons">
      <div className="button-group">
        <button
          onClick={onCoverLetterClick}
          disabled={disabled}
          className="action-button cover-letter-button"
        >
          ✉️ Write Cover Letter
        </button>
        <div className="button-description">
          Generate a tailored cover letter based on the job posting and your profile
        </div>
      </div>
    </div>
  );
};

export default ActionButtons;

