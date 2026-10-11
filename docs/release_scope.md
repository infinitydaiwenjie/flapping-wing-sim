# Component scope

The repository supports mechanical model inspection, mechanism simulation, and
interface development. The following table describes the supplied components.

| Component | Present scope |
| --- | --- |
| Mechanical geometry | Meshes, body transforms, joint axes, linkage connectivity |
| Mechanical stepping | Fixed body, illustrative inertias and drive dynamics |
| Flight aerodynamics | Generic extension helper only; no identified flight model |
| Motor model | Generic extension helper only; no identified actuator mapping |
| Learning algorithm | Narrative and non-executable conceptual pseudocode |
| Experiments | No tasks, data, protocols, seeds, metrics, or outputs |
| Trained controller | Not included |

## Model assumptions

Mesh dimensions, assembly transforms, hinge directions, and closed-chain
connections describe the project geometry. The dynamic parameters are
illustrative settings for the mechanism demo, rather than measured vehicle
properties. The torso is fixed, gravity and contact are disabled, and the
standalone physics helpers are not connected to the demo's stepping loop.

See the [asset notes](../flapping_sim/assets/README.md) for model settings and
the [environment documentation](environment.md) for units and API semantics.

## Learning and experiments

The [method outline](method_outline.md) describes the learning framework. The
repository does not include its executable training implementation, learned
policies, identified flight parameters, or experiment data and protocols.
It does not provide a complete reproduction package for the paper experiments.

The file manifest verifies the contents of this repository. Software tests
check implementation behavior and do not evaluate flight-control performance.
