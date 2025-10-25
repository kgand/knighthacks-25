from pathlib import Path
import cv2
import time
import os
import json
import signal
import sys

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

############################################
# USER CONFIG (edit if ports / IDs change)
############################################

FOLLOWER_PORT = "/dev/ttyACM1"   # follower arm controller
LEADER_PORT   = "/dev/ttyACM2"   # leader / teacher controller

FOLLOWER_ID = "my_awesome_follower_arm"
LEADER_ID   = "my_awesome_leader_arm"

FOLLOWER_CALIB_DIR = "/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower"
LEADER_CALIB_DIR   = "/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader"

CAM_INDEX  = 0          # /dev/video0
CAM_WIDTH  =  640
CAM_HEIGHT = 480
CAM_FPS    = 30

TARGET_HZ = 30.0        # control/logging rate target
DT = 1.0 / TARGET_HZ

BASE_SESSION_DIR = Path("dataset_sessions")

############################################
# graceful Ctrl+C handling
############################################

running = True
def handle_sigint(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, handle_sigint)

############################################
# STEP 0. Create a new episode directory
############################################

timestamp_str = time.strftime("episode_%Y%m%d_%H%M%S")
EPISODE_DIR = BASE_SESSION_DIR / timestamp_str
FRAMES_DIR = EPISODE_DIR / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

ACTIONS_CSV = EPISODE_DIR / "actions.csv"
log_f = open(ACTIONS_CSV, "w")
log_f.write("timestamp_ns,action_json\n")

print(f"📁 Recording new episode: {timestamp_str}")
print(f"   Frames dir : {FRAMES_DIR}")
print(f"   Actions CSV: {ACTIONS_CSV}")

############################################
# STEP 1. Init camera with MJPG so OpenCV works in WSL
############################################

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAM_FPS)

# warm up camera
cam_ok = False
for _ in range(10):
    ret, _frame = cap.read()
    if ret:
        cam_ok = True
        break

if cam_ok:
    print(f"📷 Camera ready at {CAM_WIDTH}x{CAM_HEIGHT}@{CAM_FPS}fps.")
else:
    print("⚠️ Camera did not start streaming. We'll still teleop, but won't save frames.")

############################################
# STEP 2. Init follower + leader
############################################

follower_cfg = SO101FollowerConfig(
    port=FOLLOWER_PORT,
    id=FOLLOWER_ID,
    calibration_dir=Path(FOLLOWER_CALIB_DIR),
)

leader_cfg = SO101LeaderConfig(
    port=LEADER_PORT,
    id=LEADER_ID,
    calibration_dir=Path(LEADER_CALIB_DIR),
)

follower = SO101Follower(follower_cfg)
leader = SO101Leader(leader_cfg)

print("🔌 Connecting follower...")
follower.connect()
print("🔌 Connecting leader...")
leader.connect()

# configure() loads calibration and applies limits.
# you've already synced calibration, so this should *not* ask you to recalibrate again.
print("⚙️ Configuring follower...")
follower.configure()
print("⚙️ Configuring leader...")
leader.configure()

print("✅ Both devices connected and configured.")
print("🤖 Teleop active. Move the leader to drive the follower.")
print("💾 Logging images + actions to", EPISODE_DIR)
print("⛔ Press Ctrl+C to stop and save this episode.")

############################################
# STEP 3. Main control loop (leader -> follower, + logging)
############################################

last_t = time.time()

try:
    while running:
        # 1. get the leader's action (joint targets / pose command)
        action = leader.get_action()

        # 2. send that action to the follower
        follower.send_action(action)

        # 3. grab camera frame
        frame = None
        if cam_ok:
            ret, f = cap.read()
            if ret:
                frame = cv2.rotate(f, cv2.ROTATE_90_CLOCKWISE)
            else:
                frame = None

        # 4. timestamp for sync
        ts_ns = time.time_ns()

        # 5. serialize action to JSON
        if isinstance(action, dict):
            action_json = json.dumps(action)
        else:
            # fallback: arrays / tensors etc.
            try:
                action_json = json.dumps(action.tolist())
            except Exception:
                action_json = json.dumps(str(action))

        # 6. write action row
        log_f.write(f"{ts_ns},{action_json}\n")

        # 7. save frame
        if frame is not None:
            frame_path = FRAMES_DIR / f"frame_{ts_ns}.png"
            cv2.imwrite(str(frame_path), frame)

        # 8. gentle pacing (~30 Hz target)
        now = time.time()
        dt = now - last_t
        if dt < DT:
            time.sleep(DT - dt)
        last_t = now

except KeyboardInterrupt:
    # normal stop
    pass
finally:
    print("\n🟡 Stopping teleop for this episode...")

    # close action log
    log_f.close()

    # release camera
    cap.release()
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

    # relax the follower (turn off torque so the arm isn't locked)
    try:
        follower.bus.disable_torque()
    except Exception:
        pass

    # disconnect from both devices
    try:
        follower.disconnect()
    except Exception as e:
        print("Follower disconnect warning:", e)

    try:
        leader.disconnect()
    except Exception as e:
        print("Leader disconnect warning:", e)

    print("✅ Episode saved.")
    print(f"   -> {EPISODE_DIR}")


#python3 -u "/home/marion/so-arm101-ros2-bridge/teleop_full_pipeline.py"
