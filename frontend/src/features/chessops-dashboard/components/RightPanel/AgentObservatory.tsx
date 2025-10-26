/**
 * Agent Observatory Component
 * 
 * Visualizes agent-to-agent interactions (lanes or graph view)
 */

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { LayoutList, Network } from "lucide-react";
import { useDashboardStore } from "../../store/dashboardStore";
import { mockAgentMetadata, generateMockAgentEvents } from "../../lib/mockData";
import { useState } from "react";

export function AgentObservatory() {
  const observatoryView = useDashboardStore((s) => s.observatoryView);
  const setObservatoryView = useDashboardStore((s) => s.setObservatoryView);
  const [agents] = useState(mockAgentMetadata);
  const [events] = useState(() => generateMockAgentEvents(20));

  return (
    <div className="h-full flex flex-col">
      {/* Header with view toggle */}
      <div className="p-4 border-b flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold">Agent Observatory</h3>
          <p className="text-xs text-muted-foreground">
            {events.length} events tracked
          </p>
        </div>

        <div className="flex gap-1">
          <Button
            variant={observatoryView === "lanes" ? "secondary" : "ghost"}
            size="icon-sm"
            onClick={() => setObservatoryView("lanes")}
          >
            <LayoutList className="size-4" />
          </Button>
          <Button
            variant={observatoryView === "graph" ? "secondary" : "ghost"}
            size="icon-sm"
            onClick={() => setObservatoryView("graph")}
          >
            <Network className="size-4" />
          </Button>
        </div>
      </div>

      {/* Agent Status Cards */}
      <div className="px-4 py-3 border-b space-y-2">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className="flex items-center justify-between p-2 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <div
                className="size-2 rounded-full"
                style={{ backgroundColor: agent.color }}
              />
              <span className="text-xs font-medium">{agent.label}</span>
            </div>
            <Badge variant="outline" className="text-xs">
              {agent.status}
            </Badge>
          </div>
        ))}
      </div>

      {/* Events View */}
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-2">
          {observatoryView === "lanes" ? (
            <AgentLanesView events={events} agents={agents} />
          ) : (
            <AgentGraphView />
          )}
        </div>
      </ScrollArea>
    </div>
  );
}

function AgentLanesView({ events, agents }: any) {
  return (
    <div className="space-y-3">
      {events.map((event: any) => {
        const agent = agents.find((a: any) => a.id === event.agent);
        return (
          <Card key={event.id} className="p-3">
            <div className="flex items-start gap-3">
              <div
                className="size-2 rounded-full mt-1.5 shrink-0"
                style={{ backgroundColor: agent?.color }}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-medium">{agent?.label}</span>
                  <Badge variant="outline" className="text-xs">
                    {event.kind}
                  </Badge>
                  {event.latency_ms && (
                    <span className="text-xs text-muted-foreground">
                      {event.latency_ms}ms
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {event.content || event.tool || "Processing..."}
                </p>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

function AgentGraphView() {
  return (
    <Card className="p-6">
      <div className="text-center text-muted-foreground space-y-2">
        <Network className="size-12 mx-auto opacity-20" />
        <p className="text-sm">Conversation Graph View</p>
        <p className="text-xs">Force-directed graph coming soon</p>
      </div>
    </Card>
  );
}

