import os

class ConfigManager:
    def __init__(self, env_file="../../.env"):
        self._load_env(env_file)

    def _load_env(self, env_file):
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

    def get(self, key, default=None):
        return os.getenv(key, default)