
export enum MessageRole {
  USER = 'user',
  BOT = 'bot'
}

export interface Source {
  id: string;
  title: string;
  content: string;
  type: 'pdf' | 'text' | 'law';
  uploadDate: Date;
}

export interface LawDocument {
  id: string;
  titulo: string;
  url: string;
  summary?: string;
  metadata: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  timestamp: Date;
  sources?: string[]; // IDs of sources cited
  // Backend response metadata
  lawDocument?: LawDocument;
  confidenceScore?: number;
  cacheUsed?: boolean;
  cacheId?: string;
  responseTimeMs?: number;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
}
