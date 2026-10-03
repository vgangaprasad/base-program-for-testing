"""Robot settings. Change numbers HERE, not in robot.py."""
from hub import port

# ----- Ports -----
LEFT_MOTOR = port.A
RIGHT_MOTOR = port.B
ATTACHMENTS = {"left": port.C, "right": port.D}   # names you use in missions
COLOR_SENSOR = port.E        # pointing down at the mat
DISTANCE_SENSOR = port.F

# ----- Robot size -----
WHEEL_DIAMETER_CM = 5.6      # SPIKE small wheel = 56 mm
AXLE_TRACK_CM = 11.2         # distance between wheel centres (only used by arc)

# ----- Gyro -----
# Hub must lie FLAT. We want: turning RIGHT (clockwise) = positive angle.
# If calibrate (m00) turns the wrong way or spins, change -1 to 1.
GYRO_SIGN = -1

# ----- Speeds (motor degrees per second) -----
SPEEDS = {"slow": 250, "medium": 500, "fast": 800}
DEFAULT_SPEED = "medium"
ATTACHMENT_SPEED = 500

# ----- Tuning (ask your coach before changing) -----
MIN_SPEED = 120          # slowest the robot creeps at start/end of a drive
ACCEL_GAIN = 2.0         # speed gained per degree of wheel travel
DECEL_GAIN = 1.5         # braking ramp near the target
KP_DRIVE = 6.0           # how hard to correct heading while driving
KP_TURN = 8.0            # how hard to correct while turning
MIN_TURN_SPEED = 80
MAX_TURN_SPEED = 400
TURN_TOLERANCE = 1.0     # degrees
TURN_TIMEOUT_MS = 4000
LINE_TARGET = 50         # reflection value on the line's edge (0-100)
KP_LINE = 3.0