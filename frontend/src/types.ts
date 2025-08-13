export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'progress';
  content: string;
  timestamp: Date;
}

export interface ActivityLogEntry {
  id: string;
  type: 'info' | 'tool' | 'error' | 'browser';
  message: string;
  timestamp: Date;
}

export interface WebSocketMessage {
  type: 'response' | 'progress' | 'tool_start' | 'tool_result' | 'browser_action' | 'error';
  content?: string;
  tool?: string;
  step?: number;
  total?: number;
  url?: string;
  action?: string;
  args?: Record<string, any>;
  timestamp?: string;
}

export interface JobSearchRequest {
  query: string;
  experience_years?: number;
  location?: string;
  remote_only: boolean;
}

export interface JobSearchResponse {
  query: string;
  response: string;
  timestamp: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  timestamp: string;
}

export interface ProgressState {
  current: number;
  total: number;
  isActive: boolean;
}

export interface BrowserState {
  status: 'Idle' | 'Initializing' | 'Active' | 'Browsing';
  url: string;
  content: string;
}
