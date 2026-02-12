/**
 * Workout Recommendation Display Component
 */

import { useState } from 'react';
import { getWorkoutRecommendation, getProgressAnalysis } from '../api/client';
import type {
  WorkoutRecommendation,
  ProgressAnalysis,
  MuscleGroup,
  RecommendationRequest
} from '../types/aiCoach';
import { ApiKeySettings } from './ApiKeySettings';

interface RecommendationPanelProps {
  onClose: () => void;
}

const MUSCLE_GROUPS: { value: MuscleGroup | ''; label: string }[] = [
  { value: '', label: 'Any / Full Body' },
  { value: 'chest', label: 'Chest' },
  { value: 'back', label: 'Back' },
  { value: 'shoulders', label: 'Shoulders' },
  { value: 'biceps', label: 'Biceps' },
  { value: 'triceps', label: 'Triceps' },
  { value: 'legs', label: 'Legs' },
  { value: 'core', label: 'Core' },
];

const EQUIPMENT_OPTIONS = [
  'barbell',
  'dumbbells',
  'cables',
  'machines',
  'pull-up bar',
  'bodyweight',
  'kettlebells',
  'resistance bands',
];

export function RecommendationPanel({ onClose }: RecommendationPanelProps) {
  const [activeTab, setActiveTab] = useState<'recommend' | 'analyze'>('recommend');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showKeySettings, setShowKeySettings] = useState(false);
  const hasApiKey = () => !!localStorage.getItem('anthropic_api_key');

  // Recommendation form state
  const [focusArea, setFocusArea] = useState<MuscleGroup | ''>('');
  const [duration, setDuration] = useState(45);
  const [equipment, setEquipment] = useState<string[]>(['barbell', 'dumbbells', 'cables', 'bodyweight']);

  // Results state
  const [recommendation, setRecommendation] = useState<WorkoutRecommendation | null>(null);
  const [analysis, setAnalysis] = useState<ProgressAnalysis | null>(null);

  const handleEquipmentToggle = (item: string) => {
    setEquipment(prev =>
      prev.includes(item)
        ? prev.filter(e => e !== item)
        : [...prev, item]
    );
  };

  const handleGetRecommendation = async () => {
    setLoading(true);
    setError(null);
    setRecommendation(null);

    try {
      const request: RecommendationRequest = {
        session_duration_minutes: duration,
        equipment_available: equipment,
      };
      if (focusArea) {
        request.focus_area = focusArea;
      }

      const result = await getWorkoutRecommendation(request);
      setRecommendation(result);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Anthropic API key required. Please set your key using the 🔑 button.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to get recommendation');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGetAnalysis = async () => {
    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const result = await getProgressAnalysis();
      setAnalysis(result);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Anthropic API key required. Please set your key using the 🔑 button.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to get analysis');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="recommendation-modal" onClick={e => e.stopPropagation()}>
        <div className="recommendation-header">
          <div className="tab-buttons">
            <button
              className={`tab-btn ${activeTab === 'recommend' ? 'active' : ''}`}
              onClick={() => setActiveTab('recommend')}
            >
              💪 Get Workout
            </button>
            <button
              className={`tab-btn ${activeTab === 'analyze' ? 'active' : ''}`}
              onClick={() => setActiveTab('analyze')}
            >
              📊 Analyze Progress
            </button>
          </div>
          <div className="recommendation-header-actions">
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setShowKeySettings(true)}
              title="API Key Settings"
            >
              {hasApiKey() ? '🔑' : '⚠️ Set Key'}
            </button>
            <button className="btn btn-secondary btn-sm" onClick={onClose}>
              ✕
            </button>
          </div>
        </div>

        <div className="recommendation-content">
          {error && <div className="error-message">{error}</div>}

          {activeTab === 'recommend' && (
            <>
              {!recommendation ? (
                <div className="recommendation-form">
                  <div className="form-group">
                    <label>Focus Area</label>
                    <select
                      value={focusArea}
                      onChange={e => setFocusArea(e.target.value as MuscleGroup | '')}
                    >
                      {MUSCLE_GROUPS.map(mg => (
                        <option key={mg.value} value={mg.value}>
                          {mg.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Session Duration: {duration} minutes</label>
                    <input
                      type="range"
                      min={15}
                      max={120}
                      step={5}
                      value={duration}
                      onChange={e => setDuration(Number(e.target.value))}
                    />
                  </div>

                  <div className="form-group">
                    <label>Available Equipment</label>
                    <div className="equipment-grid">
                      {EQUIPMENT_OPTIONS.map(item => (
                        <label key={item} className="equipment-item">
                          <input
                            type="checkbox"
                            checked={equipment.includes(item)}
                            onChange={() => handleEquipmentToggle(item)}
                          />
                          <span>{item}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <button
                    className="btn btn-primary full-width"
                    onClick={handleGetRecommendation}
                    disabled={loading || equipment.length === 0}
                  >
                    {loading ? 'Generating...' : '🎯 Generate Workout'}
                  </button>
                </div>
              ) : (
                <div className="recommendation-result">
                  <div className="result-header">
                    <h3>{recommendation.title}</h3>
                    <div className="result-meta">
                      <span className="badge">{recommendation.difficulty}</span>
                      <span className="badge">⏱️ {recommendation.estimated_duration_minutes} min</span>
                    </div>
                  </div>

                  <p className="result-description">{recommendation.description}</p>

                  <div className="exercises-list">
                    <h4>Exercises</h4>
                    {recommendation.exercises.map((ex, idx) => (
                      <div key={idx} className="exercise-card">
                        <div className="exercise-name">
                          <strong>{ex.name}</strong>
                          <span className="muscle-badge">{ex.muscle_group}</span>
                        </div>
                        <div className="exercise-details">
                          {ex.sets} sets × {ex.reps}
                          {ex.weight_suggestion && (
                            <span className="weight-suggestion"> @ {ex.weight_suggestion}</span>
                          )}
                        </div>
                        {ex.notes && <div className="exercise-notes">💡 {ex.notes}</div>}
                      </div>
                    ))}
                  </div>

                  {recommendation.tips.length > 0 && (
                    <div className="tips-section">
                      <h4>Tips</h4>
                      <ul>
                        {recommendation.tips.map((tip, idx) => (
                          <li key={idx}>{tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <button
                    className="btn btn-secondary full-width"
                    onClick={() => setRecommendation(null)}
                  >
                    ← Generate Another
                  </button>
                </div>
              )}
            </>
          )}

          {activeTab === 'analyze' && (
            <>
              {!analysis ? (
                <div className="analyze-prompt">
                  <p>
                    Get an AI-powered analysis of your current workout routine.
                    The coach will review your exercises and provide insights on:
                  </p>
                  <ul>
                    <li>✓ Training strengths</li>
                    <li>✓ Areas to improve</li>
                    <li>✓ Muscle balance assessment</li>
                    <li>✓ Actionable recommendations</li>
                  </ul>
                  <button
                    className="btn btn-primary full-width"
                    onClick={handleGetAnalysis}
                    disabled={loading}
                  >
                    {loading ? 'Analyzing...' : '📊 Analyze My Routine'}
                  </button>
                </div>
              ) : (
                <div className="analysis-result">
                  <div className="analysis-summary">
                    <h3>Summary</h3>
                    <p>{analysis.summary}</p>
                  </div>

                  {analysis.muscle_balance_score !== null && analysis.muscle_balance_score !== undefined && (
                    <div className="balance-score">
                      <h4>Muscle Balance Score</h4>
                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{ width: `${analysis.muscle_balance_score}%` }}
                        />
                      </div>
                      <span className="score-value">{analysis.muscle_balance_score}/100</span>
                    </div>
                  )}

                  {analysis.strengths.length > 0 && (
                    <div className="analysis-section strengths">
                      <h4>💪 Strengths</h4>
                      <ul>
                        {analysis.strengths.map((s, idx) => (
                          <li key={idx}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysis.areas_to_improve.length > 0 && (
                    <div className="analysis-section improvements">
                      <h4>🎯 Areas to Improve</h4>
                      <ul>
                        {analysis.areas_to_improve.map((a, idx) => (
                          <li key={idx}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {analysis.recommendations.length > 0 && (
                    <div className="analysis-section recommendations">
                      <h4>📝 Recommendations</h4>
                      <ul>
                        {analysis.recommendations.map((r, idx) => (
                          <li key={idx}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <button
                    className="btn btn-secondary full-width"
                    onClick={() => setAnalysis(null)}
                  >
                    ← Analyze Again
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {showKeySettings && (
          <ApiKeySettings onClose={() => setShowKeySettings(false)} />
        )}
      </div>
    </div>
  );
}

