import React, { useState } from 'react';

interface JobUrlInputProps {
  onSubmit: (url: string) => void;
  disabled?: boolean;
}

const JobUrlInput: React.FC<JobUrlInputProps> = ({ onSubmit, disabled = false }) => {
  const [url, setUrl] = useState('');
  const [isValid, setIsValid] = useState(true);

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
        <button
          type="submit"
          disabled={disabled || !url.trim() || !isValid}
          className="submit-button"
        >
          Submit Job URL
        </button>
      </form>
    </div>
  );
};

export default JobUrlInput;
