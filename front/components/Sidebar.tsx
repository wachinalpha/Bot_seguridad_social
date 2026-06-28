
import React, { useEffect, useState } from 'react';
import { getDocuments, checkHealth } from '../services/geminiService';

interface SidebarProps {
  isOpen: boolean;
  toggle: () => void;
}

interface Document {
  id: string;
  titulo: string;
  url: string;
  summary?: string;
  categoria?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, toggle }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadDocuments();
      checkBackendHealth();
    }
  }, [isOpen]);

  const loadDocuments = async () => {
    setIsLoadingDocs(true);
    try {
      const response = await getDocuments();
      setDocuments(response.documents);
    } catch (error) {
      console.error('Error loading documents:', error);
      setDocuments([]);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  const checkBackendHealth = async () => {
    try {
      await checkHealth();
      setIsBackendHealthy(true);
    } catch (error) {
      setIsBackendHealthy(false);
    }
  };

  return (
    <aside className={`${isOpen ? 'w-80' : 'w-0'} bg-brand-navy border-r border-slate-800 flex flex-col h-full transition-all duration-300 overflow-hidden z-20 shadow-2xl`}>
      <div className="p-6 flex items-center justify-between border-b border-white/10 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-green rounded flex items-center justify-center">
            <svg className="w-5 h-5 text-brand-navy" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" />
            </svg>
          </div>
          <span className="font-bold text-lg tracking-tight text-white">exdata</span>
        </div>
        <button onClick={toggle} className="p-2 text-white/40 hover:text-white rounded-md hover:bg-white/5">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
          </svg>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        <div>
          <h3 className="text-xs font-semibold text-brand-green uppercase tracking-widest mb-4">Misión</h3>
          <p className="text-sm text-slate-300 leading-relaxed italic">
            "Transformamos la complejidad legal en respuestas claras para una seguridad social justa."
          </p>
        </div>

        {/* Backend Status */}
        <div className="flex items-center gap-2 text-xs">
          <div className={`w-2 h-2 rounded-full ${isBackendHealthy ? 'bg-green-400' : isBackendHealthy === false ? 'bg-red-400' : 'bg-yellow-400'}`} />
          <span className="text-slate-400">
            {isBackendHealthy ? 'Conectado' : isBackendHealthy === false ? 'Desconectado' : 'Verificando...'}
          </span>
        </div>

        {/* Documents Section */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">
            Documentos Indexados ({documents.length})
          </h3>
          {isLoadingDocs ? (
            <div className="text-slate-400 text-sm">Cargando...</div>
          ) : documents.length > 0 ? (
            <ul className="space-y-3 max-h-64 overflow-y-auto">
              {documents.map((doc) => (
                <li
                  key={doc.id}
                  className="text-slate-300 text-xs hover:text-brand-green cursor-pointer transition-colors group p-2 rounded hover:bg-white/5"
                  title={doc.summary || doc.titulo}
                >
                  <div className="font-medium truncate">{doc.titulo}</div>
                  {doc.categoria && (
                    <div className="text-[10px] text-slate-500 mt-1">{doc.categoria}</div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-slate-400 text-xs">No hay documentos indexados</div>
          )}
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Chats</h3>
            <span className="text-[10px] text-slate-500 uppercase tracking-wide">Demo</span>
          </div>
          <ul className="space-y-3">
            <li className="flex items-center gap-3 text-slate-200 text-sm bg-white/5 border border-white/10 rounded-lg p-3">
              <svg className="w-4 h-4 text-brand-green shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 4v-4z" />
              </svg>
              <div className="min-w-0">
                <div className="font-medium truncate">Chat actual</div>
                <div className="text-[10px] text-slate-500 mt-1">Sesión temporal</div>
              </div>
            </li>
            <li className="flex items-center justify-between gap-3 text-slate-400 text-sm rounded-lg p-3 border border-dashed border-white/10">
              <div className="flex items-center gap-3 min-w-0">
                <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span className="truncate">Nuevo chat</span>
              </div>
              <span className="text-[10px] text-slate-500 uppercase tracking-wide">Próximamente</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="p-6 border-t border-white/10">
        <p className="text-[10px] text-slate-500 uppercase tracking-widest">Demo institucional</p>
      </div>
    </aside>
  );
};
