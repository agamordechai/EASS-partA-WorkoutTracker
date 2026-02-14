import { useState } from 'react';
import { getWorkoutRecommendation, getProgressAnalysis } from '../api/client';
import type {
  WorkoutRecommendation,
  ProgressAnalysis,
  MuscleGroup,
  RecommendationRequest
} from '../types/aiCoach';

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
  'barbell', 'dumbbells', 'cables', 'machines',
  'pull-up bar', 'bodyweight', 'kettlebells', 'resistance bands',
];

interface RecommendationPanelProps {
  initialTab?: 'recommend' | 'analyze';
}

export function RecommendationPanel({ initialTab = 'recommend' }: RecommendationPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Recommendation form state
  const [focusArea, setFocusArea] = useState<MuscleGroup | ''>('');
  const [duration, setDuration] = useState(45);
  const [equipment, setEquipment] = useState<string[]>(['barbell', 'dumbbells', 'cables', 'bodyweight']);

  // Results
  const [recommendation, setRecommendation] = useState<WorkoutRecommendation | null>(null);
  const [analysis, setAnalysis] = useState<ProgressAnalysis | null>(null);

  const handleEquipmentToggle = (item: string) => {
    setEquipment(prev =>
      prev.includes(item) ? prev.filter(e => e !== item) : [...prev, item]
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
      if (focusArea) request.focus_area = focusArea;
      const result = await getWorkoutRecommendation(request);
      setRecommendation(result);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setError('Anthropic API key required. Please set your key in Settings.');
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
        setError('Anthropic API key required. Please set your key in Settings.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to get analysis');
      }
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <div className="card">
        <div className="bg-danger/10 border border-danger/20 text-danger text-sm rounded-lg px-4 py-3 mb-4">
          {error}
        </div>
        <button className="btn btn-secondary" onClick={() => setError(null)}>Try Again</button>
      </div>
    );
  }

  // ── Recommend tab ──
  if (initialTab === 'recommend') {
    if (recommendation) {
      return (
        <div className="card space-y-4">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">{recommendation.title}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-primary-muted text-primary">
                {recommendation.difficulty}
              </span>
              <span className="text-xs text-text-muted">
                {recommendation.estimated_duration_minutes} min
              </span>
            </div>
          </div>

          <p className="text-sm text-text-secondary">{recommendation.description}</p>

          <div className="space-y-2">
            <h4 className="text-sm font-medium text-text-primary">Exercises</h4>
            {recommendation.exercises.map((ex, idx) => (
              <div key={idx} className="bg-surface-light rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-text-primary">{ex.name}</span>
                  <span className="px-2 py-0.5 rounded text-xs bg-surface text-text-muted">{ex.muscle_group}</span>
                </div>
                <p className="text-xs text-text-secondary">
                  {ex.sets} sets x {ex.reps}
                  {ex.weight_suggestion && <span className="text-primary ml-1">@ {ex.weight_suggestion}</span>}
                </p>
                {ex.notes && <p className="text-xs text-text-muted mt-1">{ex.notes}</p>}
              </div>
            ))}
          </div>

          {recommendation.tips.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-text-primary mb-2">Tips</h4>
              <ul className="space-y-1">
                {recommendation.tips.map((tip, idx) => (
                  <li key={idx} className="text-xs text-text-secondary flex gap-2">
                    <span className="text-primary shrink-0">-</span>
                    {tip}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <button className="btn btn-secondary w-full" onClick={() => setRecommendation(null)}>
            Generate Another
          </button>
        </div>
      );
    }

    return (
      <div className="card space-y-4">
        <div>
          <label className="block text-xs font-medium text-text-secondary mb-1">Focus Area</label>
          <select value={focusArea} onChange={e => setFocusArea(e.target.value as MuscleGroup | '')} className="input">
            {MUSCLE_GROUPS.map(mg => (
              <option key={mg.value} value={mg.value}>{mg.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-text-secondary mb-1">
            Duration: {duration} minutes
          </label>
          <input
            type="range"
            min={15}
            max={120}
            step={5}
            value={duration}
            onChange={e => setDuration(Number(e.target.value))}
            className="w-full accent-primary"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-text-secondary mb-2">Available Equipment</label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {EQUIPMENT_OPTIONS.map(item => (
              <label
                key={item}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs cursor-pointer transition-colors border
                  ${equipment.includes(item)
                    ? 'bg-primary-muted border-primary/30 text-primary'
                    : 'bg-surface-light border-border text-text-secondary hover:border-text-muted'}`}
              >
                <input
                  type="checkbox"
                  checked={equipment.includes(item)}
                  onChange={() => handleEquipmentToggle(item)}
                  className="sr-only"
                />
                {item}
              </label>
            ))}
          </div>
        </div>

        <button
          className="btn btn-primary w-full"
          onClick={handleGetRecommendation}
          disabled={loading || equipment.length === 0}
        >
          {loading ? 'Generating...' : 'Generate Workout'}
        </button>
      </div>
    );
  }

  // ── Analyze tab ──
  if (analysis) {
    return (
      <div className="card space-y-4">
        <div>
          <h3 className="text-sm font-medium text-text-primary mb-1">Summary</h3>
          <p className="text-sm text-text-secondary">{analysis.summary}</p>
        </div>

        {analysis.muscle_balance_score !== null && analysis.muscle_balance_score !== undefined && (
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">Muscle Balance Score</h4>
            <div className="w-full h-2 bg-surface-light rounded-full overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all duration-500"
                style={{ width: `${analysis.muscle_balance_score}%` }}
              />
            </div>
            <p className="text-xs text-text-muted mt-1">{analysis.muscle_balance_score}/100</p>
          </div>
        )}

        {analysis.strengths.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-1">Strengths</h4>
            <ul className="space-y-1">
              {analysis.strengths.map((s, idx) => (
                <li key={idx} className="text-xs text-text-secondary flex gap-2">
                  <span className="text-success shrink-0">+</span>{s}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis.areas_to_improve.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-1">Areas to Improve</h4>
            <ul className="space-y-1">
              {analysis.areas_to_improve.map((a, idx) => (
                <li key={idx} className="text-xs text-text-secondary flex gap-2">
                  <span className="text-danger shrink-0">-</span>{a}
                </li>
              ))}
            </ul>
          </div>
        )}

        {analysis.recommendations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-1">Recommendations</h4>
            <ul className="space-y-1">
              {analysis.recommendations.map((r, idx) => (
                <li key={idx} className="text-xs text-text-secondary flex gap-2">
                  <span className="text-primary shrink-0">*</span>{r}
                </li>
              ))}
            </ul>
          </div>
        )}

        <button className="btn btn-secondary w-full" onClick={() => setAnalysis(null)}>
          Analyze Again
        </button>
      </div>
    );
  }

  return (
    <div className="card space-y-4">
      <p className="text-sm text-text-secondary">
        Get an AI-powered analysis of your current workout routine. The coach will review your exercises and provide insights on:
      </p>
      <ul className="space-y-1 text-sm text-text-secondary">
        <li className="flex gap-2"><span className="text-success">+</span> Training strengths</li>
        <li className="flex gap-2"><span className="text-primary">*</span> Areas to improve</li>
        <li className="flex gap-2"><span className="text-primary">*</span> Muscle balance assessment</li>
        <li className="flex gap-2"><span className="text-primary">*</span> Actionable recommendations</li>
      </ul>
      <button
        className="btn btn-primary w-full"
        onClick={handleGetAnalysis}
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Analyze My Routine'}
      </button>
    </div>
  );
}
