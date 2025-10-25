import cv2
import sys
from lerobot.teleoperate import main

# 🔧 Pre-set the camera mode before LeRobot opens it
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.release()
print("✅ /dev/video0 pre-set to MJPG 640x480x30")

# Forward args to LeRobot just like the CLI does
sys.argv = [
    "lerobot-teleoperate",
    "--robot.type=so101_follower",
    "--robot.port=/dev/ttyACM1",
    "--robot.id=my_awesome_follower_arm",
    "--robot.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower",
    "--robot.cameras={ front: { type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30 } }",
    "--teleop.type=so101_leader",
    "--teleop.port=/dev/ttyACM0",
    "--teleop.id=my_awesome_leader_arm",
    "--teleop.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader",
    "--display_data=false",
]

# 🚀 Run LeRobot programmatically
main()
