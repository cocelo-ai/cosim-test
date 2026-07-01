from envs.wrappers import StateBuildWrapper, TimeLimitWrapper, CommandWrapper


SUPPORTED_ENVS = {
    "flamingo_light_p_v3": (
        "envs.flamingo_light_p_v3.flamingo_light_p_v3",
        "FlamingoLightPV3",
    ),
    "flamingo_p_v3_1": (
        "envs.flamingo_p_v3_1.flamingo_p_v3",
        "FlamingoPV31",
    ),
    "wheeldog_p_v2": (
        "envs.wheeldog_p_v2.wheeldog_p_v2",
        "WheelDogPV2",
    ),
    "humanoid_light_v2": (
        "envs.humanoid_light_v2.humanoid_light_v2",
        "HumanoidLightV2",
    ),
}


def _load_env_class(env_id):
    try:
        module_path, class_name = SUPPORTED_ENVS[env_id]
    except KeyError as exc:
        supported_ids = ", ".join(sorted(SUPPORTED_ENVS))
        raise NameError(
            f"Please select a valid environment id. "
            f"Received '{env_id}'. Supported ids: {supported_ids}."
        ) from exc

    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


def get_supported_env_ids():
    return tuple(SUPPORTED_ENVS)


def build_env(config):
    env_id = config["env"]["id"]
    env_cls = _load_env_class(env_id)
    render_flag = bool(config.get("env", {}).get("render", True))
    render_mode = config.get("env", {}).get("render_mode", "human")
    env = env_cls(config, render_flag=render_flag, render_mode=render_mode)
    
    env = StateBuildWrapper(env, config)
    env = TimeLimitWrapper(env, config)
    env = CommandWrapper(env, config)

    return env
