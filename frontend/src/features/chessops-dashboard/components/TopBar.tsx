/**
 * Top Bar Component
 * 
 * Displays product title, connection status, and global controls
 */

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, Camera, Cpu, Moon, Sun } from "lucide-react";
import { useDashboardStore } from "../store/dashboardStore";
import { useState, useEffect } from "react";

export function TopBar() {
  const pipelineConnected = useDashboardStore((s) => s.pipelineConnected);
  const agentConnected = useDashboardStore((s) => s.agentConnected);
  
  // Initialize theme from system preference or saved state
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== "undefined") {
      return (
        document.documentElement.classList.contains("dark") ||
        window.matchMedia("(prefers-color-scheme: dark)").matches
      );
    }
    return true; // default to dark
  });

  // Apply dark class on mount
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, []);

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle("dark");
  };

  return (
    <div className="h-16 border-b bg-card px-6 flex items-center justify-between">
      {/* Left: Title & Status */}
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-xl font-bold tracking-tight">ChessOps Dashboard</h1>
          <p className="text-xs text-muted-foreground">Real-time chess detection & agent observatory</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Camera className="size-4 text-muted-foreground" />
            <Badge variant={pipelineConnected ? "success" : "outline"}>
              {pipelineConnected ? "Pipeline Live" : "Disconnected"}
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Cpu className="size-4 text-muted-foreground" />
            <Badge variant={agentConnected ? "success" : "outline"}>
              {agentConnected ? "Agents Online" : "No Agents"}
            </Badge>
          </div>
        </div>
      </div>

      {/* Right: Controls */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={toggleTheme}
          className="rounded-full"
        >
          {isDark ? (
            <Sun className="size-4" />
          ) : (
            <Moon className="size-4" />
          )}
        </Button>

        <Button variant="outline" size="sm" className="gap-2">
          <Activity className="size-4" />
          Health
        </Button>
      </div>
    </div>
  );
}

