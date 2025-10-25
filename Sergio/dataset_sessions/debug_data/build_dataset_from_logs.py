import os
import json
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

BASE_SESSION_DIR = Path("dataset_sessions")
OUT_DIR = Path("combined_dataset")
OUT_DIR.mkdir(parents=True, exist_ok=True)

all_frames = []
all_actions = []
all_timestamps = []
all_episode_names = []
index_rows = []

episodes = sorted([p for p in BASE_SESSION_DIR.iterdir() if p.is_dir()])

print(f"📂 Found {len(episodes)} episode(s).")
for ep_dir in episodes:
    ep_name = ep_dir.name
    frames_dir = ep_dir / "frames"
    actions_csv = ep_dir / "actions.csv"

    if not actions_csv.exists():
        print(f"⚠️ Skipping {ep_name}: no actions.csv")
        continue

    # load the action timeline
    df = pd.read_csv(actions_csv)
    # df columns: timestamp_ns,action_json

    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Episode {ep_name}"):
        ts = int(row["timestamp_ns"])
        action = json.loads(row["action_json"])

        frame_path = frames_dir / f"frame_{ts}.png"
        if not frame_path.exists():
            # no frame at this timestamp? skip this step
            continue

        # load the image (BGR -> RGB)
        img_bgr = cv2.imread(str(frame_path))
        if img_bgr is None:
            continue
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # store in memory
        all_frames.append(img_rgb)
        all_actions.append(action)
        all_timestamps.append(ts)
        all_episode_names.append(ep_name)

        # also log for index.jsonl
        rel_frame_path = f"{ep_name}/frames/frame_{ts}.png"
        index_rows.append({
            "episode": ep_name,
            "timestamp_ns": ts,
            "image_path": rel_frame_path,
            "action": action,
        })

# convert to numpy arrays where possible
frames_array = np.array(all_frames, dtype=np.uint8)

# actions may be dicts with per-joint values, etc.
# we'll keep them as an object array to avoid losing structure
actions_array = np.array(all_actions, dtype=object)
timestamps_array = np.array(all_timestamps, dtype=np.int64)
episodes_array = np.array(all_episode_names, dtype=object)

# save NPZ bundle
npz_path = OUT_DIR / "teleop_data.npz"
np.savez_compressed(
    npz_path,
    frames=frames_array,
    actions=actions_array,
    timestamp_ns=timestamps_array,
    episode=episodes_array,
)

print(f"✅ Saved merged dataset to {npz_path}")
print(f"   Total usable samples: {len(frames_array)}")

# write an index.jsonl for human/debug/loading
index_path = OUT_DIR / "index.jsonl"
with open(index_path, "w") as f:
    for row in index_rows:
        f.write(json.dumps(row) + "\n")

print(f"📑 Wrote {index_path}")
print("Done.")
