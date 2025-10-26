"use client";
import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Brain, 
  Network, 
  Zap, 
  MessageSquare, 
  Activity, 
  Cpu, 
  Database,
  GitBranch,
  Sparkles,
  Radio,
  Satellite,
  Orbit,
  TrendingUp,
  Target,
  Shield,
  Lock,
  Unlock,
  Eye,
  Search,
  Filter,
  Settings
} from "lucide-react";

// Technical Agent Types for Google A2A
type AgentType = "quantum-planner" | "neural-worldview" | "synthetic-personality" | "cognitive-analyzer" | "strategic-optimizer";

interface Agent {
  id: string;
  name: string;
  type: AgentType;
  status: "idle" | "thinking" | "communicating" | "processing";
  lastActivity: Date;
  messageCount: number;
  connections: string[];
  currentThought?: string;
  confidence: number;
  color: string;
  icon: React.ReactNode;
}

interface AgentMessage {
  id: string;
  from: string;
  to: string;
  content: string;
  timestamp: Date;
  type: "thought" | "action" | "query" | "response";
  confidence: number;
}

const AGENTS: Agent[] = [
  {
    id: "quantum-planner",
    name: "Quantum Strategic Planner",
    type: "quantum-planner",
    status: "idle",
    lastActivity: new Date(),
    messageCount: 0,
    connections: ["neural-worldview", "synthetic-personality"],
    confidence: 0.95,
    color: "from-blue-500 to-cyan-500",
    icon: <Brain className="size-5" />
  },
  {
    id: "neural-worldview",
    name: "Neural Worldview Engine",
    type: "neural-worldview", 
    status: "idle",
    lastActivity: new Date(),
    messageCount: 0,
    connections: ["quantum-planner", "cognitive-analyzer"],
    confidence: 0.88,
    color: "from-purple-500 to-pink-500",
    icon: <Network className="size-5" />
  },
  {
    id: "synthetic-personality",
    name: "Synthetic Personality Core",
    type: "synthetic-personality",
    status: "idle", 
    lastActivity: new Date(),
    messageCount: 0,
    connections: ["quantum-planner", "strategic-optimizer"],
    confidence: 0.92,
    color: "from-emerald-500 to-teal-500",
    icon: <Zap className="size-5" />
  },
  {
    id: "cognitive-analyzer",
    name: "Cognitive Analysis Engine",
    type: "cognitive-analyzer",
    status: "idle",
    lastActivity: new Date(),
    messageCount: 0,
    connections: ["neural-worldview", "strategic-optimizer"],
    confidence: 0.87,
    color: "from-orange-500 to-red-500",
    icon: <Cpu className="size-5" />
  },
  {
    id: "strategic-optimizer",
    name: "Strategic Optimization Matrix",
    type: "strategic-optimizer",
    status: "idle",
    lastActivity: new Date(),
    messageCount: 0,
    connections: ["synthetic-personality", "cognitive-analyzer"],
    confidence: 0.91,
    color: "from-violet-500 to-purple-500",
    icon: <Target className="size-5" />
  }
];

export function AdvancedAgentObservatory() {
  const [agents, setAgents] = useState<Agent[]>(AGENTS);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [view, setView] = useState<"lanes" | "graph" | "timeline">("graph");
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Fix hydration issues
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Simulate agent activity
  const simulateAgentActivity = () => {
    if (!isSimulating) return;

    const activeAgents = agents.filter(agent => agent.status !== "idle");
    const idleAgents = agents.filter(agent => agent.status === "idle");
    
    if (idleAgents.length > 0 && Math.random() < 0.3) {
      const randomAgent = idleAgents[Math.floor(Math.random() * idleAgents.length)];
      const targetAgent = randomAgent.connections[Math.floor(Math.random() * randomAgent.connections.length)];
      
      setAgents(prev => prev.map(agent => 
        agent.id === randomAgent.id 
          ? { ...agent, status: "thinking" as const, lastActivity: new Date() }
          : agent
      ));

      // Create a message between agents
      const newMessage: AgentMessage = {
        id: `msg-${Date.now()}`,
        from: randomAgent.id,
        to: targetAgent,
        content: generateAgentThought(randomAgent.type),
        timestamp: new Date(),
        type: "thought",
        confidence: Math.random() * 0.3 + 0.7
      };

      setMessages(prev => [...prev.slice(-49), newMessage]);

      // Update agent status after delay
      setTimeout(() => {
        setAgents(prev => prev.map(agent => 
          agent.id === randomAgent.id 
            ? { ...agent, status: "idle" as const, messageCount: agent.messageCount + 1 }
            : agent
        ));
      }, 2000 + Math.random() * 3000);
    }
  };

  const generateAgentThought = (type: AgentType): string => {
    const thoughts = {
      "quantum-planner": [
        "Analyzing strategic pathways for optimal decision matrix...",
        "Computing probability distributions for future state vectors...",
        "Evaluating multi-dimensional constraint satisfaction algorithms...",
        "Synthesizing quantum decision trees for tactical optimization..."
      ],
      "neural-worldview": [
        "Processing environmental context through neural network layers...",
        "Updating world model with latest sensory input streams...",
        "Correlating temporal patterns across distributed knowledge graphs...",
        "Integrating cross-modal perception data for unified understanding..."
      ],
      "synthetic-personality": [
        "Generating contextual response vectors for human interaction...",
        "Calibrating emotional resonance parameters for optimal engagement...",
        "Synthesizing personality traits based on current conversation context...",
        "Adapting communication style to match user preference patterns..."
      ],
      "cognitive-analyzer": [
        "Performing deep cognitive analysis on input data streams...",
        "Identifying patterns in behavioral data through machine learning...",
        "Correlating insights across multiple analytical dimensions...",
        "Generating predictive models for future behavior patterns..."
      ],
      "strategic-optimizer": [
        "Optimizing resource allocation across multiple objective functions...",
        "Computing Pareto-optimal solutions for multi-criteria decision making...",
        "Balancing trade-offs between efficiency and robustness parameters...",
        "Implementing adaptive algorithms for dynamic optimization..."
      ]
    };
    
    const agentThoughts = thoughts[type];
    return agentThoughts[Math.floor(Math.random() * agentThoughts.length)];
  };

  useEffect(() => {
    if (isSimulating) {
      intervalRef.current = setInterval(simulateAgentActivity, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isSimulating, agents]);

  const toggleSimulation = () => {
    setIsSimulating(!isSimulating);
  };

  const getStatusColor = (status: Agent["status"]) => {
    switch (status) {
      case "idle": return "text-muted-foreground";
      case "thinking": return "text-blue-600";
      case "communicating": return "text-green-600";
      case "processing": return "text-orange-600";
      default: return "text-muted-foreground";
    }
  };

  const getStatusIcon = (status: Agent["status"]) => {
    switch (status) {
      case "idle": return <Shield className="size-4" />;
      case "thinking": return <Brain className="size-4 animate-pulse" />;
      case "communicating": return <Radio className="size-4" />;
      case "processing": return <Cpu className="size-4 animate-spin" />;
      default: return <Shield className="size-4" />;
    }
  };

  if (!isClient) {
    return (
      <div className="rounded-xl border bg-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-6 w-6 rounded-full bg-muted animate-pulse" />
          <div className="h-4 w-48 rounded bg-muted animate-pulse" />
        </div>
        <div className="h-64 rounded-lg bg-muted animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card">
      <div className="flex items-center justify-between border-b p-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <Network className="h-4 w-4 text-primary" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">Agent Observatory</h3>
            <p className="text-sm text-muted-foreground">Multi-agent coordination system</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${isSimulating ? 'bg-green-500 animate-pulse' : 'bg-muted-foreground'}`} />
            <span className="text-sm text-muted-foreground">
              {isSimulating ? 'Active' : 'Standby'}
            </span>
          </div>
          
          <div className="flex rounded-md border p-1">
            {(["graph", "lanes", "timeline"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-sm px-3 py-1 text-sm font-medium transition-colors ${
                  view === v 
                    ? 'bg-primary text-primary-foreground' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                {v === 'graph' ? 'Network' : v === 'lanes' ? 'Agents' : 'Activity'}
              </button>
            ))}
          </div>
          
          <button
            onClick={toggleSimulation}
            className={`inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              isSimulating 
                ? 'bg-destructive/10 text-destructive hover:bg-destructive/20' 
                : 'bg-primary text-primary-foreground hover:bg-primary/90'
            }`}
          >
            {isSimulating ? (
              <>
                <div className="h-2 w-2 rounded-full bg-destructive" />
                Stop
              </>
            ) : (
              <>
                <div className="h-2 w-2 rounded-full bg-green-500" />
                Start
              </>
            )}
          </button>
        </div>
      </div>

      <div className="p-6">
        <AnimatePresence mode="wait">
          {view === "graph" && (
            <motion.div
              key="graph"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative"
            >
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent, index) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`group relative rounded-lg border bg-card/50 p-4 cursor-pointer transition-all hover:shadow-md ${
                      selectedAgent === agent.id ? 'ring-2 ring-primary' : 'hover:border-primary/50'
                    }`}
                    onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${agent.color} shadow-sm`}>
                          {agent.icon}
                        </div>
                        <div>
                          <h4 className="font-medium text-sm">{agent.name}</h4>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            {getStatusIcon(agent.status)}
                            <span className={getStatusColor(agent.status)}>
                              {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <div className="text-xs text-muted-foreground">Confidence</div>
                        <div className="text-sm font-medium">{Math.round(agent.confidence * 100)}%</div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Messages</span>
                        <span className="font-medium">{agent.messageCount}</span>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-muted-foreground">Connections</span>
                        <span className="font-medium">{agent.connections.length}</span>
                      </div>
                    </div>

                    {selectedAgent === agent.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mt-4 pt-4 border-t"
                      >
                        <div className="space-y-3">
                          <div>
                            <div className="text-xs text-muted-foreground mb-2">Connected Agents</div>
                            <div className="flex flex-wrap gap-1">
                              {agent.connections.map((connId) => {
                                const connAgent = agents.find(a => a.id === connId);
                                return (
                                  <span
                                    key={connId}
                                    className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium"
                                  >
                                    {connAgent?.name.split(' ')[0]}
                                  </span>
                                );
                              })}
                            </div>
                          </div>
                          
                          {agent.currentThought && (
                            <div>
                              <div className="text-xs text-muted-foreground mb-2">Current Thought</div>
                              <div className="text-sm text-foreground italic bg-muted/50 rounded-md p-2">
                                "{agent.currentThought}"
                              </div>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {view === "lanes" && (
            <motion.div
              key="lanes"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {agents.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`rounded-lg border bg-card p-4 transition-all hover:shadow-sm ${
                    selectedAgent === agent.id ? 'ring-2 ring-primary' : 'hover:border-primary/50'
                  }`}
                  onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br ${agent.color}`}>
                        {agent.icon}
                      </div>
                      <div>
                        <h4 className="font-medium">{agent.name}</h4>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          {getStatusIcon(agent.status)}
                          <span className={getStatusColor(agent.status)}>
                            {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6 text-sm">
                      <div className="text-right">
                        <div className="text-xs text-muted-foreground">Confidence</div>
                        <div className="font-medium">{Math.round(agent.confidence * 100)}%</div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-muted-foreground">Messages</div>
                        <div className="font-medium">{agent.messageCount}</div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}

          {view === "timeline" && (
            <motion.div
              key="timeline"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-3"
            >
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <div className="text-lg font-medium">No agent communications yet</div>
                  <div className="text-sm text-muted-foreground mt-2">Start simulation to see activity</div>
                </div>
              ) : (
                <div className="space-y-3">
                  {messages.slice(-10).reverse().map((message, index) => {
                    const fromAgent = agents.find(a => a.id === message.from);
                    const toAgent = agents.find(a => a.id === message.to);
                    
                    return (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-start gap-3 p-4 rounded-lg border bg-card/50"
                      >
                        <div className="flex items-center gap-2">
                          <div className={`h-2 w-2 rounded-full ${
                            message.type === 'thought' ? 'bg-blue-500' :
                            message.type === 'action' ? 'bg-green-500' :
                            message.type === 'query' ? 'bg-orange-500' : 'bg-purple-500'
                          }`} />
                          <span className="text-xs text-muted-foreground">
                            {fromAgent?.name.split(' ')[0]} → {toAgent?.name.split(' ')[0]}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="text-sm">{message.content}</div>
                          <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                            <span>
                              {message.timestamp.toLocaleTimeString()}
                            </span>
                            <span>
                              Confidence: {Math.round(message.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
