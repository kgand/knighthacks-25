/**
 * Right Panel Component
 * 
 * Toggleable Chat & Agent Observatory
 */

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { MessageSquare, Network } from "lucide-react";
import { ChatPanel } from "./ChatPanel";
import { AgentObservatory } from "./AgentObservatory";

export function RightPanel() {
  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Tabs defaultValue="chat" className="flex-1 flex flex-col">
        <div className="p-4 border-b">
          <TabsList className="w-full">
            <TabsTrigger value="chat" className="flex-1 gap-2">
              <MessageSquare className="size-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="agents" className="flex-1 gap-2">
              <Network className="size-4" />
              Agents
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-hidden">
          <TabsContent value="chat" className="h-full m-0">
            <ChatPanel />
          </TabsContent>

          <TabsContent value="agents" className="h-full m-0">
            <AgentObservatory />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}

