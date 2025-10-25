from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader

def callibrate():
        
    config = SO101LeaderConfig(
        port="/dev/ttyACM0",
        id="leader_01_v1",
    )

    leader = SO101Leader(config)
    leader.connect(calibrate=False)
    leader.calibrate()
    leader.disconnect()


callibrate()