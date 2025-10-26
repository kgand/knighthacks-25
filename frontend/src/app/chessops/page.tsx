"use client";

import { useEffect } from "react";
import { TopBar } from "@/components/chessops/TopBar";
import { CameraWall } from "@/components/chessops/CameraWall";
import { DebugWorkbench } from "@/components/chessops/DebugWorkbench/PipelineTabs";
import { AgentObservatory } from "@/components/chessops/Agents/AgentObservatory";
import { ChatPanel } from "@/components/chessops/Chat/ChatPanel";
import { featureEnabled } from "@/lib/featureFlags";

export default function ChessOpsPage() {
  useEffect(() => {
    if (!featureEnabled("CHESSOPS")) console.warn("ChessOps flag disabled.");
  }, []);

  return (
    <div className="flex h-dvh flex-col">
      <TopBar />
      <div className="grid grid-cols-12 gap-3 p-3">
        <div className="col-span-12 xl:col-span-4 space-y-3">
          <CameraWall />
        </div>
        <div className="col-span-12 xl:col-span-5 space-y-3">
          <DebugWorkbench />
        </div>
        <div className="col-span-12 xl:col-span-3 space-y-3">
          <AgentObservatory />
          <ChatPanel />
        </div>
      </div>
    </div>
  );
}
