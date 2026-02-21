
import React, { useState, useCallback, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { ChatMessage, MessageRole } from './types';
import { sendChatMessage } from './services/geminiService';

const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: MessageRole.BOT,
      text: 'Hola. Soy tu asistente legal especializado en seguridad social de exdata. ¿En qué puedo ayudarte hoy?',
      timestamp: new Date(),
    }
  ]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  // Generate a session ID on first mount
  useEffect(() => {
    // Use a simple timestamp-based session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
  }, []);

  const handleSendMessage = useCallback(async (text: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: MessageRole.USER,
      text,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the real backend API
      const response = await sendChatMessage(text, sessionId);

      // Update session ID from backend response
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id);
      }

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: MessageRole.BOT,
        text: response.answer,
        timestamp: new Date(),
        lawDocuments: response.law_documents,
        confidenceScore: response.confidence_score,
        responseTimeMs: response.response_time_ms,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error generating response:", error);

      // Provide more specific error messages
      let errorText = 'Lo siento, hubo un error al procesar tu solicitud.';

      if (error instanceof Error) {
        if (error.message.includes('fetch')) {
          errorText = '⚠️ No se pudo conectar con el servidor. Asegúrate de que el backend esté corriendo en http://localhost:8000';
        } else {
          errorText = `⚠️ Error: ${error.message}`;
        }
      }

      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: MessageRole.BOT,
        text: errorText,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 text-slate-900">
      <Sidebar
        isOpen={isSidebarOpen}
        toggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      <main className="flex-1 flex flex-col relative">
        <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6 shrink-0 shadow-sm z-10">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6 text-brand-navy" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
              </svg>
            </button>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-brand-navy">Legal<span className="text-brand-green text-2xl leading-none">AI</span></span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Powered by</span>
              <span className="text-sm font-black text-brand-green tracking-tighter">exdata</span>
            </div>
          </div>
        </header>

        <ChatArea
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </main>
    </div>
  );
};

export default App;
