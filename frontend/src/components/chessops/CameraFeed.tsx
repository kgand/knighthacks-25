"use client";
import { useEffect, useRef, useState } from "react";
import { Video, VideoOff, Settings } from "lucide-react";
import { cameraManager, type CameraDevice } from "@/lib/cameraManager";

type Props = {
  title: string;
  deviceId?: string;
  overlays?: React.ReactNode;
};

export function CameraFeed({ title, deviceId, overlays }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [status, setStatus] = useState<"connecting"|"connected"|"error">("connecting");
  const [devices, setDevices] = useState<CameraDevice[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | undefined>(deviceId);
  const [showDeviceSelector, setShowDeviceSelector] = useState(false);

  // Initialize camera manager and get devices
  useEffect(() => {
    const initializeCameras = async () => {
      await cameraManager.initialize();
      setDevices(cameraManager.getDevices());
      
      // Auto-select first device if none selected
      if (!selectedDeviceId && cameraManager.getDevices().length > 0) {
        setSelectedDeviceId(cameraManager.getDevices()[0].deviceId);
      }
    };

    initializeCameras();

    // Subscribe to device changes
    const unsubscribe = cameraManager.subscribe(() => {
      setDevices(cameraManager.getDevices());
    });

    return () => {
      unsubscribe();
    };
  }, [selectedDeviceId]);

  // Start camera stream
  useEffect(() => {
    if (!selectedDeviceId) return;

    const startStream = async () => {
      try {
        setStatus("connecting");
        
        const stream = await cameraManager.getStream(selectedDeviceId);
        
        if (stream && videoRef.current) {
          videoRef.current.srcObject = stream;
          setStatus("connected");
        } else {
          setStatus("error");
        }
      } catch (error) {
        console.error('Error accessing camera:', error);
        setStatus("error");
      }
    };

    startStream();

    // Cleanup on unmount
    return () => {
      if (selectedDeviceId) {
        cameraManager.stopStream(selectedDeviceId);
      }
    };
  }, [selectedDeviceId]);

  const handleDeviceChange = (newDeviceId: string) => {
    setSelectedDeviceId(newDeviceId);
    setShowDeviceSelector(false);
  };

  return (
    <div className="relative rounded-2xl bg-zinc-950 shadow-soft ring-1 ring-white/10">
      <div className="flex items-center justify-between border-b border-white/10 px-3 py-2 text-sm">
        <span className="font-medium">{title}</span>
        <div className="flex items-center gap-2">
          <span className={`text-xs ${status==="connected"?"text-emerald-400":"text-amber-400"}`}>
            {status}
          </span>
          <button
            onClick={() => setShowDeviceSelector(!showDeviceSelector)}
            className="rounded-lg p-1 hover:bg-white/10"
            title="Select Camera"
          >
            <Settings className="size-4" />
          </button>
        </div>
      </div>

      <div className="relative">
        {status === "connected" ? (
          <video 
            ref={videoRef} 
            className="aspect-video w-full rounded-b-2xl bg-black object-cover" 
            autoPlay 
            muted 
            playsInline 
          />
        ) : (
          <div className="flex aspect-video w-full items-center justify-center rounded-b-2xl bg-black">
            {status === "error" ? (
              <div className="flex flex-col items-center gap-2 text-zinc-400">
                <VideoOff className="size-8" />
                <span className="text-sm">Camera Error</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2 text-zinc-400">
                <Video className="size-8 animate-pulse" />
                <span className="text-sm">Connecting...</span>
              </div>
            )}
          </div>
        )}
        
        {/* Device Selector Dropdown */}
        {showDeviceSelector && (
          <div className="absolute top-2 right-2 z-10 rounded-lg bg-zinc-900 p-2 shadow-lg ring-1 ring-white/10">
            <div className="text-xs font-medium text-zinc-300 mb-2">Select Camera:</div>
            {devices.length === 0 ? (
              <div className="text-xs text-zinc-400">No cameras found</div>
            ) : (
              <div className="space-y-1">
                {devices.map((device) => (
                  <button
                    key={device.deviceId}
                    onClick={() => handleDeviceChange(device.deviceId)}
                    className={`block w-full rounded px-2 py-1 text-left text-xs hover:bg-white/10 ${
                      selectedDeviceId === device.deviceId ? 'bg-fuchsia-500/20 text-fuchsia-300' : 'text-zinc-300'
                    }`}
                  >
                    {device.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        
        <div className="pointer-events-none absolute inset-0">{overlays}</div>
      </div>
    </div>
  );
}
