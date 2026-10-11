"""Small MuJoCo interface, independent of the research learning stack."""

from dataclasses import dataclass
from pathlib import Path

import mujoco
import numpy as np


@dataclass(frozen=True)
class MechanismState:
    """Owned copies of joint positions and velocities (radians, radians/s)."""

    time: float
    joint_position: np.ndarray
    joint_velocity: np.ndarray


class MechanismEnv:
    """Fixed-body mechanism with two illustrative velocity drives.

    This is a mechanical preview, with no flight task or learning interface.
    It has no reward, trained controller, reference trajectory, or data writer.
    """

    def __init__(self):
        model_file = Path(__file__).parent / "assets" / "mechanism.xml"
        self.model = mujoco.MjModel.from_xml_path(str(model_file))
        self.data = mujoco.MjData(self.model)
        self.actuator_names = tuple(
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, index)
            for index in range(self.model.nu)
        )
        self.joint_names = tuple(
            mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_JOINT, index)
            for index in range(self.model.njnt)
        )
        self.reset()

    @property
    def timestep(self):
        return float(self.model.opt.timestep)

    @property
    def command_limits(self):
        """Rows are actuator-coordinate velocity bounds, in radians/s."""
        return self.model.actuator_ctrlrange.copy()

    def reset(self):
        """Return to the model's geometric reference pose."""
        mujoco.mj_resetData(self.model, self.data)
        mujoco.mj_forward(self.model, self.data)
        return self.state()

    def state(self):
        return MechanismState(
            time=float(self.data.time),
            joint_position=self.data.qpos.copy(),
            joint_velocity=self.data.qvel.copy(),
        )

    def step(self, command, *, substeps=1):
        """Advance [left, right] drive speeds; reject invalid inputs.

        Positive equal inputs drive the mirrored gears in opposite joint
        directions. These are preview motor speeds, not firmware commands.
        """
        values = np.asarray(command, dtype=float)
        if values.shape != (self.model.nu,) or not np.all(np.isfinite(values)):
            raise ValueError("Provide one finite velocity per actuator.")
        if isinstance(substeps, bool) or not isinstance(substeps, (int, np.integer)) or substeps < 1:
            raise ValueError("substeps must be a positive integer.")
        limits = self.command_limits
        if np.any(values < limits[:, 0]) or np.any(values > limits[:, 1]):
            raise ValueError("Command exceeds the preview actuator limits.")
        self.data.ctrl[:] = values
        warning_counts = self.data.warning.number.copy()
        for _ in range(substeps):
            mujoco.mj_step(self.model, self.data)
        if (not np.all(np.isfinite(self.data.qpos))
                or not np.all(np.isfinite(self.data.qvel))
                or np.any(self.data.warning.number > warning_counts)):
            raise RuntimeError("MuJoCo reported an invalid or unstable preview state.")
        return self.state()
