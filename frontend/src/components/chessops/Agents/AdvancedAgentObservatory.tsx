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
  const [view, setView] = useState<"lanes" | "graph" | "timeline">("lanes");
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

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
      case "idle": return "text-zinc-400";
      case "thinking": return "text-blue-400";
      case "communicating": return "text-green-400";
      case "processing": return "text-orange-400";
      default: return "text-zinc-400";
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

  return (
    <div className="rounded-2xl bg-zinc-950 shadow-soft ring-1 ring-white/10 p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Orbit className="size-6 text-fuchsia-400" />
            <motion.div
              className="absolute inset-0"
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
            >
              <Satellite className="size-3 text-fuchsia-300" />
            </motion.div>
          </div>
          <h3 className="text-lg font-semibold">A2A Agent Observatory</h3>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isSimulating ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-500'}`} />
            <span className="text-xs text-zinc-400">
              {isSimulating ? 'Active' : 'Standby'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={toggleSimulation}
            className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${
              isSimulating 
                ? 'bg-red-500/20 text-red-300 hover:bg-red-500/25' 
                : 'bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/25'
            }`}
          >
            {isSimulating ? 'Stop Simulation' : 'Start Simulation'}
          </button>
          
          <div className="flex rounded-lg bg-zinc-800 p-1">
            {(["lanes", "graph", "timeline"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-md px-2 py-1 text-xs capitalize transition-colors ${
                  view === v ? 'bg-white/10 text-white' : 'text-zinc-400 hover:text-white'
                }`}
              >
                {v}
              </button>
            ))}
          </div>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {view === "lanes" && (
          <motion.div
            key="lanes"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {agents.map((agent) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                whileHover={{ scale: 1.02 }}
                className={`rounded-xl border border-white/10 p-4 cursor-pointer transition-all ${
                  selectedAgent === agent.id ? 'ring-2 ring-fuchsia-500/50' : 'hover:border-white/20'
                }`}
                onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-gradient-to-r ${agent.color}`}>
                      {agent.icon}
                    </div>
                    <div>
                      <h4 className="font-medium text-sm">{agent.name}</h4>
                      <div className="flex items-center gap-2 text-xs text-zinc-400">
                        {getStatusIcon(agent.status)}
                        <span className={getStatusColor(agent.status)}>
                          {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-xs text-zinc-400">Confidence</div>
                      <div className="text-sm font-medium">{Math.round(agent.confidence * 100)}%</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-zinc-400">Messages</div>
                      <div className="text-sm font-medium">{agent.messageCount}</div>
                    </div>
                  </div>
                </div>

                {selectedAgent === agent.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-white/10"
                  >
                    <div className="space-y-3">
                      <div>
                        <div className="text-xs text-zinc-400 mb-2">Connections</div>
                        <div className="flex gap-2">
                          {agent.connections.map((connId) => {
                            const connAgent = agents.find(a => a.id === connId);
                            return (
                              <span
                                key={connId}
                                className="px-2 py-1 bg-zinc-800 rounded-md text-xs"
                              >
                                {connAgent?.name.split(' ')[0]}
                              </span>
                            );
                          })}
                        </div>
                      </div>
                      
                      {agent.currentThought && (
                        <div>
                          <div className="text-xs text-zinc-400 mb-2">Current Thought</div>
                          <div className="text-sm text-zinc-300 italic">
                            "{agent.currentThought}"
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </motion.div>
        )}

        {view === "graph" && (
          <motion.div
            key="graph"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="relative h-96 bg-zinc-900 rounded-lg overflow-hidden"
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Network className="size-12 text-zinc-600 mx-auto mb-4" />
                <div className="text-zinc-400">Agent Network Visualization</div>
                <div className="text-xs text-zinc-500 mt-2">Coming Soon</div>
              </div>
            </div>
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
              <div className="text-center py-8 text-zinc-400">
                <MessageSquare className="size-8 mx-auto mb-2" />
                <div>No agent communications yet</div>
                <div className="text-xs text-zinc-500 mt-1">Start simulation to see activity</div>
              </div>
            ) : (
              messages.slice(-10).reverse().map((message) => {
                const fromAgent = agents.find(a => a.id === message.from);
                const toAgent = agents.find(a => a.id === message.to);
                
                return (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-start gap-3 p-3 bg-zinc-900/50 rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        message.type === 'thought' ? 'bg-blue-400' :
                        message.type === 'action' ? 'bg-green-400' :
                        message.type === 'query' ? 'bg-orange-400' : 'bg-purple-400'
                      }`} />
                      <span className="text-xs text-zinc-400">
                        {fromAgent?.name.split(' ')[0]} → {toAgent?.name.split(' ')[0]}
                      </span>
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-zinc-300">{message.content}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-zinc-500">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                        <span className="text-xs text-zinc-500">
                          Confidence: {Math.round(message.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
