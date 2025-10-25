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
# CONFIG
############################################

FOLLOWER_PORT = "/dev/ttyACM1"
LEADER_PORT   = "/dev/ttyACM0"

FOLLOWER_ID = "my_awesome_follower_arm"
LEADER_ID   = "my_awesome_leader_arm"

FOLLOWER_CALIB_DIR = "/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower"
LEADER_CALIB_DIR   = "/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader"

CAM_INDEX  = 0           # /dev/video0
CAM_WIDTH  = 640
CAM_HEIGHT = 480
CAM_FPS    = 30

LOG_DIR = "session_frames"
LOG_CSV = "session_actions.csv"

TARGET_HZ = 30.0
DT = 1.0 / TARGET_HZ

############################################
# CTRL+C handling so we always clean up
############################################

running = True
def handle_sigint(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, handle_sigint)

############################################
# STEP 1. Force camera MJPG mode & open capture
############################################

cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAM_FPS)

# Warm up camera so it's actually streaming
_cam_ok = False
for _ in range(10):
    ret, _frame = cap.read()
    if ret:
        _cam_ok = True
        break
if not _cam_ok:
    print("⚠️ Camera did not start streaming, continuing without vision logging.")
else:
    print(f"📷 Camera ready at {CAM_WIDTH}x{CAM_HEIGHT}@{CAM_FPS}fps.")

############################################
# STEP 2. Build robot objects
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

############################################
# STEP 3. Connect + configure both devices
############################################

print("🔌 Connecting follower...")
follower.connect()
print("🔌 Connecting leader...")
leader.connect()

# This is where LeRobot would sometimes try to force calibration.
# You've already synced calibration and IDs, so this *should* return without prompting.
print("⚙️ Configuring follower...")
follower.configure()
print("⚙️ Configuring leader...")
leader.configure()

print("✅ Both devices connected and configured.")
print("🤖 Teleop active. Move the leader to drive the follower.")
print("💾 Logging to session_frames/ and session_actions.csv. Press Ctrl+C to stop.")

############################################
# STEP 4. Prepare logging
############################################

os.makedirs(LOG_DIR, exist_ok=True)
log_f = open(LOG_CSV, "w")
log_f.write("timestamp_ns,action_json\n")

############################################
# STEP 5. Main control + logging loop
############################################

last_t = time.time()
while running:
    # get leader command
    action = leader.get_action()

    # send to follower
    follower.send_action(action)

    # get frame
    frame = None
    if _cam_ok:
        ret, frame = cap.read()
        if not ret:
            frame = None

    # timestamp
    ts_ns = time.time_ns()

    # serialize action
    if isinstance(action, dict):
        action_json = json.dumps(action)
    else:
        try:
            action_json = json.dumps(action.tolist())
        except Exception:
            action_json = json.dumps(str(action))

    # log action
    log_f.write(f"{ts_ns},{action_json}\n")

    # log frame
    if frame is not None:
        cv2.imwrite(f"{LOG_DIR}/frame_{ts_ns}.png", frame)

    # pacing ~30Hz
    now = time.time()
    dt = now - last_t
    if dt < DT:
        time.sleep(DT - dt)
    last_t = now

############################################
# STEP 6. Cleanup
############################################

print("\n🟡 Stopping teleop, cleaning up...")

# close log
log_f.close()

# release cam
cap.release()
try:
    cv2.destroyAllWindows()
except Exception:
    pass

# drop torque so the arm relaxes
try:
    follower.bus.disable_torque()
except Exception:
    pass

# disconnect devices
try:
    follower.disconnect()
except Exception as e:
    print("Follower disconnect warning:", e)

try:
    leader.disconnect()
except Exception as e:
    print("Leader disconnect warning:", e)

print("✅ Session ended cleanly.")
print(f"   Frames -> {LOG_DIR}/")
print(f"   Actions -> {LOG_CSV}")





# import sys, cv2
# from lerobot.teleoperate import main
# import lerobot.cameras.opencv.camera_opencv as cam_mod

# # ✅ Patch: redefine OpenCVCamera.connect to force MJPG settings
# def patched_connect(self):
#     self.cap = cv2.VideoCapture(int(self.index_or_path), cv2.CAP_V4L2)
#     self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
#     self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#     self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#     self.cap.set(cv2.CAP_PROP_FPS, 30)
#     for _ in range(5):
#         ret, frame = self.cap.read()
#         if ret:
#             print("✅ Patched camera stream OK")
#             return
#     raise RuntimeError("❌ Patched OpenCVCamera could not read frames after forcing MJPG")

# cam_mod.OpenCVCamera.connect = patched_connect

# # now forward normal args to the CLI
# sys.argv = [
#     "lerobot-teleoperate",
#     "--robot.type=so101_follower",
#     "--robot.port=/dev/ttyACM1",
#     "--robot.id=my_awesome_follower_arm",
#     "--robot.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower",
#     "--robot.cameras={ front: { type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30 } }",
#     "--teleop.type=so101_leader",
#     "--teleop.port=/dev/ttyACM0",
#     "--teleop.id=my_awesome_leader_arm",
#     "--teleop.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader",
#     "--display_data=false",
# ]
# main()
