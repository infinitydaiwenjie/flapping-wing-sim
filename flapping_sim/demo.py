"""Short, fixed-body mechanical demonstration; creates no recordings."""

import argparse
import math
import time

from .environment import MechanismEnv


def positive_int(value):
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("steps must be positive")
    return parsed


def finite_float(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise argparse.ArgumentTypeError("speed must be finite")
    return parsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--viewer", action="store_true", help="open the MuJoCo viewer")
    parser.add_argument("--steps", type=positive_int, default=2000)
    parser.add_argument("--speed", type=finite_float, default=2.0,
                        help="illustrative drive speed in radians/s")
    args = parser.parse_args()
    env = MechanismEnv()
    bounds = env.command_limits
    if any(args.speed < lo or args.speed > hi for lo, hi in bounds):
        parser.error("speed is outside the model's preview drive limits")
    command = [args.speed, args.speed]
    if args.viewer:
        import mujoco.viewer

        with mujoco.viewer.launch_passive(env.model, env.data) as viewer:
            with viewer.lock():
                viewer.cam.lookat[:] = env.model.stat.center
                viewer.cam.distance = 1.1
                viewer.cam.azimuth = 140
                viewer.cam.elevation = -20
            for _ in range(args.steps):
                if not viewer.is_running():
                    break
                started = time.perf_counter()
                with viewer.lock():
                    env.step(command)
                viewer.sync()
                time.sleep(max(0.0, env.timestep - (time.perf_counter() - started)))
    else:
        env.step(command, substeps=args.steps)
    print("Mechanical preview completed. No recording was created.")


if __name__ == "__main__":
    main()
