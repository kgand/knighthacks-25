/**
 * Mock Data for Development
 * 
 * Since backend APIs don't exist yet, this provides realistic mock data
 * for all dashboard surfaces.
 */

import type {
  PipelineFrameEvent,
  AgentEvent,
  CameraFeed,
  AgentMetadata,
  ConversationThread,
} from "../types";

/**
 * Generate mock pipeline events
 */
export function generateMockPipelineEvents(count: number): PipelineFrameEvent[] {
  const events: PipelineFrameEvent[] = [];
  const baseTime = Date.now() - count * 33; // 30 FPS = 33ms per frame

  const pieces = ["R", "N", "B", "Q", "K", "P", "r", "n", "b", "q", "k", "p", "0"];
  const cells = [
    "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8",
    "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8",
    "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8",
    "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8",
    "e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8",
    "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8",
    "h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8",
  ];

  for (let i = 0; i < count; i++) {
    const timestamp = baseTime + i * 33;
    const hasAnomaly = Math.random() < 0.05; // 5% chance of anomaly

    events.push({
      frame_id: `frame_${timestamp}`,
      timestamp,
      stage_timings: {
        preprocess_ms: 2 + Math.random() * 3,
        board_detect_ms: 5 + Math.random() * 5,
        grid_fit_ms: 3 + Math.random() * 2,
        crop_ms: 1 + Math.random() * 2,
        classify_ms: 15 + Math.random() * 10,
        postprocess_ms: 2 + Math.random() * 3,
      },
      board_geometry: {
        corners: [
          [120, 80],
          [520, 85],
          [515, 475],
          [115, 470],
        ],
        reprojection_error: Math.random() * 2,
      },
      cell_scores: cells.slice(0, 32 + Math.floor(Math.random() * 32)).map((cell) => ({
        cell,
        top1_class: pieces[Math.floor(Math.random() * pieces.length)],
        top1_confidence: hasAnomaly && Math.random() < 0.2 ? 0.3 + Math.random() * 0.3 : 0.7 + Math.random() * 0.3,
        top_k: pieces.slice(0, 3).map((cls, idx) => ({
          class: cls,
          confidence: 1 - idx * 0.2 - Math.random() * 0.1,
        })),
      })),
      accepted_board_state: {
        fen: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        last_move: i > 0 ? "e2e4" : undefined,
      },
      anomalies: hasAnomaly
        ? [
            {
              type: Math.random() < 0.5 ? "low_confidence" : "corner_drift",
              severity: Math.random() < 0.7 ? "warning" : "error",
              message: "Low confidence on cell d4 (0.42)",
              affected_cells: ["d4"],
            },
          ]
        : undefined,
    });
  }

  return events;
}

/**
 * Generate mock agent events
 */
export function generateMockAgentEvents(count: number): AgentEvent[] {
  const events: AgentEvent[] = [];
  const baseTime = Date.now() - count * 500; // ~2 events per second

  const agents = ["perception", "board-reconstruction", "rules-engine", "planner"];
  const tools = ["explain_frame", "validate_move", "get_legal_moves", "generate_fen"];

  for (let i = 0; i < count; i++) {
    const timestamp = baseTime + i * 500;
    const agent = agents[Math.floor(Math.random() * agents.length)];
    const isToolCall = Math.random() < 0.3;

    if (isToolCall) {
      // Tool call
      events.push({
        id: `event_${timestamp}_call`,
        timestamp,
        agent,
        role: agent as any,
        kind: "tool_call",
        tool: tools[Math.floor(Math.random() * tools.length)],
        args: { frame_id: `frame_${timestamp}` },
        parent_id: i > 0 ? `event_${baseTime + (i - 1) * 500}` : undefined,
        thread_id: `thread_${Math.floor(i / 5)}`,
      });
      // Tool result
      events.push({
        id: `event_${timestamp}_result`,
        timestamp: timestamp + 100,
        agent,
        role: agent as any,
        kind: "tool_result",
        result: { success: true },
        parent_id: `event_${timestamp}_call`,
        thread_id: `thread_${Math.floor(i / 5)}`,
        latency_ms: 100,
      });
    } else {
      // Message
      events.push({
        id: `event_${timestamp}`,
        timestamp,
        agent,
        role: agent as any,
        kind: "message",
        content: `Agent ${agent} processed frame ${i}`,
        parent_id: i > 0 ? `event_${baseTime + (i - 1) * 500}` : undefined,
        thread_id: `thread_${Math.floor(i / 5)}`,
        latency_ms: 50 + Math.random() * 200,
      });
    }
  }

  return events;
}

/**
 * Mock camera feeds
 */
export const mockCameraFeeds: Record<string, CameraFeed> = {
  "robot-arm": {
    id: "robot-arm",
    label: "Robot Arm Camera",
    protocol: "static",
    resolution: { width: 640, height: 480 },
    fps: 30,
    health: "connected",
    latency_ms: 45,
  },
  "top-down": {
    id: "top-down",
    label: "Top-Down Board View",
    protocol: "static",
    resolution: { width: 1280, height: 720 },
    fps: 30,
    health: "connected",
    latency_ms: 38,
  },
};

/**
 * Mock chat messages
 */
export const mockChatMessages = [
  {
    id: "msg_1",
    role: "assistant" as const,
    content: "Hello! I'm your ChessOps assistant. I can help you understand what's happening with the chess detection pipeline.",
    timestamp: Date.now() - 60000,
    status: "complete" as const,
  },
  {
    id: "msg_2",
    role: "user" as const,
    content: "What's the current board state?",
    timestamp: Date.now() - 50000,
    status: "complete" as const,
  },
  {
    id: "msg_3",
    role: "assistant" as const,
    content: "The current board state is the starting position. FEN: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    timestamp: Date.now() - 45000,
    status: "complete" as const,
  },
];

/**
 * Mock agent metadata
 */
export const mockAgentMetadata: AgentMetadata[] = [
  {
    id: "perception",
    role: "perception",
    label: "Perception Agent",
    description: "Processes camera frames and detects board state",
    status: "idle",
    color: "#06b6d4",
  },
  {
    id: "board-reconstruction",
    role: "board-reconstruction",
    label: "Board Reconstruction",
    description: "Converts detections to FEN strings",
    status: "idle",
    color: "#3b82f6",
  },
  {
    id: "rules-engine",
    role: "rules-engine",
    label: "Rules Engine",
    description: "Validates moves and board states",
    status: "idle",
    color: "#8b5cf6",
  },
  {
    id: "planner",
    role: "planner",
    label: "Planner",
    description: "Plans robot arm movements",
    status: "idle",
    color: "#ec4899",
  },
];

/**
 * Mock conversation threads
 */
export const mockConversationThreads: ConversationThread[] = [
  {
    thread_id: "thread_0",
    label: "Initial board detection",
    agents: ["perception", "board-reconstruction"],
    event_count: 5,
    start_timestamp: Date.now() - 120000,
    end_timestamp: Date.now() - 100000,
    status: "complete",
  },
  {
    thread_id: "thread_1",
    label: "Move validation",
    agents: ["rules-engine", "planner"],
    event_count: 8,
    start_timestamp: Date.now() - 60000,
    status: "active",
  },
];

