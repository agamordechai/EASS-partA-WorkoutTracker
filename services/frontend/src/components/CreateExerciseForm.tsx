import { useState, FormEvent } from 'react';
import type { CreateExerciseRequest } from '../types/exercise';

interface CreateExerciseFormProps {
  onSubmit: (data: CreateExerciseRequest) => Promise<void>;
}

export function CreateExerciseForm({ onSubmit }: CreateExerciseFormProps) {
  const [name, setName] = useState('');
  const [sets, setSets] = useState(3);
  const [reps, setReps] = useState(10);
  const [weight, setWeight] = useState('');
  const [workoutDay, setWorkoutDay] = useState('A');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!name.trim()) {
      setError('Exercise name is required!');
      return;
    }

    let weightValue: number | null = null;
    if (weight.trim()) {
      const parsed = parseFloat(weight);
      if (isNaN(parsed) || parsed <= 0) {
        setError('Weight must be a valid positive number or empty for bodyweight');
        return;
      }
      weightValue = parsed;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        name: name.trim(),
        sets,
        reps,
        weight: weightValue,
        workout_day: workoutDay,
      });

      const weightDisplay = weightValue ? `${weightValue} kg` : 'Bodyweight';
      setSuccess(`Created exercise: ${name} (${sets} sets x ${reps} reps, ${weightDisplay})`);

      setName('');
      setSets(3);
      setReps(10);
      setWeight('');
      setWorkoutDay('A');
    } catch (err) {
      setError(`Failed to create exercise: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-text-primary mb-4">Add New Exercise</h3>

      {error && (
        <div className="bg-danger/10 border-[1.5px] border-danger/20 text-danger text-sm rounded-xl px-4 py-3 mb-4">
          {error}
        </div>
      )}
      {success && (
        <div className="bg-success/10 border-[1.5px] border-success/20 text-success text-sm rounded-xl px-4 py-3 mb-4">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
          <div className="sm:col-span-2 lg:col-span-1">
            <label htmlFor="create-name" className="block text-xs font-medium text-text-secondary mb-1">
              Exercise Name *
            </label>
            <input
              id="create-name"
              type="text"
              placeholder="e.g., Bench Press"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={isSubmitting}
              className="input"
            />
          </div>

          <div>
            <label htmlFor="create-sets" className="block text-xs font-medium text-text-secondary mb-1">
              Sets *
            </label>
            <input
              id="create-sets"
              type="number"
              min={1}
              max={20}
              value={sets}
              onChange={(e) => setSets(parseInt(e.target.value) || 1)}
              disabled={isSubmitting}
              className="input"
            />
          </div>

          <div>
            <label htmlFor="create-reps" className="block text-xs font-medium text-text-secondary mb-1">
              Reps *
            </label>
            <input
              id="create-reps"
              type="number"
              min={1}
              max={100}
              value={reps}
              onChange={(e) => setReps(parseInt(e.target.value) || 1)}
              disabled={isSubmitting}
              className="input"
            />
          </div>

          <div>
            <label htmlFor="create-weight" className="block text-xs font-medium text-text-secondary mb-1">
              Weight (kg)
            </label>
            <input
              id="create-weight"
              type="text"
              placeholder="Bodyweight"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              disabled={isSubmitting}
              className="input"
            />
          </div>

          <div>
            <label htmlFor="create-workout-day" className="block text-xs font-medium text-text-secondary mb-1">
              Workout Day *
            </label>
            <select
              id="create-workout-day"
              value={workoutDay}
              onChange={(e) => setWorkoutDay(e.target.value)}
              disabled={isSubmitting}
              className="input"
            >
              <option value="None">Daily</option>
              <option value="A">Day A</option>
              <option value="B">Day B</option>
              <option value="C">Day C</option>
              <option value="D">Day D</option>
              <option value="E">Day E</option>
              <option value="F">Day F</option>
              <option value="G">Day G</option>
            </select>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Creating...' : 'Create Exercise'}
        </button>
      </form>
    </div>
  );
}
