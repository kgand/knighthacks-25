import json
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

config = SO101FollowerConfig(
    port="/dev/ttyACM1",
    id="my_awesome_follower_arm",
)
follower = SO101Follower(config)
follower.setup_motors()


# --- 2️⃣ Save motor configuration to file ---
# Save configuration manually
with open("so101_follower_config.json", "w") as f:
    json.dump(config.__dict__, f, indent=4)
print("✅ Configuration saved!")