import random
import string
import yaml as yaml


def get_random_suffix(prefix:str, length:int=10) -> str:
    return prefix+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


class ConfigLoader:
    def __init__(self, path="../../config/application-dev.yml"):
        self.path = path
        with open(path) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def get_nested(self, dotted_key: str, default=None):
        keys = dotted_key.split(".")
        value = self.config
        for k in keys:
            if k not in value:
                return default
            value = value[k]
        return value

    def get_property(self, key: str, default=None):
        if "." in key:
            return self.get_nested(key, default)
        else:
            return self.get(key, default)

    def reload(self, path=None):
        if path:
            self.path = path
        with open(self.path) as f:
            self.config = yaml.safe_load(f)