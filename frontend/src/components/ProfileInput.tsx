import React, { useState, useEffect } from 'react';
import type { UserProfile, CareerBackground } from '../types';

interface ProfileInputProps {
  onSubmit: (profile: UserProfile) => void;
  currentProfile?: UserProfile;
  disabled?: boolean;
}

const ProfileInput: React.FC<ProfileInputProps> = ({
  onSubmit,
  currentProfile,
  disabled = false
}) => {
  const [careerBackground, setCareerBackground] = useState<CareerBackground>({
    data_science: '',
    data_engineering: '',
    computer_vision: '',
    cto: '',
  });

  const [educationBackground, setEducationBackground] = useState('');
  const [motivation, setMotivation] = useState('');
  const [activeTab, setActiveTab] = useState<keyof CareerBackground>('data_science');

  // Load current profile when it changes
  useEffect(() => {
    if (currentProfile) {
      setCareerBackground(currentProfile.career_background);
      setEducationBackground(currentProfile.education_background);
      setMotivation(currentProfile.motivation);
    }
  }, [currentProfile]);

  const handleCareerBackgroundChange = (field: keyof CareerBackground, value: string) => {
    setCareerBackground(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const profile: UserProfile = {
      career_background: careerBackground,
      education_background: educationBackground.trim(),
      motivation: motivation.trim(),
    };

    onSubmit(profile);
  };

  const isFormValid = () => {
    return educationBackground.trim() && motivation.trim() &&
           Object.values(careerBackground).some(content => content.trim());
  };

  const careerTabs = [
    { key: 'data_science' as keyof CareerBackground, label: 'Data Science', icon: '📊' },
    { key: 'data_engineering' as keyof CareerBackground, label: 'Data Engineering', icon: '⚙️' },
    { key: 'computer_vision' as keyof CareerBackground, label: 'Computer Vision', icon: '👁️' },
    { key: 'cto' as keyof CareerBackground, label: 'CTO/Leadership', icon: '👔' },
  ];

  return (
    <div className="profile-input">
      <form onSubmit={handleSubmit} className="input-form">
        <h3>Your Professional Profile</h3>

        {/* Career Background Tabs */}
        <div className="career-tabs">
          <label>Career Background (add details for relevant roles)</label>
          <div className="tabs">
            {careerTabs.map(({ key, label, icon }) => (
              <button
                key={key}
                type="button"
                className={`tab ${activeTab === key ? 'active' : ''}`}
                onClick={() => setActiveTab(key)}
                disabled={disabled}
              >
                {icon} {label}
              </button>
            ))}
          </div>

          <div className="tab-content">
            {careerTabs.map(({ key, label }) => (
              <div
                key={key}
                className={`tab-panel ${activeTab === key ? 'active' : ''}`}
              >
                <textarea
                  value={careerBackground[key]}
                  onChange={(e) => handleCareerBackgroundChange(key, e.target.value)}
                  placeholder={`Describe your ${label.toLowerCase()} experience, skills, and achievements...`}
                  disabled={disabled}
                  rows={6}
                  className="career-textarea"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Education Background */}
        <div className="input-group">
          <label htmlFor="education">Education Background</label>
          <textarea
            id="education"
            value={educationBackground}
            onChange={(e) => setEducationBackground(e.target.value)}
            placeholder="Describe your educational background, degrees, certifications..."
            disabled={disabled}
            rows={4}
            required
          />
        </div>

        {/* Motivation */}
        <div className="input-group">
          <label htmlFor="motivation">Motivation & Career Goals</label>
          <textarea
            id="motivation"
            value={motivation}
            onChange={(e) => setMotivation(e.target.value)}
            placeholder="What drives you? What are your career goals and motivations?"
            disabled={disabled}
            rows={4}
            required
          />
        </div>

        <button
          type="submit"
          disabled={disabled || !isFormValid()}
          className="submit-button"
        >
          {currentProfile ? 'Update Profile' : 'Save Profile'}
        </button>

        {currentProfile && (
          <div className="profile-status">
            ✅ Profile loaded and ready to use
          </div>
        )}
      </form>
    </div>
  );
};

export default ProfileInput;
