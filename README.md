# FLL Base Code (SPIKE Prime, SPIKE App 3, Python)

## Repo layout
- `config.py`  ports, wheel size, speeds, tuning (change numbers here)
- `robot.py`   the base library (don't edit during the season unless the coach agrees)
- `missions/`  one file per mission, each with `async def run():`
- `build.py`   glues everything into one file for the SPIKE App

## Workflow for a new mission
1. Copy `missions/template.py` to `missions/m03_name.py` and write `run()`.
2. On a computer: `python build.py m03_name`
3. Open `build/m03_name.py`, copy all text, paste into a new Python project in the SPIKE App, run.
4. Place the robot, keep it still, press the RIGHT hub button to start.
5. Final competition file: `python build.py all` gives a menu (LEFT = next mission, RIGHT = start).

Missions can't share function names with each other (all files are glued together).

## First-time setup (do once per robot)
1. Edit `config.py`: ports, `WHEEL_DIAMETER_CM`, `AXLE_TRACK_CM`.
2. `python build.py m00_calibrate`, run it with the hub flat on the robot.
   - Turns wrong way or spins: flip `GYRO_SIGN` (-1 <-> 1).
   - Drives the wrong distance: fix `WHEEL_DIAMETER_CM` (measure the real distance, scale the number).
   - Drives backwards: swap which motors are left/right, or check cables/ports.

## Functions (all with `await` unless noted)
| Call | What it does |
|---|---|
| `drive(cm, speed=None)` | straight, gyro-held; negative = backward |
| `turn(deg)` | pivot, + right / - left |
| `turn_to(angle)` | turn to absolute heading |
| `arc(radius_cm, deg)` | curve; + right / - left |
| `follow_line(cm, edge)` | follow black line |
| `square_up(sec, backwards, known_heading)` | push on wall, optionally reset gyro |
| `attachment(name, deg)` | move attachment motor |
| `attachment_start/stop(name)` | no await; run until stopped |
| `set_speed("slow"/"medium"/"fast")` | no await |
| `heading()`, `reflection()`, `distance_cm()` | no await; sensor values |
| `beep()`, `show(text)`, `wait_for_button()` | hub helpers |

`speed` can be `"slow"`, `"medium"`, `"fast"` or a number (deg/s).