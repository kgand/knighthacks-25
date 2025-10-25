from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower

def callibrate():
        
    config = SO101FollowerConfig(
        port="/dev/ttyACM1",
        id="follower_01_v1",
    )

    follower = SO101Follower(config)
    follower.connect(calibrate=False)
    follower.calibrate()
    follower.disconnect()

callibrate()