"use client";
import { CameraFeed } from "./CameraFeed";

const ARM = process.env.NEXT_PUBLIC_CAMERA_ARM_URL || "";
const TOP = process.env.NEXT_PUBLIC_CAMERA_TOP_URL || "";

function detectTransport(url: string): "mjpeg"|"hls"|"webrtc" {
  if (!url) return "mjpeg";
  if (url.startsWith("ws")) return "webrtc";
  if (url.endsWith(".m3u8")) return "hls";
  if (url.endsWith(".mjpg") || url.endsWith(".mjpeg")) return "mjpeg";
  return "mjpeg";
}

export function CameraWall() {
  return (
    <div className="space-y-3">
      <CameraFeed title="Robot Arm" url={ARM} transport={detectTransport(ARM)} />
      <CameraFeed title="Top-Down Board" url={TOP} transport={detectTransport(TOP)} />
    </div>
  );
}
