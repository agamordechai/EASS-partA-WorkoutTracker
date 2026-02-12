/**
 * Component for managing the user's Anthropic API key.
 */

import { useState, useEffect } from 'react';

const STORAGE_KEY = 'anthropic_api_key';

function maskKey(key: string): string {
  if (key.length <= 12) return '****';
  return `${key.slice(0, 7)}...${key.slice(-4)}`;
}

interface ApiKeySettingsProps {
  onClose: () => void;
}

export function ApiKeySettings({ onClose }: ApiKeySettingsProps) {
  const [key, setKey] = useState('');
  const [savedKey, setSavedKey] = useState<string | null>(null);

  useEffect(() => {
    setSavedKey(localStorage.getItem(STORAGE_KEY));
  }, []);

  const handleSave = () => {
    const trimmed = key.trim();
    if (!trimmed) return;
    localStorage.setItem(STORAGE_KEY, trimmed);
    setSavedKey(trimmed);
    setKey('');
  };

  const handleRemove = () => {
    localStorage.removeItem(STORAGE_KEY);
    setSavedKey(null);
    setKey('');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="api-key-modal" onClick={e => e.stopPropagation()}>
        <div className="api-key-header">
          <h2>API Key Settings</h2>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="api-key-body">
          <p className="api-key-description">
            Enter your Anthropic API key to use the AI Coach. Your key is stored
            locally in your browser and sent directly to the backend per-request.
          </p>

          {savedKey ? (
            <div className="api-key-saved">
              <span className="api-key-masked">{maskKey(savedKey)}</span>
              <button className="btn btn-secondary btn-sm" onClick={handleRemove}>
                Remove
              </button>
            </div>
          ) : (
            <p className="api-key-status">No API key set.</p>
          )}

          <div className="api-key-form">
            <input
              type="password"
              value={key}
              onChange={e => setKey(e.target.value)}
              placeholder="sk-ant-..."
              className="api-key-input"
            />
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={!key.trim()}
            >
              {savedKey ? 'Update Key' : 'Save Key'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
