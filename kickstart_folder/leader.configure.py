import json
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

def configur():
        
    config = SO101LeaderConfig(
    port="COM15",
    id="leader_01_v1",
    )
    leader = SO101Leader(config)
    leader.setup_motors()

    # Save configuration manually
    with open("so101_leader_config.json", "w") as f:
        json.dump(config.__dict__, f, indent=4)
    