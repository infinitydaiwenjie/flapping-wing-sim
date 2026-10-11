"""Software invariants using synthetic inputs; no research reference outputs."""

import unittest

import numpy as np

from flapping_sim import MechanismEnv
from flapping_sim.physics import (
    BladeElementParameters, DCMotorParameters,
    blade_element_force, dc_motor_torque,
)


class MechanicalPreviewTests(unittest.TestCase):
    def test_step_reset_and_state_ownership(self):
        env = MechanismEnv()
        initial = env.state()
        before = initial.joint_position.copy()
        advanced = env.step([2.0, 2.0], substeps=2000)
        self.assertGreater(advanced.time, initial.time)
        self.assertTrue(np.isfinite(advanced.joint_position).all())
        self.assertGreater(np.linalg.norm(advanced.joint_position - before), 0)
        np.testing.assert_array_equal(initial.joint_position, before)
        self.assertFalse(np.any(env.data.warning.number))
        restored = env.reset()
        np.testing.assert_array_equal(restored.joint_position, before)
        np.testing.assert_array_equal(restored.joint_velocity, initial.joint_velocity)
        self.assertEqual(restored.time, initial.time)

    def test_invalid_commands_do_not_advance_time(self):
        env = MechanismEnv()
        for command in ([float("nan"), 0], [0], [[0, 0]], [float("inf"), 0], [1000, 0]):
            with self.subTest(command=command), self.assertRaises(ValueError):
                env.step(command)
        for count in (0, -1, True, 1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                env.step([0, 0], substeps=count)
        self.assertEqual(env.state().time, 0)

    def test_fixed_body_and_complete_mesh_loading(self):
        env = MechanismEnv()
        self.assertEqual(env.model.nmesh, 20)
        self.assertEqual(env.actuator_names, ("drive_left", "drive_right"))
        pose = env.data.body("torso").xpos.copy()
        env.step([-2, -2], substeps=1000)
        np.testing.assert_array_equal(env.data.body("torso").xpos, pose)
        self.assertEqual(env.model.nq, env.model.njnt)


class GenericPhysicsTests(unittest.TestCase):
    def test_passive_motor_dissipates_energy(self):
        # Artificial unit-scale parameters, unrelated to a vehicle.
        motor = DCMotorParameters(1, 1, 1, 1, 1)
        speeds = np.array([-3, -1, 0, 1, 3], dtype=float)
        torque = dc_motor_torque(0, speeds, motor)
        self.assertTrue(np.all(torque * speeds <= 0))
        np.testing.assert_allclose(torque, -torque[::-1])
        np.testing.assert_allclose(dc_motor_torque([-100, 100], 0, motor), [-1, 1])

    def test_element_zero_flow_and_force_directions(self):
        # Unit-scale coefficients test direction and scaling, not calibration.
        element = BladeElementParameters(1, 1, 1, 1, 0, 1, 0)
        np.testing.assert_array_equal(blade_element_force([0, 0], 0, element), [0, 0])
        force = blade_element_force([1, 0], 1, element)
        self.assertGreater(force[0], 0)
        self.assertGreater(force[1], 0)
        np.testing.assert_allclose(blade_element_force([2, 0], 1, element), 4 * force)
        np.testing.assert_allclose(blade_element_force([-1, 0], 1, element), -force)

    def test_parameter_and_input_validation(self):
        with self.assertRaises(ValueError):
            DCMotorParameters(0, 1, 1, 1, 1)
        with self.assertRaises(ValueError):
            BladeElementParameters(1, 1, 1, 1, float("nan"), 1, 0)
        element = BladeElementParameters(1, 1, 1, 1, 0, 1, 0)
        with self.assertRaises(ValueError):
            blade_element_force([1, 2, 3], 0, element)
        with self.assertRaises(ValueError):
            blade_element_force([float("nan"), 0], 0, element)


if __name__ == "__main__":
    unittest.main()
