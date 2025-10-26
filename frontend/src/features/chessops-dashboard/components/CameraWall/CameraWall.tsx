/**
 * Camera Wall Component
 * 
 * Displays two camera feeds: robot arm + top-down chessboard
 */

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Camera, Maximize2, Minimize2, Pause, Play } from "lucide-react";
import { useState } from "react";
import { mockCameraFeeds } from "../../lib/mockData";

export function CameraWall() {
  const [feeds] = useState(mockCameraFeeds);

  return (
    <div className="flex-1 overflow-auto p-4 space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <Camera className="size-4" />
          Camera Feeds
        </h2>
      </div>

      {/* Robot Arm Camera */}
      <CameraFeedCard feed={feeds["robot-arm"]} />

      {/* Top-Down Board Camera */}
      <CameraFeedCard feed={feeds["top-down"]} />
    </div>
  );
}

interface CameraFeedCardProps {
  feed: typeof mockCameraFeeds[string];
}

function CameraFeedCard({ feed }: CameraFeedCardProps) {
  const [isPlaying, setIsPlaying] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showOverlay, setShowOverlay] = useState(true);

  const isConnected = feed.health === "connected";

  return (
    <Card className="overflow-hidden">
      {/* Header */}
      <div className="p-3 border-b bg-muted/30 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{feed.label}</span>
          <Badge 
            variant={isConnected ? "success" : "outline"}
            className="text-xs"
          >
            {feed.health}
          </Badge>
        </div>
        <div className="flex items-center gap-1">
          {feed.fps && (
            <Badge variant="outline" className="text-xs">
              {feed.fps} FPS
            </Badge>
          )}
          {feed.latency_ms && (
            <Badge variant="outline" className="text-xs">
              {feed.latency_ms}ms
            </Badge>
          )}
        </div>
      </div>

      {/* Video/Image Display */}
      <div className="relative aspect-video bg-black/90">
        {isConnected ? (
          <>
            {/* Placeholder for actual video stream */}
            <div className="absolute inset-0 flex items-center justify-center text-muted-foreground">
              <div className="text-center space-y-2">
                <Camera className="size-12 mx-auto opacity-20" />
                <p className="text-xs">Camera feed placeholder</p>
                <p className="text-xs opacity-70">
                  {feed.resolution?.width} × {feed.resolution?.height}
                </p>
              </div>
            </div>

            {/* Overlay (grid, keypoints, etc.) */}
            {showOverlay && (
              <svg className="absolute inset-0 pointer-events-none">
                {/* Example grid overlay for top-down */}
                {feed.id === "top-down" && (
                  <g opacity="0.5" stroke="cyan" strokeWidth="1.5">
                    {/* 8x8 grid lines */}
                    {Array.from({ length: 9 }).map((_, i) => (
                      <line
                        key={`h-${i}`}
                        x1="10%"
                        y1={`${10 + i * 10}%`}
                        x2="90%"
                        y2={`${10 + i * 10}%`}
                      />
                    ))}
                    {Array.from({ length: 9 }).map((_, i) => (
                      <line
                        key={`v-${i}`}
                        x1={`${10 + i * 10}%`}
                        y1="10%"
                        x2={`${10 + i * 10}%`}
                        y2="90%"
                      />
                    ))}
                  </g>
                )}
              </svg>
            )}
          </>
        ) : (
          <Skeleton className="w-full h-full" />
        )}
      </div>

      {/* Controls */}
      <div className="p-2 border-t bg-muted/10 flex items-center justify-between">
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? (
              <Pause className="size-3.5" />
            ) : (
              <Play className="size-3.5" />
            )}
          </Button>

          <Button
            variant={showOverlay ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setShowOverlay(!showOverlay)}
            className="text-xs h-7"
          >
            Overlay
          </Button>
        </div>

        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => setIsFullscreen(!isFullscreen)}
        >
          {isFullscreen ? (
            <Minimize2 className="size-3.5" />
          ) : (
            <Maximize2 className="size-3.5" />
          )}
        </Button>
      </div>
    </Card>
  );
}

