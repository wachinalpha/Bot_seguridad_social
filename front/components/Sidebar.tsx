
import React, { useEffect, useState } from 'react';
import {
  checkHealth,
  getDocuments,
  getModels,
  ModelOption,
  ModelsResponse,
  ModelSelection,
} from '../services/geminiService';

interface SidebarProps {
  isOpen: boolean;
  toggle: () => void;
  selectedModels?: ModelSelection;
  onModelSelectionChange: (selection: ModelSelection) => void;
}

interface Document {
  id: string;
  titulo: string;
  url: string;
  summary?: string;
  categoria?: string;
}

type SidebarTab = 'documents' | 'models';

const optionKey = (option: Pick<ModelOption, 'provider' | 'model'>) => `${option.provider}::${option.model}`;

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  toggle,
  selectedModels,
  onModelSelectionChange,
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [activeTab, setActiveTab] = useState<SidebarTab>('documents');
  const [modelsConfig, setModelsConfig] = useState<ModelsResponse | null>(null);
  const [isLoadingModels, setIsLoadingModels] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadDocuments();
      checkBackendHealth();
      loadModels();
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

  const loadModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await getModels();
      setModelsConfig(response);
      if (!selectedModels) {
        onModelSelectionChange(response.active);
      }
    } catch (error) {
      console.error('Error loading models:', error);
    } finally {
      setIsLoadingModels(false);
    }
  };

  const currentSelection = selectedModels || modelsConfig?.active;
  const selectedEmbedding = modelsConfig?.embedding_models.find((option) => (
    currentSelection && option.provider === currentSelection.embedding_provider && option.model === currentSelection.embedding_model
  ));

  const handleEmbeddingChange = (value: string) => {
    const option = modelsConfig?.embedding_models.find((candidate) => optionKey(candidate) === value);
    if (!option || !currentSelection) return;

    onModelSelectionChange({
      ...currentSelection,
      embedding_provider: option.provider,
      embedding_model: option.model,
    });
  };

  const handleGenerationChange = (value: string) => {
    const option = modelsConfig?.generation_models.find((candidate) => optionKey(candidate) === value);
    if (!option || !currentSelection) return;

    onModelSelectionChange({
      ...currentSelection,
      generation_provider: option.provider,
      generation_model: option.model,
    });
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

        <div>
          <div className="grid grid-cols-2 gap-2 mb-4 rounded-xl bg-white/5 p-1 border border-white/10">
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-colors ${activeTab === 'documents' ? 'bg-brand-green text-brand-navy' : 'text-slate-400 hover:text-white'}`}
            >
              Documentos
            </button>
            <button
              onClick={() => setActiveTab('models')}
              className={`px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-wide transition-colors ${activeTab === 'models' ? 'bg-brand-green text-brand-navy' : 'text-slate-400 hover:text-white'}`}
            >
              Modelos
            </button>
          </div>

          {activeTab === 'documents' ? (
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
          ) : (
            <div className="space-y-4">
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">Selección de modelos</h3>
              {isLoadingModels ? (
                <div className="text-slate-400 text-sm">Cargando modelos...</div>
              ) : modelsConfig && currentSelection ? (
                <>
                  <label className="block space-y-2">
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest">Embeddings</span>
                    <select
                      value={optionKey({ provider: currentSelection.embedding_provider, model: currentSelection.embedding_model })}
                      onChange={(event) => handleEmbeddingChange(event.target.value)}
                      className="w-full bg-slate-950 border border-white/10 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-brand-green"
                    >
                      {modelsConfig.embedding_models.map((option) => (
                        <option key={optionKey(option)} value={optionKey(option)}>
                          {option.label} ({option.indexed_documents ?? 0} docs)
                        </option>
                      ))}
                    </select>
                  </label>

                  <label className="block space-y-2">
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest">Generación</span>
                    <select
                      value={optionKey({ provider: currentSelection.generation_provider, model: currentSelection.generation_model })}
                      onChange={(event) => handleGenerationChange(event.target.value)}
                      className="w-full bg-slate-950 border border-white/10 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-brand-green"
                    >
                      {modelsConfig.generation_models.map((option) => (
                        <option key={optionKey(option)} value={optionKey(option)}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>

                  <div className="rounded-lg border border-white/10 bg-white/5 p-3 space-y-2">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-[10px] text-slate-500 uppercase tracking-widest">Corpus</span>
                      <span className="text-xs text-slate-300">{modelsConfig.corpus_version}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 break-all">
                      Índice: {selectedEmbedding?.index_id || modelsConfig.embedding_index_id}
                    </div>
                    {selectedEmbedding?.indexed_documents === 0 && (
                      <p className="text-[11px] leading-relaxed text-amber-300">
                        Este embedding todavía no tiene corpus indexado. Hay que correr index_corpus antes de usarlo.
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <div className="text-slate-400 text-xs">No se pudo cargar la configuración de modelos</div>
              )}
            </div>
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
