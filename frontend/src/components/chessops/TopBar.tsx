"use client";
import { useState } from "react";
import { apiSetElo } from "@/lib/api";
import { Rocket, Signal, Sun, Triangle } from "lucide-react";

export function TopBar() {
  const [elo, setElo] = useState(1500);
  return (
    <div className="sticky top-0 z-50 border-b border-white/10 bg-zinc-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-[1920px] items-center gap-3 px-4 py-2">
        <Triangle className="size-5 text-fuchsia-400" />
        <div className="font-semibold">ChessOps Dashboard</div>
        <div className="ml-auto flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <Signal className="size-4" /> live
          </div>
          <input
            className="w-24 rounded-xl bg-zinc-900 px-3 py-1 text-sm"
            type="number"
            value={elo}
            min={1320}
            max={3190}
            onChange={(e) => setElo(parseInt(e.target.value || "1500", 10))}
            onBlur={() => apiSetElo(elo).catch(() => {})}
            title="Stockfish Elo"
          />
          <button className="rounded-xl bg-fuchsia-500/20 px-3 py-1 text-sm hover:bg-fuchsia-500/25">
            <Rocket className="mr-1 inline size-4" /> Run
          </button>
          <button className="rounded-xl bg-zinc-900 px-3 py-1 text-sm">
            <Sun className="inline size-4" /> Theme
          </button>
        </div>
      </div>
    </div>
  );
}
