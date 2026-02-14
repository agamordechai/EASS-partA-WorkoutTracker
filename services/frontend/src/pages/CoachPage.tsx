import { useState } from 'react';
import { AICoachChat } from '../components/AICoachChat';
import { RecommendationPanel } from '../components/RecommendationPanel';

type Tab = 'chat' | 'workout' | 'progress';

export default function CoachPage() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  const tabs: { id: Tab; label: string }[] = [
    { id: 'chat', label: 'Chat' },
    { id: 'workout', label: 'Workout Generator' },
    { id: 'progress', label: 'Progress Analysis' },
  ];

  return (
    <div className="animate-fadeIn space-y-5">
      <h2 className="text-xl font-bold text-text-primary">AI Coach</h2>

      {/* Tab bar — iOS segmented control style */}
      <div className="card p-1 flex gap-1">
        {tabs.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex-1 px-4 py-3 rounded-[0.75rem] text-[15px] font-semibold transition-all duration-200 ${
              activeTab === id
                ? 'bg-surface-light text-text-primary shadow-sm'
                : 'text-text-muted hover:text-text-secondary'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {activeTab === 'chat' && <AICoachChat />}
      {activeTab === 'workout' && <RecommendationPanel initialTab="recommend" />}
      {activeTab === 'progress' && <RecommendationPanel initialTab="analyze" />}
    </div>
  );
}
