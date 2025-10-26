"use client";
import { useEffect, useState } from "react";
import { sse } from "@/lib/streams";
import { AgentLanes } from "./AgentLanes";
import { ConversationGraph } from "./ConversationGraph";

export type AgentEvent = {
  id: string; ts: number;
  agent: string; kind: "message"|"tool_call"|"tool_result"|"status";
  parent?: string; latency?: number; refs?: { frameId?: string; cell?: string };
  summary?: string; status?: "running"|"waiting"|"error"|"done";
};

export function AgentObservatory() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [view, setView] = useState<"lanes"|"graph">("lanes");

  useEffect(() => {
    const off = sse<AgentEvent>(process.env.NEXT_PUBLIC_AGENT_EVENTS_URL, (e) => {
      setEvents((prev) => [...prev.slice(-999), e]);
    });
    return off;
  }, []);

  return (
    <div className="rounded-2xl bg-zinc-950 shadow-soft ring-1 ring-white/10">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-2 text-sm">
        <div className="font-medium">A2A Agent Observatory</div>
        <div className="space-x-1">
          <button className={`rounded-lg px-2 py-1 text-xs ${view==="lanes"?"bg-white/10":""}`} onClick={() => setView("lanes")}>Lanes</button>
          <button className={`rounded-lg px-2 py-1 text-xs ${view==="graph"?"bg-white/10":""}`} onClick={() => setView("graph")}>Graph</button>
        </div>
      </div>
      <div className="p-3">
        {view === "lanes" ? <AgentLanes events={events} /> : <ConversationGraph events={events} />}
      </div>
    </div>
  );
}
