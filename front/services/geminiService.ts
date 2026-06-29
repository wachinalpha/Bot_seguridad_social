/**
 * Backend API Service
 * 
 * This service communicates with the FastAPI backend instead of using Gemini directly.
 * All AI processing and RAG happens on the Python backend.
 */

const configuredApiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_ORIGIN = configuredApiUrl.endsWith('/api/v1')
  ? configuredApiUrl.slice(0, -'/api/v1'.length)
  : configuredApiUrl;
const API_BASE_URL = `${API_ORIGIN}/api/v1`;

export interface ChatRequest {
  query: string;
  session_id?: string;
  model_selection?: ModelSelection;
}

export interface ModelSelection {
  embedding_provider: string;
  embedding_model: string;
  generation_provider: string;
  generation_model: string;
}

export interface ModelOption {
  provider: string;
  model: string;
  label: string;
  index_id?: string | null;
  collection_name?: string | null;
  indexed_documents?: number | null;
}

export interface ModelsResponse {
  active: ModelSelection;
  corpus_version: string;
  embedding_index_id: string;
  indexed_documents: number;
  embedding_models: ModelOption[];
  generation_models: ModelOption[];
}

export interface LawDocument {
  id: string;
  titulo: string;
  url: string;
  summary?: string;
  metadata: Record<string, any>;
}

export interface ChatResponse {
  answer: string;
  law_documents: LawDocument[];
  confidence_score: number;
  response_time_ms: number;
  session_id: string;
}

export interface DocumentListResponse {
  documents: Array<{
    id: string;
    titulo: string;
    url: string;
    summary?: string;
    categoria?: string;
  }>;
  total: number;
}

/**
 * Send a chat message to the backend RAG system
 */
export const sendChatMessage = async (
  query: string,
  sessionId?: string,
  modelSelection?: ModelSelection
): Promise<ChatResponse> => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      session_id: sessionId,
      model_selection: modelSelection,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get active and available AI models
 */
export const getModels = async (): Promise<ModelsResponse> => {
  const response = await fetch(`${API_BASE_URL}/models`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get list of all indexed documents
 */
export const getDocuments = async (): Promise<DocumentListResponse> => {
  const response = await fetch(`${API_BASE_URL}/documents`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get details of a specific document
 */
export const getDocumentById = async (lawId: string): Promise<LawDocument> => {
  const response = await fetch(`${API_BASE_URL}/documents/${lawId}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Check backend health status
 */
export const checkHealth = async (): Promise<{
  status: string;
  version: string;
  services: Record<string, string>;
}> => {
  const response = await fetch(`${API_ORIGIN}/health`);

  if (!response.ok) {
    throw new Error('Backend is not healthy');
  }

  return response.json();
};
