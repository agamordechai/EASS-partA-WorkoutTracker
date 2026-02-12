/**
 * Login page with Google Sign-In button.
 */

import { useState } from 'react';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  const handleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      setError('No credential received from Google');
      return;
    }
    try {
      setError(null);
      await login(credentialResponse.credential);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Login failed. Please try again.'
      );
    }
  };

  const handleError = () => {
    setError('Google Sign-In failed. Please try again.');
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Workout Tracker</h1>
        <p>Sign in to track your workouts</p>

        <div className="google-btn-wrapper">
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={handleError}
            theme="filled_blue"
            size="large"
            shape="rectangular"
            text="signin_with"
            width="300"
          />
        </div>

        {error && <div className="login-error">{error}</div>}
      </div>
    </div>
  );
}
