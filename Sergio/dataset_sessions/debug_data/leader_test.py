import json
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

config = SO101LeaderConfig(
    port="COM11",
    id="my_awesome_leader_arm",
)
leader = SO101Leader(config)
leader.setup_motors()

# Save configuration manually
with open("so101_leader_config.json", "w") as f:
    json.dump(config.__dict__, f, indent=4)
    