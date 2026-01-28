export enum Role {
  USER = 'user',
  MODEL = 'model',
  SYSTEM = 'system'
}

export interface CanvasSnapshot {
  snapshot_id: number;
  timestamp: number;
  step_id: number | null;
  canvas_text: string;
  patch_text: string | null; // Added to track the logic delta
  hash: string | null;
  meta: {
    patch_applied: boolean;
    restored_from: number | null;
  };
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  timestamp: number;
  proposal?: string | null;
  proposalAccepted?: boolean;
  proposalRejected?: boolean;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  canvas: string;
  sessionStarted: boolean;
  snapshots: CanvasSnapshot[];
  lastSavedAt?: number | null;
}