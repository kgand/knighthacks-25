from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# 1. Use the same port/id you used for teleop
config = SO101FollowerConfig(
    port="/dev/ttyACM1",          # <-- if you're on Linux; use COM10 if you're on Windows
    id="my_awesome_follower_arm", # <-- whatever you actually named it
)

# 2. Bring up the follower
follower = SO101Follower(config)

# Some versions require connect() before talking to motors
follower.connect()

# 3. Kill torque on all servos
follower.bus.disable_torque()

print("✅ Torque disabled on all joints. You can now move the follower arm freely (support it, it may drop).")








#CHECKING MOTOR INFO
# from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

# config = SO101FollowerConfig(
#     port="/dev/ttyACM1",          # use your real port
#     id="my_awesome_follower_arm", # same ID you used
# )

# follower = SO101Follower(config)

# # Some versions need this, some connect in __init__. If this errors, just comment it out.
# try:
#     follower.connect()
# except AttributeError:
#     pass

# print("=== dir(follower) ===")
# print(dir(follower))

# # Try to guess common bus names and print them if they exist
# possible_bus_attrs = [
#     "bus",
#     "motors_bus",
#     "_bus",
#     "_motors_bus",
#     "feetech_bus",
#     "_feetech_bus",
#     "servo_bus",
#     "motors",
#     "_motors",
# ]

# for attr in possible_bus_attrs:
#     if hasattr(follower, attr):
#         print(f"\n=== Found candidate bus attr: {attr} ===")
#         obj = getattr(follower, attr)
#         print("type:", type(obj))
#         print("dir:", dir(obj))