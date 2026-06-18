
/**
 * Este archivo sirve como guía para integrar tu aplicación React con tu backend en Python.
 * Dado que usas Arquitectura Hexagonal, probablemente tengas endpoints REST (FastAPI/Flask).
 */

const configuredApiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_ORIGIN = configuredApiUrl.endsWith('/api/v1')
  ? configuredApiUrl.slice(0, -'/api/v1'.length)
  : configuredApiUrl;
const API_BASE_URL = `${API_ORIGIN}/api/v1`;

export const pythonApi = {
  // Enviar mensaje al modelo RAG en Python
  chat: async (query: string, session_id?: string) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id }),
    });
    return response.json();
  },

  // Subir documento al sistema de vectores
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  // Obtener documentos indexados
  getDocuments: async () => {
    const response = await fetch(`${API_BASE_URL}/documents`);
    return response.json();
  }
};
