# Calibration: robot should drive 50 cm, turn RIGHT 90, turn LEFT 90, return.
from robot import *


async def run():
    await drive(50)
    await turn(90)
    await turn(-90)
    await drive(-50)
