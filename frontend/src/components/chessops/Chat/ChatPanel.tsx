"use client";
import { useSelection } from "../SelectionStore";
import type { ChatComponent } from "./ChatAdapter";

const MissingChat: ChatComponent = ({ className }) => (
  <div className={className}>
    <div className="rounded-2xl bg-zinc-900 p-4 text-sm text-zinc-400">
      Plug your existing chat component here via ChatAdapter. Streaming/tool messages will just work.
    </div>
  </div>
);

export function ChatPanel() {
  const ctx = useSelection((s) => ({ frameId: s.frameId, cell: s.cell, threadId: s.threadId }));
  const Chat = MissingChat; // Replace with your chat component
  return (
    <div className="rounded-2xl bg-zinc-950 shadow-soft ring-1 ring-white/10">
      <div className="border-b border-white/10 px-3 py-2 text-sm font-medium">Chat</div>
      <Chat className="p-3" context={ctx} />
    </div>
  );
}
