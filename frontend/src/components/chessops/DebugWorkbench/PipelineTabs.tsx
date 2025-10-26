"use client";
import { TimelineChart } from "./TimelineChart";
import { ScoresTable } from "./ScoresTable";
import { Heatmaps } from "./Heatmaps";
import { BoardState } from "./BoardState";
import { Alerts } from "./Alerts";
import { useState } from "react";

export function DebugWorkbench() {
  const [tab, setTab] = useState<"pipeline"|"scores"|"heatmaps"|"board"|"alerts">("pipeline");
  return (
    <>
      <TimelineChart />
      <div className="rounded-2xl bg-zinc-950 shadow-soft ring-1 ring-white/10">
        <div className="flex items-center gap-2 border-b border-white/10 px-3 py-2 text-sm">
          {(["pipeline","scores","heatmaps","board","alerts"] as const).map(k => (
            <button key={k}
              onClick={() => setTab(k)}
              className={`rounded-lg px-2 py-1 capitalize ${tab===k?"bg-white/10":"hover:bg-white/5"}`}
            >
              {k}
            </button>
          ))}
        </div>
        <div className="p-3">
          {tab==="pipeline" && <div className="text-sm text-zinc-400">Raw → Grid Fit → Crops + Logits → Board + FEN/PGN (hook to your pipeline images and scores)</div>}
          {tab==="scores" && <ScoresTable />}
          {tab==="heatmaps" && <Heatmaps />}
          {tab==="board" && <BoardState />}
          {tab==="alerts" && <Alerts />}
        </div>
      </div>
    </>
  );
}
