### Start up for doing a SO ARM Configuration and setting things up
Simple Startup guide for working with the software:
Run the indentify_script (probably hardest since you have to undo servo connections)
Run Callibrate (Do a full range of motion testing)

Then all Good to Run the Tele-Op script


Use this to find port of arms
lerobot-find-port


12v 2A - Follower
5v  4A - Leader

For jetson, use the following
python -m lerobot.find_port

Follower is /dev/ttyACM1
Leader is   /dev/ttyACM0


For Jetson
/home/marion/Desktop/Knighthacks/Robot_Tests/.venv/bin/python tele_op.py