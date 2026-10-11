# Mechanical assets

`mechanism.xml` contains a fixed-body MuJoCo mechanism with four wings. Its
mesh geometry, body transforms, hinge axes, and linkage closure relationships
come from the project's CAD-derived model. The binary STL headers are blank;
their triangle geometry is preserved.

This release deliberately uses illustrative dynamics. Every moving body has
the same placeholder mass (0.01 kg), an isotropic inertia of 0.0001 kg m²,
and its centre of mass at its local origin. These values do not describe the
physical vehicle. The torso is fixed, the wing-root and dihedral mounts are
held at their initial poses, gravity is disabled, and collision forces are
disabled. The model demonstrates articulation under these assumptions.

The simulation step is 0.001 s with the `implicitfast` integrator. Joint damping
is 0.002 and armature is 0.00002 in MuJoCo's SI-unit convention. Closure
constraints use MuJoCo's default solver parameters. These choices are public
preview settings, without identification or flight-validation claims.

The two controls, in order, are `drive_left` and `drive_right`. They are ideal
velocity drives with a gain of 0.02, command limits of ±12 rad/s and force
limits of ±0.05 N m. The right drive uses a negative transmission direction,
so equal positive commands turn the mirrored mechanisms in corresponding
directions. They are generic MuJoCo drives, without an electrical motor model.

No aerodynamic forces, flight controller, learned policy, training task,
experimental calibration, or benchmark outcome is included in these assets.
Geometric dimensions are still observable in the meshes and joint transforms.
