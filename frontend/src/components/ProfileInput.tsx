import React, { useEffect, useState } from 'react';
import type { CareerBackground, CareerStory, UserProfile } from '../types';

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
    'Data Science': { initiator: '', achievement_sample: '', education_profile: '', motivation_goals: '' },
    'Data Engineering': { initiator: '', achievement_sample: '', education_profile: '', motivation_goals: '' },
    'Computer Vision': { initiator: '', achievement_sample: '', education_profile: '', motivation_goals: '' },
    'CTO/Leadership': { initiator: '', achievement_sample: '', education_profile: '', motivation_goals: '' },
  });

  const [activeCareerTab, setActiveCareerTab] = useState<string>('Data Science');
  const [activeStoryTab, setActiveStoryTab] = useState<keyof CareerStory>('achievement_sample');
  const [editingCategory, setEditingCategory] = useState<string | null>(null);
  const [newCategoryName, setNewCategoryName] = useState<string>('');
  const [showStoryModal, setShowStoryModal] = useState(false);
  const [modalStoryContent, setModalStoryContent] = useState('');

  // Load current profile when it changes
  useEffect(() => {
    console.log('ProfileInput: currentProfile changed', currentProfile);

    if (currentProfile && currentProfile.career_background) {
      console.log('ProfileInput: career_background found', currentProfile.career_background);

      let updatedBackground: CareerBackground = {};

      // Handle different profile structures
      if (currentProfile.career_background.careers) {
        // New structure with careers field (from server) - ensure all fields exist
        console.log('ProfileInput: using careers field', currentProfile.career_background.careers);
        updatedBackground = {};
        for (const [category, story] of Object.entries(currentProfile.career_background.careers)) {
          updatedBackground[category] = {
            initiator: story?.initiator || '',
            achievement_sample: story?.achievement_sample || '',
            education_profile: story?.education_profile || '',
            motivation_goals: story?.motivation_goals || '',
          };
        }
      } else if ('data_science' in currentProfile.career_background) {
        // Old structure - migrate to new dynamic structure
        console.log('ProfileInput: migrating old structure');
        const oldBg = currentProfile.career_background as any;
        updatedBackground = {
          'Data Science': {
            initiator: oldBg.data_science?.initiator || '',
            achievement_sample: oldBg.data_science?.achievement_sample || '',
            education_profile: oldBg.data_science?.education_profile || '',
            motivation_goals: oldBg.data_science?.motivation_goals || ''
          },
          'Data Engineering': {
            initiator: oldBg.data_engineering?.initiator || '',
            achievement_sample: oldBg.data_engineering?.achievement_sample || '',
            education_profile: oldBg.data_engineering?.education_profile || '',
            motivation_goals: oldBg.data_engineering?.motivation_goals || ''
          },
          'Computer Vision': {
            initiator: oldBg.computer_vision?.initiator || '',
            achievement_sample: oldBg.computer_vision?.achievement_sample || '',
            education_profile: oldBg.computer_vision?.education_profile || '',
            motivation_goals: oldBg.computer_vision?.motivation_goals || ''
          },
          'CTO/Leadership': {
            initiator: oldBg.cto?.initiator || '',
            achievement_sample: oldBg.cto?.achievement_sample || '',
            education_profile: oldBg.cto?.education_profile || '',
            motivation_goals: oldBg.cto?.motivation_goals || ''
          },
        };
      } else {
        // Fallback for any other structure
        console.log('ProfileInput: using fallback structure');
        updatedBackground = currentProfile.career_background as any;
      }

      console.log('ProfileInput: setting careerBackground', updatedBackground);
      setCareerBackground(updatedBackground);

      // Set active tab to first available category
      const firstCategory = Object.keys(updatedBackground)[0];
      if (firstCategory) {
        console.log('ProfileInput: setting active tab to', firstCategory);
        setActiveCareerTab(firstCategory);
      }
    } else {
      console.log('ProfileInput: no currentProfile or career_background');
    }
  }, [currentProfile]);

  const handleCareerStoryChange = (categoryName: string, storyField: keyof CareerStory, value: string) => {
    setCareerBackground(prev => ({
      ...prev,
      [categoryName]: {
        ...prev[categoryName],
        [storyField]: value,
      },
    }));
  };

  const addCareerCategory = () => {
    if (newCategoryName.trim()) {
      const categoryName = newCategoryName.trim();
      setCareerBackground(prev => ({
        ...prev,
        [categoryName]: { initiator: '', achievement_sample: '', education_profile: '', motivation_goals: '' },
      }));
      setActiveCareerTab(categoryName);
      setNewCategoryName('');
    }
  };

  const removeCareerCategory = (categoryName: string) => {
    setCareerBackground(prev => {
      const updated = { ...prev };
      delete updated[categoryName];

      // If we're removing the active tab, switch to another one
      if (activeCareerTab === categoryName) {
        const remainingCategories = Object.keys(updated);
        setActiveCareerTab(remainingCategories.length > 0 ? remainingCategories[0] : '');
      }

      return updated;
    });
  };

  const renameCareerCategory = (oldName: string, newName: string) => {
    if (newName.trim() && newName !== oldName) {
      setCareerBackground(prev => {
        const updated = { ...prev };
        updated[newName] = updated[oldName];
        delete updated[oldName];

        // Update active tab if it was renamed
        if (activeCareerTab === oldName) {
          setActiveCareerTab(newName);
        }

        return updated;
      });
    }
    setEditingCategory(null);
  };

  const openStoryModal = (careerName: string, storyType: keyof CareerStory) => {
    const currentContent = careerBackground[careerName]?.[storyType] || '';
    setModalStoryContent(currentContent);
    setActiveCareerTab(careerName);
    setActiveStoryTab(storyType);
    setShowStoryModal(true);
  };

  const handleStoryModalSubmit = () => {
    handleCareerStoryChange(activeCareerTab, activeStoryTab, modalStoryContent.trim());
    setShowStoryModal(false);
    setModalStoryContent('');
  };

  const handleStoryModalClose = () => {
    setShowStoryModal(false);
    setModalStoryContent('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // For backward compatibility, populate education_background and motivation from the first available story
    let education_background = '';
    let motivation = '';

    Object.values(careerBackground).forEach(story => {
      if (story) {
        if (story.education_profile && !education_background) {
          education_background = story.education_profile;
        }
        if (story.motivation_goals && !motivation) {
          motivation = story.motivation_goals;
        }
      }
    });

    const profile: UserProfile = {
      career_background: { careers: careerBackground },
      education_background: education_background,
      motivation: motivation,
    };

    onSubmit(profile);
  };

  const isFormValid = () => {
    return Object.values(careerBackground).some(story =>
      story && Object.values(story).some(content => content && content.trim())
    );
  };

  const careerCategories = Object.keys(careerBackground);

  const getCategoryIcon = (categoryName: string): string => {
    const iconMap: Record<string, string> = {
      'Data Science': '📊',
      'Data Engineering': '⚙️',
      'Computer Vision': '👁️',
      'CTO/Leadership': '👔',
    };
    return iconMap[categoryName] || '💼';
  };

  const storyTabs = [
    { key: 'achievement_sample' as keyof CareerStory, label: 'Achievement Sample', icon: '🏆' },
    { key: 'education_profile' as keyof CareerStory, label: 'Education Profile', icon: '🎓' },
    { key: 'motivation_goals' as keyof CareerStory, label: 'Motivation & Career Goals', icon: '🎯' },
  ];

  return (
    <div className="profile-input">
      <form onSubmit={handleSubmit} className="input-form">
        <h3>Your Professional Profile</h3>

        {/* Career Category Management */}
        <div className="career-tabs">
          <div className="category-management">
            <label>Career Categories</label>
            <div className="add-category">
              <input
                type="text"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                placeholder="New career category name..."
                disabled={disabled}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCareerCategory())}
              />
              <button
                type="button"
                onClick={addCareerCategory}
                disabled={disabled || !newCategoryName.trim()}
                className="add-button"
              >
                ➕ Add Category
              </button>
            </div>
          </div>

          <div className="tabs">
            {careerCategories.map((categoryName) => (
              <div key={categoryName} className="category-tab-container">
                {editingCategory === categoryName ? (
                  <input
                    type="text"
                    defaultValue={categoryName}
                    onBlur={(e) => renameCareerCategory(categoryName, e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        renameCareerCategory(categoryName, e.currentTarget.value);
                      } else if (e.key === 'Escape') {
                        setEditingCategory(null);
                      }
                    }}
                    autoFocus
                    className="category-edit-input"
                  />
                ) : (
                  <button
                    type="button"
                    className={`tab ${activeCareerTab === categoryName ? 'active' : ''}`}
                    onClick={() => setActiveCareerTab(categoryName)}
                    disabled={disabled}
                  >
                    {getCategoryIcon(categoryName)} {categoryName}
                  </button>
                )}
                <div className="category-actions">
                  <button
                    type="button"
                    onClick={() => setEditingCategory(categoryName)}
                    disabled={disabled}
                    className="edit-category-button"
                    title="Rename category"
                  >
                    ✏️
                  </button>
                  {careerCategories.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCareerCategory(categoryName)}
                      disabled={disabled}
                      className="remove-category-button"
                      title="Remove category"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Story Type Tabs for Active Career */}
          {activeCareerTab && (
            <div className="story-tabs">
              {/* Initiator Field */}
              <div className="initiator-section">
                <label htmlFor="initiator">Content Guidance for {activeCareerTab}</label>
                <textarea
                  id="initiator"
                  value={careerBackground[activeCareerTab]?.initiator || ''}
                  onChange={(e) => handleCareerStoryChange(activeCareerTab, 'initiator', e.target.value)}
                  placeholder={`Provide guidance for how the AI should approach content generation for ${activeCareerTab.toLowerCase()}. For example: "Focus on technical leadership and team management experience" or "Emphasize innovative problem-solving approaches"`}
                  disabled={disabled}
                  rows={3}
                  className="initiator-textarea"
                />
                <div className="initiator-description">
                  This guidance helps the AI understand your preferred approach and tone for this career category.
                </div>
              </div>

              <label>Story Types for {activeCareerTab}</label>
              <div className="tabs">
                {storyTabs.map(({ key, label, icon }) => (
                  <button
                    key={key}
                    type="button"
                    className={`tab ${activeStoryTab === key ? 'active' : ''}`}
                    onClick={() => setActiveStoryTab(key)}
                    disabled={disabled}
                  >
                    {icon} {label}
                  </button>
                ))}
              </div>

              {/* Story Content */}
              <div className="story-content">
                {storyTabs.map(({ key, label, icon }) => {
                  const hasContent = (careerBackground[activeCareerTab]?.[key] || '').trim().length > 0;
                  return (
                    <div key={key} className="story-item">
                      <div className="story-header">
                        <span className="story-icon">{icon}</span>
                        <span className="story-label">{label}</span>
                        {hasContent && <span className="content-indicator">✓</span>}
                      </div>
                      <button
                        type="button"
                        onClick={() => openStoryModal(activeCareerTab, key)}
                        disabled={disabled}
                        className="edit-story-button"
                      >
                        {hasContent ? 'Edit Story' : 'Add Story'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
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

      {/* Story Editing Modal */}
      {showStoryModal && (
        <div className="modal-overlay" onClick={handleStoryModalClose}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {storyTabs.find(tab => tab.key === activeStoryTab)?.icon}{' '}
                {storyTabs.find(tab => tab.key === activeStoryTab)?.label}
              </h3>
              <button
                type="button"
                onClick={handleStoryModalClose}
                className="modal-close"
              >
                ×
              </button>
            </div>
            <div className="modal-subheader">
              <span className="career-context">{activeCareerTab}</span>
            </div>
            <div className="modal-body">
              <textarea
                value={modalStoryContent}
                onChange={(e) => setModalStoryContent(e.target.value)}
                placeholder={`Describe your ${storyTabs.find(tab => tab.key === activeStoryTab)?.label.toLowerCase()} for ${activeCareerTab.toLowerCase()}...`}
                rows={15}
                className="manual-description-textarea"
                autoFocus
              />
            </div>
            <div className="modal-footer">
              <button
                type="button"
                onClick={handleStoryModalClose}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleStoryModalSubmit}
                disabled={!modalStoryContent.trim()}
                className="submit-manual-button"
              >
                Save Story
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileInput;
