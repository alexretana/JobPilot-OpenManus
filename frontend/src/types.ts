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

// Timeline API Types
export enum TimelineEventType {
  JOB_SAVED = 'JOB_SAVED',
  APPLICATION_SUBMITTED = 'APPLICATION_SUBMITTED',
  INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED',
  INTERVIEW_COMPLETED = 'INTERVIEW_COMPLETED',
  STATUS_CHANGED = 'STATUS_CHANGED',
  OFFER_RECEIVED = 'OFFER_RECEIVED',
  OFFER_ACCEPTED = 'OFFER_ACCEPTED',
  OFFER_DECLINED = 'OFFER_DECLINED',
  CUSTOM_EVENT = 'CUSTOM_EVENT',
}

export interface TimelineEvent {
  id: string;
  job_id?: string;
  application_id?: string;
  user_profile_id: string;
  event_type: TimelineEventType;
  title: string;
  description?: string;
  event_data: Record<string, any>;
  event_date: string;
  is_milestone: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTimelineEventRequest {
  event_type: TimelineEventType;
  title: string;
  description?: string;
  job_id?: string;
  application_id?: string;
  event_data?: Record<string, any>;
  event_date?: string;
  is_milestone: boolean;
}

export interface CreateCustomEventRequest {
  title: string;
  description?: string;
  job_id?: string;
  application_id?: string;
  event_data?: Record<string, any>;
  event_date?: string;
  is_milestone: boolean;
}

export interface UpdateTimelineEventRequest {
  title?: string;
  description?: string;
  event_data?: Record<string, any>;
  event_date?: string;
  is_milestone?: boolean;
}

// Re-export skill bank types
export * from './types/skillBank';
