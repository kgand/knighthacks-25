"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Send, 
  Bot, 
  User, 
  Loader2, 
  MessageSquare, 
  Trash2,
  Settings,
  Zap,
  Brain,
  Network,
  Cpu,
  ChevronDown,
  ChevronUp
} from "lucide-react";

interface ChatMessage {
  id: string;
  content: string;
  role: "user" | "assistant" | "system";
  timestamp: Date;
  agent?: string;
  confidence?: number;
  isTyping?: boolean;
}

interface ChatEndpoint {
  name: string;
  url: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}

const CHAT_ENDPOINTS: ChatEndpoint[] = [
  {
    name: "Quantum Planner",
    url: "/api/quantum-planner",
    description: "Strategic planning and decision optimization",
    icon: <Brain className="size-4" />,
    color: "from-blue-500 to-cyan-500"
  },
  {
    name: "Neural Worldview",
    url: "/api/neural-worldview", 
    description: "Context understanding and world modeling",
    icon: <Network className="size-4" />,
    color: "from-purple-500 to-pink-500"
  },
  {
    name: "Synthetic Personality",
    url: "/api/synthetic-personality",
    description: "Human-like interaction and personality",
    icon: <Zap className="size-4" />,
    color: "from-emerald-500 to-teal-500"
  },
  {
    name: "Cognitive Analyzer",
    url: "/api/cognitive-analyzer",
    description: "Deep analysis and pattern recognition",
    icon: <Cpu className="size-4" />,
    color: "from-orange-500 to-red-500"
  }
];

export function AdvancedChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      content: "Hello! I'm your A2A Agent Observatory assistant. I can connect you with our quantum planning, neural worldview, synthetic personality, and cognitive analysis agents. How can I help you today?",
      role: "assistant",
      timestamp: new Date(),
      agent: "System",
      confidence: 1.0
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedEndpoint, setSelectedEndpoint] = useState<ChatEndpoint | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: input.trim(),
      role: "user",
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate agent response
    setTimeout(() => {
      const agentResponse: ChatMessage = {
        id: `agent-${Date.now()}`,
        content: generateAgentResponse(input.trim()),
        role: "assistant",
        timestamp: new Date(),
        agent: selectedEndpoint?.name || "System",
        confidence: Math.random() * 0.3 + 0.7,
        isTyping: false
      };

      setMessages(prev => [...prev, agentResponse]);
      setIsLoading(false);
    }, 1000 + Math.random() * 2000);
  };

  const generateAgentResponse = (userInput: string): string => {
    const responses = [
      "I'm analyzing your request through our quantum planning algorithms. The optimal approach would be to...",
      "Based on my neural worldview analysis, I can see several pathways forward. Let me break this down...",
      "From a synthetic personality perspective, I understand your concern. Here's how I would approach this...",
      "My cognitive analysis suggests this is a complex problem requiring multi-dimensional thinking. Consider...",
      "The strategic optimization matrix indicates several viable solutions. The most efficient path would be...",
      "I'm processing this through our distributed knowledge graph. The correlation analysis shows...",
      "Based on my environmental context processing, I can recommend the following strategic approach...",
      "My emotional resonance parameters suggest this requires a nuanced response. Here's my analysis..."
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome",
        content: "Chat cleared. How can I help you today?",
        role: "assistant",
        timestamp: new Date(),
        agent: "System",
        confidence: 1.0
      }
    ]);
  };

  return (
    <div className="rounded-xl border bg-card flex flex-col h-96">
      {/* Header */}
      <div className="flex items-center justify-between border-b p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
            <MessageSquare className="h-4 w-4 text-primary" />
          </div>
          <div>
            <h3 className="font-semibold">Agent Chat</h3>
            <p className="text-sm text-muted-foreground">Multi-agent communication interface</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-muted"
            title="Agent Settings"
          >
            <Settings className="h-4 w-4" />
            {showSettings ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          <button
            onClick={clearChat}
            className="inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-muted text-destructive"
            title="Clear Chat"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Agent Selection */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b p-4"
          >
            <div className="text-sm font-medium mb-3">Select Agent Endpoint</div>
            <div className="grid grid-cols-2 gap-3">
              {CHAT_ENDPOINTS.map((endpoint) => (
                <button
                  key={endpoint.name}
                  onClick={() => setSelectedEndpoint(endpoint)}
                  className={`p-3 rounded-lg border transition-all ${
                    selectedEndpoint?.name === endpoint.name
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <div className={`p-1.5 rounded-md bg-gradient-to-br ${endpoint.color} shadow-sm`}>
                      {endpoint.icon}
                    </div>
                    <span className="text-sm font-medium">{endpoint.name}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">{endpoint.description}</div>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex gap-3 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role !== "user" && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                </div>
              )}
              
              <div className={`max-w-[80%] ${
                message.role === "user" ? "order-first" : ""
              }`}>
                <div className={`rounded-lg p-3 ${
                  message.role === "user" 
                    ? "bg-primary text-primary-foreground" 
                    : "bg-muted"
                }`}>
                  <div className="text-sm">{message.content}</div>
                  
                  {message.agent && (
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <span>{message.agent}</span>
                      {message.confidence && (
                        <span>• {Math.round(message.confidence * 100)}% confidence</span>
                      )}
                    </div>
                  )}
                </div>
                
                <div className="text-xs text-muted-foreground mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>

              {message.role === "user" && (
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 justify-start"
          >
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="bg-muted rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm text-muted-foreground">
                  {selectedEndpoint?.name || "System"} is thinking...
                </span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${selectedEndpoint?.name || "Agent System"}...`}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
              rows={1}
              style={{ minHeight: "40px", maxHeight: "120px" }}
            />
          </div>
          
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
        
        {selectedEndpoint && (
          <div className="mt-2 text-xs text-muted-foreground">
            Connected to: <span className="text-primary font-medium">{selectedEndpoint.name}</span>
          </div>
        )}
      </div>
    </div>
  );
}
