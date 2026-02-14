import { ApiKeySettings } from '../components/ApiKeySettings';
import { useAuth } from '../contexts/AuthContext';

export default function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <div className="animate-fadeIn space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-text-primary">Settings</h2>
        <p className="text-text-secondary text-sm mt-1">Manage your account and preferences</p>
      </div>

      {/* Profile */}
      <div className="card">
        <h3 className="text-lg font-semibold text-text-primary mb-4">Profile</h3>
        <div className="flex items-center gap-4">
          {user?.picture_url ? (
            <img
              src={user.picture_url}
              alt=""
              className="w-14 h-14 rounded-full"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-14 h-14 rounded-full bg-primary-muted flex items-center justify-center text-primary text-xl font-semibold">
              {user?.name?.[0]?.toUpperCase() || '?'}
            </div>
          )}
          <div>
            <p className="text-text-primary font-medium">{user?.name}</p>
            <p className="text-text-secondary text-sm">{user?.email}</p>
          </div>
        </div>
      </div>

      {/* API Key */}
      <div className="card">
        <h3 className="text-lg font-semibold text-text-primary mb-4">AI Coach API Key</h3>
        <ApiKeySettings />
      </div>

      {/* Sign out */}
      <div className="card">
        <h3 className="text-lg font-semibold text-text-primary mb-2">Account</h3>
        <p className="text-text-secondary text-sm mb-4">Sign out of your account on this device.</p>
        <button className="btn btn-danger" onClick={logout}>
          Sign Out
        </button>
      </div>
    </div>
  );
}
