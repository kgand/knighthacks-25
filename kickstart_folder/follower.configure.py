import json
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

def configur():
        
    config = SO101FollowerConfig(
        port="COM7",
        id="follower_01_v1",
    )
    follower = SO101Follower(config)
    follower.setup_motors()


    # --- 2️⃣ Save motor configuration to file ---
    # Save configuration manually
    with open("so101_follower_config.json", "w") as f:
        json.dump(config.__dict__, f, indent=4)
    print("✅ Configuration saved!")