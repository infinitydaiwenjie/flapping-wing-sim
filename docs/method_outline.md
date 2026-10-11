# Method outline

[中文说明](method_outline_zh.md)

The project connects a flapping-wing simulation environment with control-prior-guided policy learning. The earlier work is associated with ACAIT; the current manuscript names its method **Drift-Aware Proximal Policy Optimization (DA-PPO)**. The outline below describes the current framework at a conceptual level.

## Conceptual framework

**Control-prior initialization.** Demonstrations from a feedback controller provide an initial control behavior. Behavior cloning transfers that behavior into a policy that can serve as a starting point for learning through interaction.

**Drift-aware learning.** The initialized policy interacts with the simulator. Learning takes account of persistent position deviations as well as the vehicle's recent response. A policy and a value model are refined together within a PPO framework, with training progressively considering longer periods of motion.

**Control interface.** A reference and the simulated vehicle state supply context for the controller. The controller proposes actuator commands, and the simulator advances the vehicle dynamics. The environment and the learned controller have separate roles in this loop.

## Conceptual pseudocode

The following is a description of stages, without executable operations or implementation definitions:

```text
CONTROL-PRIOR INITIALIZATION
    Obtain demonstrations of feedback control.
    Form an initial policy through behavior cloning.

DRIFT-AWARE POLICY LEARNING
    Start from the initialized policy.
    Use simulator interaction to gather control experience.
    Consider persistent deviations when representing and assessing behavior.
    Refine the policy and value model within the drift-aware PPO framework.
    Extend the period of motion considered during learning.

CONTROLLER USE
    Connect the learned policy to the reference, state, and actuator interfaces.
```

## Relationship to the code

This document describes the method conceptually. The executable code in this repository provides a mechanical simulation interface; the learning procedure above is pseudocode, without a training implementation or learned policy. See [component scope](release_scope.md) for the supplied modules.
