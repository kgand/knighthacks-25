/**
 * Chat Types
 * 
 * Extended from existing App.tsx chat UI.
 */

export type MessageRole = "user" | "assistant" | "system" | "tool";

export type MessageStatus = "sending" | "streaming" | "complete" | "error";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  status?: MessageStatus;
  
  // Streaming support
  is_partial?: boolean;
  
  // Tool calls
  tool_calls?: Array<{
    id: string;
    name: string;
    args: Record<string, any>;
    result?: any;
    status: "pending" | "running" | "complete" | "error";
  }>;
  
  // Citations and references
  references?: {
    frame_id?: string;
    cells?: string[];
    agent_events?: string[];
  };
  
  // Metadata
  model?: string;
  latency_ms?: number;
  tokens?: {
    prompt: number;
    completion: number;
  };
}

/**
 * Chat quick action buttons
 */
export type ChatQuickAction = 
  | "explain_current_frame"
  | "why_state_change"
  | "generate_move"
  | "create_bug_report";

export interface ChatQuickActionConfig {
  action: ChatQuickAction;
  label: string;
  icon?: string;
  enabled: boolean;
  tooltip?: string;
}

