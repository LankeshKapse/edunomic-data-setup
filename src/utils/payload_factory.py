import string
import random
from datetime import date
from typing import Dict, Any, Callable, Optional
from faker import Faker
import yaml

fake = Faker("en_IN")

def get_random_suffix(prefix: str, length: int = 8) -> str:
    return prefix + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_today_date(date_format:str= "%Y-%m-%d") -> str:
    # Get today's date
    today = date.today()
    # Format as YYYY-MM-DD
    return today.strftime(date_format)


# Dispatch table for simple faker rules
RULE_HANDLERS: Dict[str, Callable[[], Any]] = {
    "faker.name": fake.name,
    "faker.address": fake.address,
    "faker.phone": lambda: "+91"+''.join(random.choices(string.digits, k=10)),
    "faker.email": fake.email,
    "faker.company": fake.company,
}

def get_address_dict() -> dict:
    return {
        "pincode": str(random.randint(100000, 999999)),   # 6-digit realistic PIN code
        "state": fake.state(),                            # random Indian state
        "city": fake.city_name()                          # random Indian city
    }

def apply_rule(rule: str) -> Any:
    """Apply a rule string to generate a value, supporting parameters."""
    if rule.startswith("random_suffix:"):
        # Format: random_suffix:PREFIX:LENGTH
        parts = rule.split(":")
        prefix = parts[1]
        length = int(parts[2]) if len(parts) > 2 else 8
        return get_random_suffix(prefix, length)

    elif rule.startswith("faker.text"):
        # Format: faker.text:MAXLEN
        parts = rule.split(":")
        max_len = int(parts[1]) if len(parts) > 1 else 100
        return fake.text(max_nb_chars=max_len)

    elif rule.startswith("today_date:"):
        parts = rule.split(":")
        if len(parts)>1 and parts[1] :
            return get_today_date(parts[1])
        else:
            return get_today_date()

    elif rule in RULE_HANDLERS:
        return RULE_HANDLERS[rule]()

    else:
        # literal value
        return rule

def build_payload(template: Dict[str, str]) -> Dict[str, Any]:
    return {key: apply_rule(rule) for key, rule in template.items()}

class PayloadFactory:
    def __init__(self, config_path: str = "../../payload_templates.yml"):
        self.config_path = config_path
        self._load()

    def _load(self):
        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f) or {}
            if not isinstance(config, dict):
                raise RuntimeError("Config must be a dictionary of templates")
            self.config: Dict[str, Dict[str, Any]] = config
        except FileNotFoundError:
            raise RuntimeError(f"Config file not found: {self.config_path}")

    def get_template(self, key: str) -> Optional[Dict[str, Any]]:
        value = self.config.get(key)
        return value if isinstance(value, dict) else None

    def build(self, key: str) -> Dict[str, Any]:
        """Build payload directly from a named template."""
        template = self.get_template(key)
        if not template:
            raise ValueError(f"No template found for {key}")
        return build_payload(template)
