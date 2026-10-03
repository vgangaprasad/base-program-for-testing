# Copy this file and rename it, e.g.  m03_crane.py  (m + number + name).
# Only write the run() function. Always put  await  before robot functions!
from robot import *


async def run():
    # Mission: <write the name here>
    # The robot starts facing heading 0.

    set_speed("medium")        # "slow", "medium" or "fast"

    await drive(30)            # forward 30 cm
    await turn(90)             # turn right 90 degrees (use -90 for left)
    await attachment("left", 180)   # move the left attachment motor
    await drive(-30)           # backward 30 cm
