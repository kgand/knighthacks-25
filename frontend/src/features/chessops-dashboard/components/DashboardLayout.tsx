/**
 * Dashboard Layout
 * 
 * Three-panel resizable layout:
 * - Left: Camera Wall
 * - Center: Debugging Workbench
 * - Right: Chat & Agent Observatory
 */

import { useState } from "react";
import { TopBar } from "./TopBar";
import { CameraWall } from "./CameraWall/CameraWall";
import { DebugWorkbench } from "./DebugWorkbench/DebugWorkbench";
import { RightPanel } from "./RightPanel/RightPanel";

export function DashboardLayout() {
  const [leftWidth, setLeftWidth] = useState(30); // percentage
  const [rightWidth, setRightWidth] = useState(25); // percentage

  return (
    <div className="h-screen flex flex-col bg-background">
      <TopBar />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Camera Wall */}
        <div
          className="border-r flex flex-col"
          style={{ width: `${leftWidth}%` }}
        >
          <CameraWall />
        </div>

        {/* Resize Handle Left */}
        <div
          className="w-1 bg-border hover:bg-primary cursor-col-resize transition-colors"
          onMouseDown={(e) => {
            e.preventDefault();
            const startX = e.clientX;
            const startWidth = leftWidth;

            const handleMouseMove = (e: MouseEvent) => {
              const deltaX = e.clientX - startX;
              const newWidth = startWidth + (deltaX / window.innerWidth) * 100;
              setLeftWidth(Math.max(20, Math.min(40, newWidth)));
            };

            const handleMouseUp = () => {
              document.removeEventListener("mousemove", handleMouseMove);
              document.removeEventListener("mouseup", handleMouseUp);
            };

            document.addEventListener("mousemove", handleMouseMove);
            document.addEventListener("mouseup", handleMouseUp);
          }}
        />

        {/* Center Panel: Debugging Workbench */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <DebugWorkbench />
        </div>

        {/* Resize Handle Right */}
        <div
          className="w-1 bg-border hover:bg-primary cursor-col-resize transition-colors"
          onMouseDown={(e) => {
            e.preventDefault();
            const startX = e.clientX;
            const startWidth = rightWidth;

            const handleMouseMove = (e: MouseEvent) => {
              const deltaX = startX - e.clientX;
              const newWidth = startWidth + (deltaX / window.innerWidth) * 100;
              setRightWidth(Math.max(20, Math.min(35, newWidth)));
            };

            const handleMouseUp = () => {
              document.removeEventListener("mousemove", handleMouseMove);
              document.removeEventListener("mouseup", handleMouseUp);
            };

            document.addEventListener("mousemove", handleMouseMove);
            document.addEventListener("mouseup", handleMouseUp);
          }}
        />

        {/* Right Panel: Chat & Agents */}
        <div
          className="border-l flex flex-col"
          style={{ width: `${rightWidth}%` }}
        >
          <RightPanel />
        </div>
      </div>
    </div>
  );
}

