import React, { useState } from 'react';

interface JobUrlInputProps {
  onSubmit: (url: string) => void;
  onManualSubmit?: (description: string) => void;
  disabled?: boolean;
}

const JobUrlInput: React.FC<JobUrlInputProps> = ({ onSubmit, onManualSubmit, disabled = false }) => {
  const [url, setUrl] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [showManualModal, setShowManualModal] = useState(false);
  const [manualDescription, setManualDescription] = useState('');

  const validateUrl = (inputUrl: string) => {
    const urlPattern = /^https?:\/\/.+/i;
    return urlPattern.test(inputUrl.trim());
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedUrl = url.trim();
    if (!trimmedUrl) {
      setIsValid(false);
      return;
    }

    if (!validateUrl(trimmedUrl)) {
      setIsValid(false);
      return;
    }

    setIsValid(true);
    onSubmit(trimmedUrl);
    setUrl(''); // Clear input after successful submission
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);

    // Real-time validation
    if (newUrl.trim()) {
      setIsValid(validateUrl(newUrl));
    } else {
      setIsValid(true); // Don't show error for empty field
    }
  };

  const handleManualSubmit = () => {
    if (manualDescription.trim() && onManualSubmit) {
      onManualSubmit(manualDescription.trim());
      setManualDescription('');
      setShowManualModal(false);
    }
  };

  const handleModalClose = () => {
    setShowManualModal(false);
    setManualDescription('');
  };

  return (
    <div className="job-url-input">
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-group">
          <label htmlFor="job-url">Job Posting URL</label>
          <input
            id="job-url"
            type="url"
            value={url}
            onChange={handleUrlChange}
            placeholder="https://example.com/job-posting"
            disabled={disabled}
            className={`url-input ${!isValid ? 'invalid' : ''}`}
          />
          {!isValid && (
            <div className="error-message">
              Please enter a valid URL (starting with http:// or https://)
            </div>
          )}
        </div>
        <div className="button-group">
          <button
            type="submit"
            disabled={disabled || !url.trim() || !isValid}
            className="submit-button"
          >
            Submit Job URL
          </button>
          <button
            type="button"
            onClick={() => setShowManualModal(true)}
            disabled={disabled}
            className="manual-description-button"
          >
            Add description manually
          </button>
        </div>
      </form>

      {/* Manual Description Modal */}
      {showManualModal && (
        <div className="modal-overlay" onClick={handleModalClose}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add Job Description Manually</h3>
              <button
                type="button"
                onClick={handleModalClose}
                className="modal-close"
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <textarea
                value={manualDescription}
                onChange={(e) => setManualDescription(e.target.value)}
                placeholder="Paste the job description content here..."
                rows={15}
                className="manual-description-textarea"
                autoFocus
              />
            </div>
            <div className="modal-footer">
              <button
                type="button"
                onClick={handleModalClose}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleManualSubmit}
                disabled={!manualDescription.trim()}
                className="submit-manual-button"
              >
                Submit Description
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobUrlInput;



