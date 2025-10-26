/**
 * Chat Panel Component
 * 
 * Reuses existing chat UI from App.tsx with enhancements
 */

import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Send, Sparkles } from "lucide-react";
import { useState } from "react";
import { mockChatMessages } from "../../lib/mockData";

export function ChatPanel() {
  const [messages] = useState(mockChatMessages);
  const [input, setInput] = useState("");

  return (
    <div className="h-full flex flex-col">
      {/* Messages */}
      <ScrollArea className="flex-1 px-4">
        <div className="space-y-4 py-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 ${
                msg.role === "user" ? "justify-end" : ""
              }`}
            >
              {msg.role === "assistant" && (
                <Avatar className="size-8 shrink-0">
                  <AvatarImage src="https://github.com/shadcn.png" />
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
              )}

              <div className={`flex flex-col gap-1 ${msg.role === "user" ? "items-end" : ""}`}>
                <div className="flex items-center gap-2">
                  {msg.role === "assistant" && (
                    <span className="text-xs font-medium">ChessOps AI</span>
                  )}
                  {msg.role === "user" && (
                    <span className="text-xs font-medium">You</span>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                <div
                  className={`rounded-lg p-3 max-w-[85%] ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>

              {msg.role === "user" && (
                <Avatar className="size-8 shrink-0">
                  <AvatarFallback>U</AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Quick Actions */}
      <div className="px-4 py-2 border-t">
        <div className="flex flex-wrap gap-1">
          <Button variant="ghost" size="sm" className="text-xs h-7 gap-1.5">
            <Sparkles className="size-3" />
            Explain current frame
          </Button>
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about the pipeline, board state, or agents..."
            className="min-h-[60px] resize-none"
          />
          <Button size="icon" className="shrink-0 h-[60px] w-[60px]">
            <Send className="size-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

