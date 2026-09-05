import os
import random
import string
from datetime import date

import yaml as yaml
from typing import Optional, Any, Dict, List



def get_random_suffix(prefix:str, length:int=10) -> str:
    return prefix+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def get_today_date(format:str="%Y-%m-%d") -> str:
    # Get today's date
    today = date.today()
    # Format as YYYY-MM-DD
    return today.strftime(format)


class ConfigLoader:
    def __init__(self, path: Optional[str] = None):
        env = os.getenv("APP_ENV", "dev")
        self.path = path or f"../../config/application-{env}.yml"
        self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                self.config: Dict[str, Any] = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise RuntimeError(f"Config file not found: {self.path}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.config.get(key, default)

    def get_nested(self, dotted_key: str, default: Optional[Any] = None) -> Any:
        keys = dotted_key.split(".")
        value = self.config
        for k in keys:
            if not isinstance(value, dict) or k not in value:
                return default
            value = value[k]
        return value

    def get_property(self, key: str, default: Optional[Any] = None) -> Any:
        return self.get_nested(key, default) if "." in key else self.get(key, default)

    def reload(self, path: Optional[str] = None):
        if path:
            self.path = path
        self._load()

    def validate(self, required_keys: List[str]):
        for key in required_keys:
            if self.get_property(key) is None:
                raise KeyError(f"Missing required config key: {key}")