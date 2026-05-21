import onnxruntime as ort
import numpy as np

class MLPPolicy:
    def __init__(self, policy_path):
        self.ort_session = ort.InferenceSession(policy_path, providers=["CPUExecutionProvider"])
        self.input_name = self.ort_session.get_inputs()[0].name
        self.output_names = [output.name for output in self.ort_session.get_outputs()]

    def get_action(self, state: np.ndarray):
        state = state.astype(np.float32)
        try:    
            _state = np.expand_dims(state, axis=0)
            action = self.ort_session.run(self.output_names, {self.input_name: _state})[0]
            action = np.squeeze(action, axis=0)
        except:
            action = self.ort_session.run(self.output_names, {self.input_name: state})[0]
        action = np.clip(action, -1, 1)
        return action

class LSTMPolicy:
    def __init__(self, config, policy_path):
        self.ort_session = ort.InferenceSession(policy_path, providers=["CPUExecutionProvider"])
        self.input_names = [self.ort_session.get_inputs()[0].name, "h_in", "c_in"]
        assert self.ort_session.get_inputs()[1].name == "h_in" and self.ort_session.get_inputs()[2].name == "c_in",\
            "The input names of ONNX policy must include 'h_in' and 'c_in'"

        self.h_in = np.zeros((1, 1, config["policy"]["h_in_dim"]), dtype=np.float32)
        self.c_in = np.zeros((1, 1, config["policy"]["c_in_dim"]), dtype=np.float32)

    def get_action(self, state):
        state = state.astype(np.float32)
        state = np.expand_dims(state, axis=0)
        policy_input = {self.input_names[0]: state,
                 "h_in": self.h_in,
                 "c_in": self.c_in,
                 }
        action, h_out, c_out = self.ort_session.run(None, policy_input)
        self.h_in = h_out
        self.c_in = c_out

        action = np.squeeze(action, axis=0)
        action = np.clip(action, -1, 1)
        return action

class EncoderPolicy:
    def __init__(self, encoder_path, policy_path):
        self.encoder_sess = ort.InferenceSession(encoder_path, providers=["CPUExecutionProvider"])
        self.policy_sess  = ort.InferenceSession(policy_path,  providers=["CPUExecutionProvider"])

        self.enc_in_name   = self.encoder_sess.get_inputs()[0].name
        self.enc_out_names = [o.name for o in self.encoder_sess.get_outputs()]

        self.pol_in_name   = self.policy_sess.get_inputs()[0].name
        self.pol_out_names = [o.name for o in self.policy_sess.get_outputs()]

    def _ensure_batch(self, arr: np.ndarray) -> np.ndarray:
        if arr.ndim == 1:
            return np.expand_dims(arr, axis=0)
        return arr

    def _run_encoder(self, obs_batched: np.ndarray) -> np.ndarray:
        out = self.encoder_sess.run(self.enc_out_names, {self.enc_in_name: obs_batched})[0]
        if out.ndim > 2:
            out = out.reshape(out.shape[0], -1)
        return out.astype(np.float32)

    def _concat(self, z: np.ndarray, obs_batched: np.ndarray) -> np.ndarray:
        if obs_batched.ndim > 2:
            obs_flat = obs_batched.reshape(obs_batched.shape[0], -1)
        else:
            obs_flat = obs_batched
        policy_in = np.concatenate([z, obs_flat], axis=-1)
        return policy_in.astype(np.float32)

    def get_action(self, state: np.ndarray) -> np.ndarray:
        state = state.astype(np.float32)
        obs_batched = self._ensure_batch(state)
        z = self._run_encoder(obs_batched)      
        policy_in = self._concat(z, obs_batched) 
        try:
            action = self.policy_sess.run(self.pol_out_names, {self.pol_in_name: policy_in})[0]
            if action.ndim >= 2 and action.shape[0] == 1:
                action = np.squeeze(action, axis=0)
        except:
            action = self.policy_sess.run(self.pol_out_names, {self.pol_in_name: policy_in.squeeze(axis=0)})[0]
        action = np.clip(action, -1, 1)
        return action   
    
def build_policy(config, policy_path, encoder_path=None):
    if config["policy"]["policy_type"] == "MLP":
        return MLPPolicy(policy_path)
    elif config["policy"]["policy_type"] == "LSTM":
        return LSTMPolicy(config, policy_path)
    elif config["policy"]["policy_type"] == "Encoder+MLP":
        return EncoderPolicy(encoder_path=encoder_path, policy_path=policy_path)
