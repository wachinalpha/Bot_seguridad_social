
/**
 * Este archivo sirve como guía para integrar tu aplicación React con tu backend en Python.
 * Dado que usas Arquitectura Hexagonal, probablemente tengas endpoints REST (FastAPI/Flask).
 */

const API_BASE_URL = 'http://localhost:8000/api/v1'; // Ajusta a tu puerto de Python

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
