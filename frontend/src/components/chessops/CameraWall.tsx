"use client";
import { CameraFeed } from "./CameraFeed";

export function CameraWall() {
  return (
    <div className="space-y-3">
      <CameraFeed title="Robot Arm" />
      <CameraFeed title="Top-Down Board" />
    </div>
  );
}
