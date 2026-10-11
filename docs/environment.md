# Environment interface

`MechanismEnv` loads the bundled MuJoCo mechanism using paths relative to its
Python package. It requires no private project directory or external model.

## What runs

The torso is fixed to the world. Two velocity drives actuate the mirrored gear
chains; linkage closure is handled by MuJoCo. Gravity and contact are disabled
for this bench-style demonstration. The preview has no aerodynamic flight loop.

Geometry is retained from the project assembly. Masses, inertia tensors, joint
dynamics, drive gains, integration settings, and constraint solver settings
are newly assigned illustrative values. They are not a perturbed or rounded
copy of the identified parameter set. See the [asset notes](../flapping_sim/assets/README.md).

## API

| API | Meaning |
| --- | --- |
| `reset()` | Restore the geometric reference pose and return its state |
| `step(command, substeps=1)` | Advance a positive integer number of integration steps |
| `state()` | Copy current time, joint coordinates, and joint velocities |
| `joint_names` | Joint names in coordinate order; this model uses hinge joints |
| `actuator_names` | Input names in actuator order |
| `command_limits` | Copy of illustrative actuator velocity bounds |
| `timestep` | Preview integration interval in seconds |
| `model`, `data` | Advanced access to native MuJoCo objects |

`command` contains `[left_speed, right_speed]` in actuator-coordinate radians
per second. Positive equal commands drive mirrored joint directions. Invalid
shape, non-finite values, out-of-range commands, and invalid step counts are
rejected. The returned arrays are copies, so a later step does not overwrite
a previously returned state.

The environment has no Gymnasium task, reward, termination criterion, learned
policy, firmware mapping, observation preprocessing, or performance metric.

## Extension utilities

`physics.py` provides independent generic motor and blade-element calculations.
All model parameters must be supplied explicitly. These helpers are **not wired
into the mechanical demo** and do not recreate the research force model. Their
docstrings define the units, signs, and assumptions. A physical flight model
requires independent parameterization and validation by the user.

## Engine documentation

The implementation uses the official MuJoCo Python bindings. See the
[Python API](https://mujoco.readthedocs.io/en/stable/python.html) and
[MJCF reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html)
for model and viewer semantics.
