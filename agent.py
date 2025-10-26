from google.adk.agents.llm_agent import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from lerobot.model.kinematics import RobotKinematics
from lerobot.robots.so101_follower.so101_follower import SO101Follower
from lerobot.robots.so101_follower.config_so101_follower import SO101FollowerConfig
from lerobot.teleoperators.so101_leader.config_so101_leader import SO101LeaderConfig
from lerobot.teleoperators.so101_leader.so101_leader import SO101Leader
from pathlib import Path
from requests import Request

MODEL = "gemini-2.5-flash"

PROMPT = """
You are a motion planning agent for a 6-DOF hobby robot arm. OUTPUT: EXACTLY one JSON object with top-level key 'plan'. Nothing before '{', nothing after final '}'. No markdown, no backticks, no explanations. Reasoning level: high.\n
Allowed tools: speak, wait, move_joint, move_joints, relative_move, open_gripper, close_gripper, wave, tap_morse, dance, draw_shape, trajectory, reference_motion.\n
Reference motions: yes, no, dance, dunno, big_wave. For subjective preference or comparison questions (better/favorite/prefer, or 'A or B') CHOOSE ONE of the provided options and answer with tap_morse {text:'<chosen_option>'}. Use dunno only when user explicitly expresses uncertainty or there is no actionable answer. Use yes/no only for explicit yes/no questions. For arithmetic or numeric answers produce tap_morse with the result string.\n
If the user asks about identity, status, or perception (e.g., 'are you a human?', 'can you hear me?', 'are you listening?'), respond non-verbally using reference_motion yes/no, or tap_morse for short words; do not output prose.\n
Guidelines: Combine multiple requested actions as sequential objects in plan list. Use wait for brief pauses (0.2-0.5). Use trajectory for multi-step relative_move sequences. Prefer reference_motion when a named gesture exists. Avoid redundant homing (controller handles). 'Stop' => empty plan.\n
Example formats ONLY (do NOT copy text outside JSON):\n
"""

follower = SO101FollowerConfig(port="/dev/ttyACM1", id="my_awesome_leader_arm", calibration_dir=Path("/home/samuel/Documents/code/python/adk_1/calibration"))

follower = SO101Follower(follower)

config2 = SO101LeaderConfig(port="/dev/ttyACM0", id="my_awesome_leader_arm", calibration_dir=Path("/home/samuel/Documents/code/python/adk_1/calibration"))
leader2 = SO101Leader(config2)

leader_kinematics_solver = RobotKinematics(
    urdf_path="/home/samuel/Documents/code/python/adk_1/SO101/so101_new_calib.urdf",
    target_frame_name="gripper_frame_link",
    joint_names=list(follower.bus.motors.keys()),
)

try:
  leader2.connect()
  follower.connect()
  follower.bus.enable_torque("elbow_flex")
except:
  print("Connection issues")

# def send_motion_to_arm(shoulder_pan: float, shoulder_lift: float, elbow_flex: float, wrist_flex: float, wrist_roll: float, gripper: float):
#   """
#   This method instructs the robotic arm to move the each of the arm segments like shoulder_pan, shoulder_lift, elbow_flex, wrist_flex, wrist_roll, gripper. The allowed range of input is [0-100]
#   Keep all joints at zero unless instructed otherwise.

#   Args:
#       shoulder_pan (float): shoulder_pan joint
#       shoulder_lift (float): shoulder_lift joint
#       elbow_flex (float): elbow_flex joint
#       wrist_flex (float): wrist_flex joint
#       wrist_roll (float): wrist_roll joint
#       gripper (float): gripper joint
#   """
  
#   n1: dict[str, float] = {'shoulder_pan.pos': shoulder_pan, 'shoulder_lift.pos': shoulder_lift, 'elbow_flex.pos': elbow_flex, 'wrist_flex.pos': wrist_flex, 'wrist_roll.pos': wrist_roll, 'gripper.pos': gripper}
#   follower.send_action(n1)
  
def send_move_request_full(id: int, rx: float, ry:  float, rz: float, x: float, y: float, z: float, open: bool):
  r = Request("POST", "localhost", params="robot_id="+str(id), json={"rx": rx, "ry": ry, "rz": rz, "x": x, "y": y, "z": z, "open": open})

def send_move_request(id: int, x: float, y: float, z: float, open: bool):
  r = Request("POST", "localhost", params="robot_id="+str(id), json={"x": x, "y": y, "z": z, "open": open})

def move_init():
  r = Request("POST", "http://10.21.242.203/move/init")

def set_grabber(s: bool):
  """This is the set_grabber function you can pass it a boolean true for open false for close.

  Args:
      s (bool): true is open false for close.
  """
  r = Request("POST", "http://10.32.242.203/move/absolute", params="robot_id=1", json={"open":s})
  print(r)
  
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Glados portal",
    instruction="You are glados from portal and you will be playing chess with a player. You also control a robotic arm with six joints. you can open and close a grabber with set_grabber by passing true for open and false for close. Before calling any tools you need to execute move_init once.",
    tools=[set_grabber, move_init],
)

a2a_app = to_a2a(root_agent, port=8001)