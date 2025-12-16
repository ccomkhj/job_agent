import React, { useEffect, useState } from 'react';
import type { AgentStep } from '../types';

interface AgentProgressProps {
  agentSteps: AgentStep[];
  isComplete?: boolean;
}

const AgentProgress: React.FC<AgentProgressProps> = ({ agentSteps, isComplete = false }) => {
  const [animatedSteps, setAnimatedSteps] = useState<AgentStep[]>([]);

  useEffect(() => {
    if (isComplete) {
      // Show all steps as completed when done
      setAnimatedSteps(agentSteps.map(step => ({ ...step, status: 'completed' as const })));
    } else {
      // Animate steps appearing one by one
      setAnimatedSteps([]);
      agentSteps.forEach((step, index) => {
        setTimeout(() => {
          setAnimatedSteps(prev => [...prev, { ...step, status: 'in_progress' as const }]);

          // Mark as completed after a brief delay
          setTimeout(() => {
            setAnimatedSteps(prev =>
              prev.map((s, i) => i === index ? { ...s, status: 'completed' as const } : s)
            );
          }, 1500);
        }, index * 800);
      });
    }
  }, [agentSteps, isComplete]);

  const getStatusIcon = (status: AgentStep['status']) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'in_progress':
        return '🔄';
      case 'completed':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const getStatusColor = (status: AgentStep['status']) => {
    switch (status) {
      case 'pending':
        return '#6b7280';
      case 'in_progress':
        return '#3b82f6';
      case 'completed':
        return '#10b981';
      case 'error':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="agent-progress">
      <div className="agent-progress-header">
        <h4>🤖 AI Agent Collaboration</h4>
        <p>Watch our specialized agents work together to create your content</p>
      </div>

      <div className="agent-steps">
        {animatedSteps.map((step, index) => (
          <div key={index} className={`agent-step ${step.status}`}>
            <div className="agent-step-header">
              <div className="agent-icon" style={{ color: getStatusColor(step.status) }}>
                {getStatusIcon(step.status)}
              </div>
              <div className="agent-info">
                <h5 className="agent-name">{step.agent}</h5>
                <p className="agent-description">{step.description}</p>
              </div>
            </div>

            {step.result && (
              <div className="agent-result">
                <div className="result-summary">
                  {Object.entries(step.result).map(([key, value]) => {
                    // Special handling for suggestions array
                    if (key === 'suggestions' && Array.isArray(value)) {
                      return (
                        <div key={key} className="result-item suggestions">
                          <span className="result-key">Key Suggestions:</span>
                          <div className="suggestions-list">
                            {value.map((suggestion: any, index: number) => (
                              <div key={index} className="suggestion-item">
                                <span className="suggestion-type">{suggestion.type}:</span>
                                <span className="suggestion-text">{suggestion.suggestion}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    }

                    // Special handling for skills list
                    if (key === 'top_skills' && Array.isArray(value)) {
                      return (
                        <div key={key} className="result-item">
                          <span className="result-key">Top Skills:</span>
                          <div className="skills-list">
                            {value.map((skill: string, index: number) => (
                              <span key={index} className="skill-tag">{skill}</span>
                            ))}
                          </div>
                        </div>
                      );
                    }

                    // Special handling for key points
                    if (key === 'key_points' && Array.isArray(value)) {
                      return (
                        <div key={key} className="result-item">
                          <span className="result-key">Key Points Used:</span>
                          <ul className="key-points-list">
                            {value.map((point: string, index: number) => (
                              <li key={index} className="key-point">{point}</li>
                            ))}
                          </ul>
                        </div>
                      );
                    }

                    // Special handling for assumptions
                    if (key === 'key_assumptions' && Array.isArray(value)) {
                      return (
                        <div key={key} className="result-item">
                          <span className="result-key">Key Assumptions:</span>
                          <ul className="assumptions-list">
                            {value.map((assumption: string, index: number) => (
                              <li key={index} className="assumption">{assumption}</li>
                            ))}
                          </ul>
                        </div>
                      );
                    }

                    // Skip these from the main loop since we handle them above
                    if (['suggestions', 'top_skills', 'key_points', 'key_assumptions'].includes(key)) return null;

                    return (
                      <div key={key} className="result-item">
                        <span className="result-key">{key.replace(/_/g, ' ')}:</span>
                        <span className="result-value">{String(value)}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {step.status === 'in_progress' && (
              <div className="progress-indicator">
                <div className="progress-bar">
                  <div className="progress-fill"></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentProgress;