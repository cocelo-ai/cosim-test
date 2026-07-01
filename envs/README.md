# Environment Scope

This repository keeps the sim-to-sim runtime path intentionally small.

`envs.build.build_env()` only registers environments that are ready for the
lightweight verifier. At the moment those are:

- `flamingo_light_p_v3`
- `flamingo_p_v3_1`
- `wheeldog_p_v2`
- `humanoid_light_v2`

Other robot folders may exist under `envs/` as reference ports, but they should
not be imported by the verifier until they are reduced to the same minimal
interface:

- `reset() -> (obs, info)`
- `step(action) -> (obs, terminated, truncated, info)`
- `render()`
- `close()`
- `event("push", value)`
- `get_data()`
- `id`, `action_dim`, `control_freq`, `obs_to_dim`

Keep optional robot-specific features behind the robot implementation. Shared
runtime code should only depend on the interface above.
