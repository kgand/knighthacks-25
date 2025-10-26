const BASE = process.env.NEXT_PUBLIC_CHESS_API_URL || "http://127.0.0.1:8000";

export async function apiCurrentBoardSvg(): Promise<string> {
  const res = await fetch(`${BASE}/current_board`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch board SVG");
  return res.text();
}

export async function apiPredict(image: File, a1Pos: string) {
  const formData = new FormData();
  formData.append('image', image);
  formData.append('a1_pos', a1Pos);
  
  const res = await fetch(`${BASE}/predict`, { 
    method: "POST", 
    body: formData 
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ fen: string; board_ascii: string; board_svg: string }>;
}

export async function apiNextMove() {
  const res = await fetch(`${BASE}/nextmove`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{
    best_move: { uci: string; san: string; score?: string | null };
    new_fen: string;
    board_svg_with_move: string;
  }>;
}

export async function apiSetElo(elo: number) {
  const res = await fetch(`${BASE}/set_elo`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ elo })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function apiVisualizeNextMove(): Promise<string> {
  const res = await fetch(`${BASE}/visualize_next_move`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch next move visualization");
  return res.text();
}

export async function checkServerStatus(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/`, { 
      method: "GET",
      signal: AbortSignal.timeout(5000)
    });
    return res.ok;
  } catch {
    return false;
  }
}
