import { useEffect, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../auth/AuthContext';
import { sendChatMessage, type ChatMessage } from '../api/endpoints';

interface UiMessage {
  role: 'user' | 'model';
  content: string;
  isError?: boolean;
}

const HISTORY_KEY = 'rhythma_chat_history';

function loadHistory(): UiMessage[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as UiMessage[];
    return parsed.filter((m) => m && m.content && typeof m.content === 'string');
  } catch {
    return [];
  }
}

function formatMessage(content: string): ReactNode {
  // Render the small markdown subset the Flutter app supports: **bold**
  // and lines starting with "- " or "* " as bullets.
  const lines = content.split('\n');
  return lines.map((line, i) => {
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const text = line.trim().slice(2);
      return (
        <div key={i} className="msg-bullet">
          • {renderBold(text)}
        </div>
      );
    }
    return <div key={i}>{renderBold(line) || '\u00A0'}</div>;
  });
}

function renderBold(text: string): ReactNode {
  const parts = text.split('**');
  return parts.map((part, i) => (i % 2 === 1 ? <strong key={i}>{part}</strong> : part));
}

function friendlyError(error: unknown, t: (k: string) => string): string {
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosErr = error as {
      response?: { status?: number; data?: { detail?: string } };
    };
    if (axiosErr.response?.status === 429) return t('assistant.rateLimited');
    if (axiosErr.response?.data?.detail) return axiosErr.response.data.detail;
  }
  return t('assistant.errorPrefix');
}

export function AssistantPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();

  const [messages, setMessages] = useState<UiMessage[]>(() => {
    const saved = loadHistory();
    if (saved.length > 0) return saved;
    const name = user?.username ?? 'User';
    return [{ role: 'model', content: t('assistant.welcome', { name }) }];
  });
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, typing]);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || typing) return;

    const next: UiMessage[] = [...messages, { role: 'user', content: trimmed }];
    setMessages(next);
    setInput('');
    setTyping(true);

    const history: ChatMessage[] = next
      .filter((m) => !m.isError)
      .slice(-10)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      const result = await sendChatMessage(trimmed, i18n.language, history);
      const withReply: UiMessage[] = [...next, { role: 'model', content: result.response }];
      setMessages(withReply);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(withReply));
    } catch (error) {
      const withError: UiMessage[] = [
        ...next,
        { role: 'model', content: `${t('assistant.errorPrefix')}: ${friendlyError(error, t)}`, isError: true },
      ];
      setMessages(withError);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(withError));
    } finally {
      setTyping(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    void send(input);
  };

  const showSuggestions = messages.filter((m) => !m.isError).length <= 1;

  return (
    <div className="assistant-page page">
      <header className="page-header assistant-header">
        <div>
          <h1>{t('assistant.title')}</h1>
          <p className="card-sub">{t('assistant.subtitle')}</p>
        </div>
        <select
          className="language-select"
          value={i18n.language.slice(0, 2)}
          onChange={(e) => void i18n.changeLanguage(e.target.value)}
          aria-label="Select AI Assistant Language"
        >
          <option value="en">English (EN)</option>
          <option value="hi">Hindi (हिन्दी)</option>
          <option value="mr">Marathi (मराठी)</option>
          <option value="ta">Tamil (தமிழ்)</option>
          <option value="te">Telugu (తెలుగు)</option>
          <option value="kn">Kannada (ಕನ್ನಡ)</option>
          <option value="ml">Malayalam (മലയാളം)</option>
          <option value="gu">Gujarati (ગુજરાતી)</option>
          <option value="bn">Bengali (বাংলা)</option>
        </select>
      </header>

      <div className="chat-list" ref={listRef}>
        {showSuggestions ? (
          <div className="suggestions">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                className="chip"
                onClick={() => void send(t(`assistant.suggest${n}`))}
              >
                {t(`assistant.suggest${n}`)}
              </button>
            ))}
          </div>
        ) : null}

        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.role}${msg.isError ? ' is-error' : ''}`}>
            {msg.role === 'model' && !msg.isError ? <span className="bubble-avatar">💗</span> : null}
            <div className="bubble-body">{formatMessage(msg.content)}</div>
          </div>
        ))}

        {typing ? (
          <div className="chat-bubble model">
            <span className="bubble-avatar">💗</span>
            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        ) : null}
      </div>

      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t('assistant.inputPlaceholder')}
          aria-label={t('assistant.inputPlaceholder')}
        />
        <button type="submit" className="send-btn" disabled={typing || !input.trim()}>
          {t('assistant.send')}
        </button>
      </form>

      <p className="disclaimer">{t('assistant.disclaimer')}</p>
    </div>
  );
}
