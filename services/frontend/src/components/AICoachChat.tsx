/**
 * AI Coach Chat Interface Component
 */

import { useState, useRef, useEffect } from 'react';
import { chatWithCoach } from '../api/client';
import type { ChatMessage } from '../types/aiCoach';
import { ApiKeySettings } from './ApiKeySettings';

interface AICoachChatProps {
  onClose: () => void;
}

export function AICoachChat({ onClose }: AICoachChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your AI fitness coach. Ask me anything about your workout routine, form tips, or training advice. I can see your current exercises and provide personalized recommendations!",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [includeContext, setIncludeContext] = useState(true);
  const [showKeySettings, setShowKeySettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasApiKey = () => !!localStorage.getItem('anthropic_api_key');

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await chatWithCoach(userMessage, includeContext);
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
    } catch (err: any) {
      if (err?.response?.status === 403) {
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: 'An Anthropic API key is required to use the AI Coach. Please set your key in Settings.',
          },
        ]);
      } else {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: `Sorry, I encountered an error: ${errorMessage}. Please make sure the AI Coach service is running.`,
          },
        ]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQuestions = [
    "What exercises should I add for balance?",
    "How can I improve my bench press?",
    "Am I doing enough volume for back?",
    "What's a good warm-up routine?",
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={e => e.stopPropagation()}>
        <div className="chat-header">
          <div className="chat-header-content">
            <h2>🤖 AI Coach</h2>
            <p>Your personal fitness assistant</p>
          </div>
          <div className="chat-header-actions">
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

        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <div className="message-avatar">
                {msg.role === 'assistant' ? '🤖' : '👤'}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <div className="message-text typing">
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {messages.length === 1 && (
          <div className="suggested-questions">
            <p>Try asking:</p>
            <div className="suggestions-grid">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  className="suggestion-btn"
                  onClick={() => setInput(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="chat-input-container">
          <label className="context-toggle">
            <input
              type="checkbox"
              checked={includeContext}
              onChange={e => setIncludeContext(e.target.checked)}
            />
            <span>Include my workout data</span>
          </label>
          <div className="chat-input-row">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your AI coach anything..."
              disabled={loading}
              rows={2}
            />
            <button
              className="btn btn-primary send-btn"
              onClick={handleSend}
              disabled={!input.trim() || loading}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
        </div>
        {showKeySettings && (
          <ApiKeySettings onClose={() => setShowKeySettings(false)} />
        )}
      </div>
    </div>
  );
}

