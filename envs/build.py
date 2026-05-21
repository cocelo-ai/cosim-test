from envs.flamingo_light_p_v3.flamingo_light_p_v3 import FlamingoLightPV3

from envs.wrappers import StateBuildWrapper, TimeLimitWrapper, CommandWrapper


def build_env(config):
    if config["env"]['id'] == "flamingo_light_p_v3":
      env = FlamingoLightPV3(config)
    else:
      raise NameError(f"Please select a valid environment id. Received '{config['env']['id']}'.")
    
    env = StateBuildWrapper(env, config)
    env = TimeLimitWrapper(env, config)
    env = CommandWrapper(env, config)

    return env
