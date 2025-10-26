"use client";
import Hls from "hls.js";
import { useEffect, useRef, useState } from "react";

type Transport = "mjpeg" | "hls" | "webrtc";
type Props = {
  title: string;
  url: string;
  transport: Transport;
  overlays?: React.ReactNode;
};

export function CameraFeed({ title, url, transport, overlays }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [status, setStatus] = useState<"connecting"|"connected"|"buffering"|"error">("connecting");

  useEffect(() => {
    let cleanup = () => {};
    if (transport === "mjpeg") {
      setStatus("connected");
    } else if (transport === "hls") {
      const video = videoRef.current!;
      if (Hls.isSupported()) {
        const hls = new Hls({ enableWorker: true, lowLatencyMode: true });
        hls.on(Hls.Events.MANIFEST_PARSED, () => setStatus("connected"));
        hls.on(Hls.Events.ERROR, () => setStatus("error"));
        hls.loadSource(url);
        hls.attachMedia(video);
        cleanup = () => hls.destroy();
      } else {
        setStatus("error");
      }
    } else if (transport === "webrtc") {
      // Expect external setup of srcObject if you use WebRTC
      setStatus("connected");
    }
    return () => cleanup();
  }, [transport, url]);

  return (
    <div className="relative rounded-2xl bg-zinc-950 shadow-soft ring-1 ring-white/10">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-2 text-sm">
        <span className="font-medium">{title}</span>
        <span className={`text-xs ${status==="connected"?"text-emerald-400":"text-amber-400"}`}>{status}</span>
      </div>

      <div className="relative">
        {transport === "mjpeg" ? (
          <img src={url} alt={title} className="aspect-video w-full rounded-b-2xl object-cover" />
        ) : (
          <video ref={videoRef} className="aspect-video w-full rounded-b-2xl bg-black" autoPlay muted playsInline />
        )}
        <div className="pointer-events-none absolute inset-0">{overlays}</div>
      </div>
    </div>
  );
}
