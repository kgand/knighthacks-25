from pathlib import Path
import cv2
import time
import os
import json

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

############################################
# User config
############################################

FOLLOWER_PORT = "/dev/ttyACM1"
LEADER_PORT   = "/dev/ttyACM0"

FOLLOWER_ID = "my_awesome_follower_arm"
LEADER_ID   = "my_awesome_leader_arm"

FOLLOWER_CALIB_DIR = "/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower"
LEADER_CALIB_DIR   = "/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader"

CAM_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 30

LOG_DIR = "session_frames"
LOG_CSV = "session_actions.csv"

############################################
# Camera setup
############################################

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAM_FPS)

if not cap.isOpened():
    print("⚠️  Warning: camera did not open. Teleop will still run, but no frames will be captured.")
    cam_ok = False
else:
    cam_ok = True
    print(f"📷 Camera stream initialized (/dev/video{CAM_INDEX} @ {CAM_WIDTH}x{CAM_HEIGHT}x{CAM_FPS}).")

############################################
# Robot setup
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

follower.connect()
leader.connect()
follower.configure()
leader.configure()

print("✅ Connected both arms with existing calibration.")
print("🤖 Teleop running. Move the leader to drive the follower.")
print("💾 Logging actions + camera frames. Ctrl+C to stop.")

############################################
# Logging setup
############################################

os.makedirs(LOG_DIR, exist_ok=True)
log_file = open(LOG_CSV, "w")
log_file.write("timestamp_ns,action_json\n")

############################################
# Main teleop + capture loop
############################################

try:
    while True:
        # 1️⃣ Get action from leader
        action = leader.get_action()

        # 2️⃣ Send action to follower
        follower.send_action(action)

        # 3️⃣ Capture camera frame
        frame = None
        if cam_ok:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Camera read failed")
                frame = None

        # 4️⃣ Log synchronized data
        ts_ns = time.time_ns()

        # convert action to JSON-friendly format
        if isinstance(action, dict):
            action_json = json.dumps(action)
        else:
            try:
                action_json = json.dumps(action.tolist())
            except Exception:
                action_json = json.dumps(str(action))

        log_file.write(f"{ts_ns},{action_json}\n")

        if frame is not None:
            cv2.imwrite(f"{LOG_DIR}/frame_{ts_ns}.png", frame)

        # Optional preview
        # if frame is not None:
        #     cv2.imshow("Teleop Camera", frame)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

except KeyboardInterrupt:
    print("\n🟡 Stopping teleop and logging...")

finally:
    log_file.close()
    if cam_ok:
        cap.release()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass

    try:
        follower.bus.disable_torque()
    except Exception:
        pass

    follower.disconnect()
    leader.disconnect()
    print("✅ Session saved successfully.")
    print(f"   - Frames in: {LOG_DIR}/")
    print(f"   - Actions in: {LOG_CSV}")

# lerobot-teleoperate   --robot.type=so101_follower   --robot.port=/dev/ttyACM1   --robot.id=my_awesome_follower_arm   --robot.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower   --robot.cameras="{ front: { type: opencv, index_or_path: '/dev/video0', width: 640, height: 480, fps: 30 } }"   --teleop.type=so101_leader   --teleop.port=/dev/ttyACM0   --teleop.id=my_awesome_leader_arm   --teleop.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader   --display_data=false

