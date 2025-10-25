from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower

config = SO101FollowerConfig(
     port="/dev/ttyACM1",
    id="my_awesome_follower_arm",
)

follower = SO101Follower(config)
follower.connect(calibrate=False)
follower.calibrate()
follower.disconnect()

# lerobot-teleoperate \
#   --robot.type=so101_follower \
#   --robot.port=/dev/ttyACM1 \
#   --robot.id=my_follower_arm \
#   --robot.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/robots/so101_follower/my_awesome_follower_arm.json
#   --robot.cameras="{
#       front: {
#         type: opencv,
#         index_or_path: 0,
#         width: 640,
#         height: 480,
#         fps: 30
#       }
#     }" \
#   --teleop.type=so101_leader \
#   --teleop.port=/dev/ttyACM0 \
#   --teleop.id=my_leader_arm \
#   --teleop.calibration_dir=/home/marion/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader/my_awesome_leader_arm.json
#   --display_data=false
