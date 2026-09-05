import React, { useState } from 'react';
import { api } from '../api';
import { 
  X, 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  HelpCircle,
  MessageSquare
} from 'lucide-react';

interface AnalystChatDrawerProps {
  investigationId: number;
  isOpen: boolean;
  onClose: () => void;
}

interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
  groundedOn?: string;
  isAi?: boolean;
}

export const AnalystChatDrawer: React.FC<AnalystChatDrawerProps> = ({ 
  investigationId, 
  isOpen, 
  onClose 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      sender: 'assistant',
      text: 'Hello, I am your evidence-grounded investigation assistant. You can ask me why specific transactions were flagged, what rules were triggered, or what actions to examine first.',
      groundedOn: 'Deterministic Case Data'
    }
  ]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (textToSend?: string) => {
    const q = (textToSend || query).trim();
    if (!q || loading) return;

    setQuery('');
    setMessages(prev => [...prev, { sender: 'user', text: q }]);
    setLoading(true);

    try {
      const res = await api.askChat(investigationId, q);
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: res.answer,
          groundedOn: res.grounded_on,
          isAi: res.is_ai
        }
      ]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'assistant',
          text: `Error retrieving evidence-grounded answer: ${err.message}`,
          groundedOn: 'Error Fallback'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "Why was TXN-101 flagged?",
    "Which transactions are connected?",
    "What should I review first?",
    "What information remains unknown?"
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/50 backdrop-blur-sm flex justify-end animate-fade-in transition-all">
      <div className="w-full max-w-lg bg-white dark:bg-[#0b1120] border-l border-slate-200 dark:border-slate-800 h-full flex flex-col justify-between shadow-2xl animate-slide-in-right">
        {/* Header */}
        <div className="p-6 border-b border-slate-200/80 dark:border-slate-800 bg-slate-50/90 dark:bg-slate-900/80 flex items-center justify-between backdrop-blur-md">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border border-purple-200 dark:border-purple-500/30 flex items-center justify-center text-purple-600 dark:text-purple-400 shadow-xs">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-tight flex items-center gap-1.5">
                Evidence-Grounded Assistant
                <Sparkles className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" />
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                Grounding: Case INV-{investigationId} Evidence Packet
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white cursor-pointer transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Chat Messages */}
        <div className="p-6 overflow-y-auto flex-1 space-y-4 text-xs lg:text-sm">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 animate-fade-in ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-purple-100 dark:bg-purple-950/80 border border-purple-200 dark:border-purple-800 flex items-center justify-center text-purple-600 dark:text-purple-400 shrink-0 mt-0.5 shadow-xs">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div className={`max-w-[85%] rounded-2xl p-4 space-y-2 shadow-xs ${
                m.sender === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium'
                  : 'bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 text-slate-800 dark:text-slate-200'
              }`}>
                <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
                {m.groundedOn && (
                  <div className="text-[11px] text-slate-400 dark:text-slate-500 font-mono pt-1.5 border-t border-slate-200/80 dark:border-slate-800 flex items-center gap-1">
                    <span>Source: {m.groundedOn}</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-xl bg-purple-100 dark:bg-purple-950/80 border border-purple-200 dark:border-purple-800 flex items-center justify-center text-purple-600 dark:text-purple-400 shrink-0 shadow-xs">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-4 text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></span>
                <span>Synthesizing grounded answer from evidence...</span>
              </div>
            </div>
          )}
        </div>

        {/* Suggested Quick Prompts */}
        <div className="px-6 py-3 border-t border-slate-200/80 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/50">
          <div className="text-[11px] text-slate-500 dark:text-slate-400 font-mono font-semibold mb-2">Suggested Quick Questions:</div>
          <div className="flex gap-2 flex-wrap">
            {sampleQuestions.map((sq, i) => (
              <button
                key={i}
                onClick={() => handleSend(sq)}
                className="text-xs px-3 py-1.5 rounded-xl bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-all duration-150 cursor-pointer border border-slate-200 dark:border-slate-700 shadow-2xs hover:scale-105 active:scale-95"
              >
                {sq}
              </button>
            ))}
          </div>
        </div>

        {/* Input Box */}
        <div className="p-5 border-t border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#0b1120]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2.5"
          >
            <input
              type="text"
              placeholder="Ask about this investigation's findings..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs lg:text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="p-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer shadow-md shadow-blue-500/20"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
