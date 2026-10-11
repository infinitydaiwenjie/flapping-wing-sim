# Flapping-Wing Mechanical Simulation

[中文](README_zh.md)

A MuJoCo mechanical model and Python interface for an X-wing flapping-wing
vehicle. The repository brings together CAD-derived geometry, articulated
linkages, simulation utilities, and an overview of the DA-PPO learning framework.

See the [method overview](docs/method_outline.md) for control-prior initialization
and drift-aware policy learning.

## Features

- Mesh geometry and articulated closed-chain mechanism topology.
- A standalone interface for reset, stepping, and reading joint states.
- A short open-loop demonstration, optionally with an interactive viewer.
- Generic, parameter-required motor and blade-element utilities for extension.
- An outline of the ACAIT work and the current DA-PPO framework.

## Quick start

Use Python 3.10–3.12. From this repository root, install the dependencies
into your Python environment and run:

```bash
python -m pip install -r requirements.txt
python -B -m flapping_sim.demo
python -B -m flapping_sim.demo --viewer --steps 8000
```

On macOS, use `mjpython -B -m flapping_sim.demo --viewer --steps 8000` for the
interactive viewer, as described in the [MuJoCo Python documentation](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer).
A headless run needs no display. The demo runs an open-loop mechanism with
configurable drive speed and duration.

## Python interface

```python
from flapping_sim import MechanismEnv

env = MechanismEnv()
state = env.reset()
state = env.step([2.0, 2.0], substeps=10)
```

The two inputs are left and right drive speeds in actuator-coordinate radians
per second. Returned states contain time, joint positions, and joint velocities.
See the [interface documentation](docs/environment.md) for details.

## Model and method scope

The bundled model demonstrates a fixed-body mechanism with illustrative dynamic
parameters. The motor and blade-element utilities are independent extension
helpers. DA-PPO is described through conceptual pseudocode; a training
implementation, trained policies, and the calibrated flight setup used for
the paper experiments are not included. See [component scope](docs/release_scope.md).

## Repository contents

| Path | Purpose |
| --- | --- |
| `flapping_sim/assets/` | Mechanical geometry and illustrative MJCF |
| `flapping_sim/environment.py` | MuJoCo stepping interface |
| `flapping_sim/physics.py` | Generic helpers requiring user-supplied parameters |
| `flapping_sim/demo.py` | Fixed-body mechanical demonstration |
| `docs/` | Environment scope and conceptual method notes |
| `tests/` | Software checks with synthetic inputs |
| `tools/check_release.py` | Verify the exact public file manifest |

## Verification

```bash
python -B tools/check_release.py
python -B -m unittest discover -s tests
```

The software checks exercise the interface and generic physics helpers. The
manifest check verifies file contents and detects additional or modified files.

## License

A distribution license has not yet been selected. MuJoCo and NumPy are installed
separately and retain their respective licenses.
