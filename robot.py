"""Base library for our SPIKE Prime robot (SPIKE App 3, Python).

Every function here is 'async': ALWAYS write  await  in front of it, e.g.
    await drive(30)
Functions that are NOT async (heading, reflection, set_speed ...) need no await.
"""
import math
import time
import motor
import motor_pair
import runloop
import color_sensor
import distance_sensor
import sound
from hub import motion_sensor, light_matrix, button
from config import *

_PAIR = motor_pair.PAIR_1
_speed = SPEEDS[DEFAULT_SPEED]
_target = 0.0          # the heading (degrees) the robot is trying to keep


# ---------- internal helpers ----------
def _wrap(angle):
    """Turn any angle into the range -180..180."""
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


def _cm_to_deg(cm):
    return cm / (math.pi * WHEEL_DIAMETER_CM) * 360


def _travelled():
    """Average wheel degrees travelled since _reset_distance()."""
    return (abs(motor.relative_position(LEFT_MOTOR)) +
            abs(motor.relative_position(RIGHT_MOTOR))) / 2


def _reset_distance():
    motor.reset_relative_position(LEFT_MOTOR, 0)
    motor.reset_relative_position(RIGHT_MOTOR, 0)


def _elapsed(start):
    return time.ticks_diff(time.ticks_ms(), start)


def _stop():
    motor_pair.stop(_PAIR, stop=motor.BRAKE)


def _resolve_speed(speed):
    if speed is None:
        return _speed
    if isinstance(speed, str):
        return SPEEDS[speed]
    return abs(speed)


# ---------- setup / state ----------
def heading():
    """Current heading in degrees. Right/clockwise = positive."""
    return GYRO_SIGN * motion_sensor.tilt_angles()[0] / 10


async def set_heading(angle=0):
    """Tell the robot 'you are currently facing <angle>' (0 = start direction)."""
    global _target
    motion_sensor.reset_yaw(int(GYRO_SIGN * angle * 10))
    await runloop.sleep_ms(100)
    _target = angle


def set_speed(name):
    """name: 'slow', 'medium' or 'fast' (or a number). Used by drive/arc/follow_line."""
    global _speed
    _speed = _resolve_speed(name)


async def init():
    """Call once at the very start. Keep the robot still!"""
    motor_pair.pair(_PAIR, LEFT_MOTOR, RIGHT_MOTOR)
    light_matrix.write("...")
    await runloop.sleep_ms(1000)
    await set_heading(0)
    set_speed(DEFAULT_SPEED)
    await beep()


# ---------- driving ----------
async def drive(cm, speed=None):
    """Drive straight. Positive = forward, negative = backward. Holds the gyro heading."""
    v = _resolve_speed(speed)
    d = 1 if cm >= 0 else -1
    target_deg = _cm_to_deg(abs(cm))
    timeout = int(target_deg / MIN_SPEED * 1000) + 2000
    _reset_distance()
    start = time.ticks_ms()
    while _elapsed(start) < timeout:
        done = _travelled()
        remaining = target_deg - done
        if remaining <= 0:
            break
        s = min(v, MIN_SPEED + done * ACCEL_GAIN, MIN_SPEED + remaining * DECEL_GAIN)
        corr = _wrap(_target - heading()) * KP_DRIVE   # + = need to steer right
        motor_pair.move_tank(_PAIR, int(d * s + corr), int(d * s - corr))
        await runloop.sleep_ms(10)
    _stop()


async def turn(degrees, max_speed=None):
    """Pivot on the spot. Positive = right (clockwise), negative = left."""
    global _target
    _target = _wrap(_target + degrees)
    top = MAX_TURN_SPEED if max_speed is None else abs(max_speed)
    start = time.ticks_ms()
    settled = 0
    while _elapsed(start) < TURN_TIMEOUT_MS:
        err = _wrap(_target - heading())
        if abs(err) <= TURN_TOLERANCE:
            _stop()
            settled += 1
            if settled >= 3:
                break
        else:
            settled = 0
            s = min(top, max(MIN_TURN_SPEED, abs(err) * KP_TURN))
            sign = 1 if err > 0 else -1
            motor_pair.move_tank(_PAIR, int(sign * s), int(-sign * s))
        await runloop.sleep_ms(10)
    _stop()


async def turn_to(angle, max_speed=None):
    """Turn to an absolute heading (0 = the direction the robot started in)."""
    await turn(_wrap(angle - _target), max_speed)


async def arc(radius_cm, degrees, speed=None):
    """Drive forward along a circle.
    radius_cm: from the circle's centre to the middle of the robot.
    degrees: positive = curve right, negative = curve left."""
    global _target
    half = AXLE_TRACK_CM / 2
    r = abs(radius_cm)
    if r <= half:
        raise ValueError("radius must be bigger than half the axle track")
    v = _resolve_speed(speed)
    ratio = (r - half) / (r + half)
    outer, inner = v, int(v * ratio)
    left, right = (outer, inner) if degrees > 0 else (inner, outer)
    outer_deg = _cm_to_deg((r + half) * math.radians(abs(degrees)))
    timeout = int(outer_deg / v * 2000) + 1000
    last = heading()
    turned = 0
    start = time.ticks_ms()
    while abs(turned) < abs(degrees) and _elapsed(start) < timeout:
        motor_pair.move_tank(_PAIR, int(left), int(right))
        await runloop.sleep_ms(10)
        h = heading()
        turned += _wrap(h - last)
        last = h
    _stop()
    _target = _wrap(_target + degrees)


async def follow_line(cm, edge="right", speed=None):
    """Follow a black line with the colour sensor for <cm> centimetres.
    edge: which edge of the line the sensor rides on ('right' or 'left').
    Afterwards the robot keeps whatever direction it ended up facing."""
    global _target
    v = _resolve_speed(speed)
    sgn = -1 if edge == "right" else 1
    target_deg = _cm_to_deg(abs(cm))
    timeout = int(target_deg / MIN_SPEED * 1000) + 2000
    _reset_distance()
    start = time.ticks_ms()
    while _travelled() < target_deg and _elapsed(start) < timeout:
        err = color_sensor.reflection(COLOR_SENSOR) - LINE_TARGET
        corr = sgn * err * KP_LINE
        motor_pair.move_tank(_PAIR, int(v + corr), int(v - corr))
        await runloop.sleep_ms(10)
    _stop()
    _target = heading()


async def square_up(seconds=1.0, backwards=True, known_heading=None):
    """Push gently into a wall to straighten the robot.
    known_heading: if you know the wall's direction (e.g. 0 or 90), the gyro
    is reset to it, which removes drift."""
    global _target
    v = SPEEDS["slow"] * (-1 if backwards else 1)
    motor_pair.move_tank(_PAIR, v, v)
    await runloop.sleep_ms(int(seconds * 1000))
    _stop()
    if known_heading is not None:
        await set_heading(known_heading)
    else:
        _target = heading()


# ---------- attachments (motors on C / D) ----------
async def attachment(name, degrees, speed=None):
    """Turn an attachment motor. name: key from ATTACHMENTS ('left'/'right').
    Positive degrees = one way, negative = the other."""
    v = ATTACHMENT_SPEED if speed is None else abs(speed)
    await motor.run_for_degrees(ATTACHMENTS[name], abs(degrees), v if degrees >= 0 else -v)


def attachment_start(name, speed=None):
    """Start spinning an attachment (does not wait). Stop it with attachment_stop."""
    v = ATTACHMENT_SPEED if speed is None else speed
    motor.run(ATTACHMENTS[name], v)


def attachment_stop(name):
    motor.stop(ATTACHMENTS[name], stop=motor.BRAKE)


# ---------- sensors ----------
def reflection():
    """Brightness under the colour sensor, 0 (dark) to 100 (bright)."""
    return color_sensor.reflection(COLOR_SENSOR)


def distance_cm():
    """Distance to object in cm, or -1 if nothing is seen."""
    mm = distance_sensor.distance(DISTANCE_SENSOR)
    return -1 if mm < 0 else mm / 10


# ---------- hub helpers ----------
async def beep(freq=880, ms=150):
    await sound.beep(freq, ms, 100)


def show(text):
    light_matrix.write(str(text))


async def wait_for_button(which=None):
    """Pause until the RIGHT hub button is pressed (and released)."""
    b = button.RIGHT if which is None else which
    await runloop.until(lambda: button.pressed(b) > 0)
    await runloop.until(lambda: button.pressed(b) == 0)


async def menu(missions):
    """missions: list of (label, async_function).
    LEFT button = next mission, RIGHT button = start it."""
    i = 0
    while True:
        light_matrix.write(missions[i][0])
        await runloop.until(lambda: button.pressed(button.LEFT) > 0 or
                            button.pressed(button.RIGHT) > 0)
        if button.pressed(button.RIGHT) > 0:
            await runloop.until(lambda: button.pressed(button.RIGHT) == 0)
            await set_heading(0)
            await missions[i][1]()
            _stop()
        else:
            await runloop.until(lambda: button.pressed(button.LEFT) == 0)
            i = (i + 1) % len(missions)