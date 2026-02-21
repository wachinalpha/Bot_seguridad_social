/**
 * Backend API Service
 * 
 * This service communicates with the FastAPI backend instead of using Gemini directly.
 * All AI processing and RAG happens on the Python backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface ChatRequest {
  query: string;
  session_id?: string;
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
  sessionId?: string
): Promise<ChatResponse> => {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Unknown error' }));
    throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
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
  const response = await fetch('http://localhost:8000/health');

  if (!response.ok) {
    throw new Error('Backend is not healthy');
  }

  return response.json();
};