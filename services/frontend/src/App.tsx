/**
 * Main App component - Workout Tracker Dashboard
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Metrics,
  ExerciseList,
  CreateExerciseForm,
  EditExerciseModal,
  AICoachChat,
  RecommendationPanel,
} from './components';
import {
  listExercises,
  createExercise,
  updateExercise,
  deleteExercise,
  seedExercises,
} from './api/client';
import type { Exercise, CreateExerciseRequest, UpdateExerciseRequest } from './types/exercise';
import { useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import './App.css';

function App() {
  const { user, loading: authLoading, isAuthenticated, logout } = useAuth();
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingExercise, setEditingExercise] = useState<Exercise | null>(null);
  const [showAIChat, setShowAIChat] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);

  // Fetch exercises
  const fetchExercises = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listExercises({ page_size: 200 });
      setExercises(data.items);
    } catch (err) {
      setError(
        `Failed to connect to the API. Is the backend running?\n${
          err instanceof Error ? err.message : 'Unknown error'
        }`
      );
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load and auto-refresh every 30 seconds (only when authenticated)
  useEffect(() => {
    if (!isAuthenticated) return;
    fetchExercises();
    const interval = setInterval(fetchExercises, 30000);
    return () => clearInterval(interval);
  }, [fetchExercises, isAuthenticated]);

  // Handle create exercise
  const handleCreate = async (data: CreateExerciseRequest) => {
    await createExercise(data);
    await fetchExercises();
  };

  // Handle update exercise
  const handleUpdate = async (exerciseId: number, data: UpdateExerciseRequest) => {
    await updateExercise(exerciseId, data);
    await fetchExercises();
  };

  // Handle delete exercise
  const handleDelete = async (exerciseId: number) => {
    try {
      await deleteExercise(exerciseId);
      await fetchExercises();
    } catch (err) {
      alert(`Failed to delete: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  // Show loading spinner while checking auth
  if (authLoading) {
    return (
      <div className="app">
        <main className="app-main" style={{ gridColumn: '1 / -1' }}>
          <div className="loading">Loading...</div>
        </main>
      </div>
    );
  }

  // Not authenticated — show login page
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  if (error) {
    return (
      <div className="app">
        <header className="app-header">
          <div className="header-content">
            <div>
              <h1>Workout Tracker Dashboard</h1>
              <p>View, create, and manage your workout exercises</p>
            </div>
            <div className="user-header">
              {user?.picture_url && (
                <img src={user.picture_url} alt="" className="user-avatar" referrerPolicy="no-referrer" />
              )}
              <span className="user-name">{user?.name}</span>
              <button className="btn btn-secondary btn-sm" onClick={logout}>Sign out</button>
            </div>
          </div>
        </header>
        <main className="app-main">
          <div className="error-container">
            <div className="error-message">{error}</div>
            <div className="info-message">
              <p>Make sure the FastAPI server is running:</p>
              <pre>uvicorn services.api.src.api:app --reload</pre>
            </div>
            <button className="btn btn-primary" onClick={fetchExercises}>
              Retry Connection
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>Workout Tracker Dashboard</h1>
            <p>View, create, and manage your workout exercises</p>
          </div>
          <div className="user-header">
            {user?.picture_url && (
              <img src={user.picture_url} alt="" className="user-avatar" referrerPolicy="no-referrer" />
            )}
            <span className="user-name">{user?.name}</span>
            <button className="btn btn-secondary btn-sm" onClick={logout}>Sign out</button>
          </div>
        </div>
      </header>

      <aside className="sidebar">
        <h2>Actions</h2>
        <button
          className="btn btn-primary full-width"
          onClick={fetchExercises}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>

        <div className="sidebar-section">
          <h3>AI Coach</h3>
          <button
            className="btn btn-coach full-width"
            onClick={() => setShowAIChat(true)}
          >
            Chat with Coach
          </button>
          <button
            className="btn btn-coach full-width"
            onClick={() => setShowRecommendations(true)}
          >
            Get Recommendations
          </button>
        </div>

        <p className="sidebar-tip">Tip: Data refreshes automatically every 30 seconds</p>
      </aside>

      <main className="app-main">
        {loading && exercises.length === 0 ? (
          <div className="loading">Loading exercises...</div>
        ) : (
          <>
            {exercises.length > 0 ? (
              <>
                <Metrics exercises={exercises} />
                <hr className="divider" />
                <ExerciseList
                  exercises={exercises}
                  onEdit={setEditingExercise}
                  onDelete={handleDelete}
                />
              </>
            ) : (
              <div className="welcome-prompt">
                <h2>Welcome to Workout Tracker!</h2>
                <p>How would you like to get started?</p>
                <div className="welcome-buttons">
                  <button
                    className="btn btn-primary"
                    onClick={async () => {
                      await seedExercises();
                      await fetchExercises();
                    }}
                  >
                    Load sample exercises
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      const el = document.querySelector('.form-section');
                      el?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    Start from scratch
                  </button>
                </div>
              </div>
            )}

            <hr className="divider" />

            <CreateExerciseForm onSubmit={handleCreate} />

            {editingExercise && (
              <EditExerciseModal
                exercise={editingExercise}
                onSubmit={handleUpdate}
                onCancel={() => setEditingExercise(null)}
              />
            )}

            {showAIChat && (
              <AICoachChat onClose={() => setShowAIChat(false)} />
            )}

            {showRecommendations && (
              <RecommendationPanel onClose={() => setShowRecommendations(false)} />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
