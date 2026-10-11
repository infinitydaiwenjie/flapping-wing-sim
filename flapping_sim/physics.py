"""Optional generic motor and blade-element helpers for an educational preview.

These simplified equations are not the identified research simulator. All
physical parameters must be supplied by the caller; no fitted coefficients,
vehicle parameters, experiment settings, or control policies are included.
"""

from dataclasses import dataclass, fields
from numbers import Real

import numpy as np


def _validate_parameters(instance, positive, nonnegative=()):
    """Validate scalar dataclass fields and normalize them to Python floats."""
    for field in fields(instance):
        value = getattr(instance, field.name)
        if not isinstance(value, Real) or isinstance(value, bool):
            raise ValueError(f"{field.name} must be a real scalar")
        value = float(value)
        if not np.isfinite(value):
            raise ValueError(f"{field.name} must be finite")
        if field.name in positive and value <= 0:
            raise ValueError(f"{field.name} must be positive")
        if field.name in nonnegative and value < 0:
            raise ValueError(f"{field.name} must be nonnegative")
        object.__setattr__(instance, field.name, value)


def _finite_array(value, name):
    array = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


@dataclass(frozen=True)
class DCMotorParameters:
    """Explicit motor constants in SI units, without inductance or gearing.

    Current is symmetrically limited by ``maximum_current_a``. Viscous
    friction opposes shaft motion and may be zero. Positive voltage, positive
    current, and positive shaft torque follow the same rotation convention.
    """

    resistance_ohm: float
    torque_constant_nm_per_a: float
    back_emf_v_per_rad_s: float
    viscous_friction_nm_per_rad_s: float
    maximum_current_a: float

    def __post_init__(self):
        _validate_parameters(
            self,
            positive=(
                "resistance_ohm",
                "torque_constant_nm_per_a",
                "back_emf_v_per_rad_s",
                "maximum_current_a",
            ),
            nonnegative=("viscous_friction_nm_per_rad_s",),
        )


def dc_motor_torque(voltage_v, angular_velocity_rad_s, parameters):
    """Return signed net shaft torque in N m with NumPy broadcasting.

    The quasi-static armature model is I = (V - Ke * omega) / R, followed by
    symmetric current clipping; net torque is Kt * I - b * omega. This helper
    does not integrate rotor dynamics, model a power supply, or choose voltage.
    """
    if not isinstance(parameters, DCMotorParameters):
        raise TypeError("parameters must be DCMotorParameters")
    voltage = _finite_array(voltage_v, "voltage_v")
    velocity = _finite_array(angular_velocity_rad_s, "angular_velocity_rad_s")
    p = parameters
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            current = (voltage - p.back_emf_v_per_rad_s * velocity) / p.resistance_ohm
            current = np.clip(current, -p.maximum_current_a, p.maximum_current_a)
            torque = p.torque_constant_nm_per_a * current
            torque = torque - p.viscous_friction_nm_per_rad_s * velocity
        except FloatingPointError as exc:
            raise ValueError("motor calculation exceeded finite numeric range") from exc
    return torque


@dataclass(frozen=True)
class BladeElementParameters:
    """Caller-supplied area and coefficients for a small-angle element model.

    CL = lift_slope_per_rad * (alpha - zero_lift_angle_rad), and
    CD = drag_coefficient_zero + induced_drag_factor * CL**2.
    Density, chord, element span, and lift slope must be positive. Both drag
    coefficients may be zero. No stall or unsteady aerodynamic model is used.
    """

    air_density_kg_per_m3: float
    chord_m: float
    element_span_m: float
    lift_slope_per_rad: float
    zero_lift_angle_rad: float
    drag_coefficient_zero: float
    induced_drag_factor: float

    def __post_init__(self):
        _validate_parameters(
            self,
            positive=(
                "air_density_kg_per_m3",
                "chord_m",
                "element_span_m",
                "lift_slope_per_rad",
            ),
            nonnegative=("drag_coefficient_zero", "induced_drag_factor"),
        )


def blade_element_force(relative_air_velocity_xz, angle_of_attack_rad, parameters):
    """Return force ON the element in its local x-z plane, in newtons.

    Velocity is air velocity minus element velocity, shaped (..., 2), with
    components (vx, vz). Local +x runs from leading to trailing edge; +z is
    the chosen wing-normal direction. Drag follows the relative air velocity.
    Positive lift points along (-vz, vx), so flow along +x produces lift along
    +z when CL is positive. Supply a signed angle of attack consistent with
    this lift convention; it is not inferred from velocity by this helper.

    Angle and velocity batch dimensions follow NumPy broadcasting. The output
    has shape (..., 2). Exactly zero flow yields exactly zero force. Spanwise
    flow, rotational circulation, added mass, and wake history are omitted.
    """
    if not isinstance(parameters, BladeElementParameters):
        raise TypeError("parameters must be BladeElementParameters")
    velocity = _finite_array(relative_air_velocity_xz, "relative_air_velocity_xz")
    if velocity.ndim < 1 or velocity.shape[-1] != 2:
        raise ValueError("relative_air_velocity_xz must have shape (..., 2)")
    alpha = _finite_array(angle_of_attack_rad, "angle_of_attack_rad")
    vx, vz, alpha = np.broadcast_arrays(velocity[..., 0], velocity[..., 1], alpha)
    p = parameters
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        try:
            speed = np.hypot(vx, vz)
            ux = np.divide(vx, speed, out=np.zeros_like(speed), where=speed != 0)
            uz = np.divide(vz, speed, out=np.zeros_like(speed), where=speed != 0)
            cl = p.lift_slope_per_rad * (alpha - p.zero_lift_angle_rad)
            cd = p.drag_coefficient_zero + p.induced_drag_factor * cl**2
            q_area = 0.5 * p.air_density_kg_per_m3 * speed**2
            q_area = q_area * p.chord_m * p.element_span_m
            force = np.stack((q_area * (cd * ux - cl * uz),
                              q_area * (cd * uz + cl * ux)), axis=-1)
        except FloatingPointError as exc:
            raise ValueError("element calculation exceeded finite numeric range") from exc
    return force
