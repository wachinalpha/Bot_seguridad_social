
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
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-4">Configuración</h3>
          <ul className="space-y-4">
            <li className="flex items-center gap-3 text-slate-300 text-sm hover:text-brand-green cursor-pointer transition-colors group">
              <svg className="w-4 h-4 group-hover:text-brand-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Nueva Conversación
            </li>
            <li className="flex items-center gap-3 text-slate-300 text-sm hover:text-brand-green cursor-pointer transition-colors group">
              <svg className="w-4 h-4 group-hover:text-brand-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 00-2 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Historial Privado
            </li>
          </ul>
        </div>
      </div>

      <div className="p-6 border-t border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-white font-bold">
            EX
          </div>
          <div>
            <p className="text-xs font-bold text-white uppercase tracking-tight">Usuario Pro</p>
            <p className="text-[10px] text-slate-500">plan@exdata.com.ar</p>
          </div>
        </div>
      </div>
    </aside>
  );
};
