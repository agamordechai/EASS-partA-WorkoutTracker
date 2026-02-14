import { useState } from 'react';
import { Metrics } from '../components/Metrics';
import { ExerciseList } from '../components/ExerciseList';
import { CreateExerciseForm } from '../components/CreateExerciseForm';
import { EditExerciseModal } from '../components/EditExerciseModal';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useExercises } from '../hooks/useExercises';
import type { Exercise } from '../types/exercise';

export default function DashboardPage() {
  const { exercises, loading, error, fetchExercises, handleCreate, handleUpdate, handleDelete, handleSeed } = useExercises();
  const [editingExercise, setEditingExercise] = useState<Exercise | null>(null);

  if (error) {
    return (
      <div className="animate-fadeIn">
        <div className="card text-center py-14">
          <div className="w-14 h-14 rounded-full bg-danger/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-7 h-7 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
          </div>
          <h2 className="text-lg font-semibold text-text-primary mb-2">Connection Error</h2>
          <p className="text-text-secondary text-sm mb-1 whitespace-pre-line max-w-md mx-auto">{error}</p>
          <p className="text-text-muted text-xs mb-6">
            Make sure the FastAPI server is running:<br />
            <code className="text-primary font-mono text-xs">uvicorn services.api.src.api:app --reload</code>
          </p>
          <button className="btn btn-primary" onClick={fetchExercises}>Retry Connection</button>
        </div>
      </div>
    );
  }

  if (loading && exercises.length === 0) {
    return <LoadingSpinner message="Loading your workouts..." />;
  }

  // Empty state — no exercises yet
  if (exercises.length === 0) {
    return (
      <div className="animate-fadeIn space-y-6">
        <div className="card text-center py-16 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary-glow via-transparent to-transparent" />
          <div className="relative">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-5">
              <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-text-primary mb-2">Welcome to Workout Tracker</h2>
            <p className="text-text-secondary text-sm mb-8 max-w-sm mx-auto">Start building your routine. Load some samples to explore, or jump right in and add your first exercise.</p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button className="btn btn-primary" onClick={handleSeed}>
                Load Sample Exercises
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => document.getElementById('create-name')?.focus()}
              >
                Start From Scratch
              </button>
            </div>
          </div>
        </div>

        <CreateExerciseForm onSubmit={handleCreate} />
      </div>
    );
  }

  return (
    <div className="animate-fadeIn space-y-5">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Dashboard</h2>
        <button
          className="btn btn-secondary btn-sm"
          onClick={fetchExercises}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Metrics */}
      <Metrics exercises={exercises} />

      {/* Exercise List */}
      <ExerciseList
        exercises={exercises}
        onEdit={setEditingExercise}
        onDelete={handleDelete}
      />

      {/* Add Exercise */}
      <CreateExerciseForm onSubmit={handleCreate} />

      {/* Edit Modal */}
      {editingExercise && (
        <EditExerciseModal
          exercise={editingExercise}
          onSubmit={handleUpdate}
          onCancel={() => setEditingExercise(null)}
        />
      )}
    </div>
  );
}
