# Example mission showing the main functions.
from robot import *


async def run():
    set_speed("fast")
    await drive(60)
    await turn(-45)
    set_speed("slow")
    await drive(20)
    await attachment("right", 360)      # lower the arm
    await attachment("right", -360)     # raise it again
    await drive(-20)
    await turn_to(0)                    # face the start direction again
    await square_up(1.0, backwards=True, known_heading=0)