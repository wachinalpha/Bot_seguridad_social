
import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, MessageRole } from '../types';

interface ChatAreaProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({ messages, onSendMessage, isLoading }) => {
  const [inputText, setInputText] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim() && !isLoading) {
      onSendMessage(inputText.trim());
      setInputText('');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full min-h-0 bg-slate-50">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-8 md:px-12 space-y-8"
      >
        <div className="max-w-3xl mx-auto space-y-10">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === MessageRole.USER ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[85%]`}>

                <div className={`space-y-2 ${message.role === MessageRole.USER ? 'text-right' : 'text-left'}`}>
                  <div className={`px-6 py-4 rounded-2xl shadow-sm border ${message.role === MessageRole.USER
                    ? 'bg-brand-navy text-white border-brand-navy rounded-tr-none'
                    : 'bg-white border-slate-200 text-slate-800 rounded-tl-none'
                    }`}>
                    <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  </div>



                  <p className="text-[9px] text-slate-400 uppercase font-black tracking-widest">
                    {message.role === MessageRole.USER ? 'Tú' : 'Asistente exdata'} • {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 px-6 py-4 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-brand-green rounded-full animate-bounce"></div>
                <div className="w-1.5 h-1.5 bg-brand-green rounded-full animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-1.5 h-1.5 bg-brand-green rounded-full animate-bounce [animation-delay:0.4s]"></div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="p-4 md:p-8 bg-white border-t border-slate-200 sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-end gap-3 mb-4">
          <div className="flex-1 relative group">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Escribe tu consulta legal aquí..."
              className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 pr-12 focus:outline-none focus:ring-2 focus:ring-brand-green/20 focus:border-brand-green transition-all resize-none max-h-40 min-h-[58px]"
              rows={1}
            />
            <div className="absolute right-4 bottom-4 text-slate-400 group-focus-within:text-brand-green transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </div>
          </div>
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className={`p-4 rounded-2xl transition-all shadow-lg active:scale-95 ${inputText.trim() && !isLoading
              ? 'exdata-gradient text-white hover:brightness-110 shadow-brand-green/20'
              : 'bg-slate-100 text-slate-300 cursor-not-allowed'
              }`}
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </button>
        </form>
        <div className="flex flex-col items-center justify-center gap-1 opacity-60">
          <p className="text-[10px] text-slate-400 uppercase tracking-widest font-black">
            Powered by <span className="text-brand-green">exdata</span>
          </p>
          <p className="text-[8px] text-slate-400 font-medium">
            © {new Date().getFullYear()} EXDATA S.A. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  );
};
