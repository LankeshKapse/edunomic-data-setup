from typing import Any, Dict, Optional
from utils.payload_factory import PayloadFactory, get_address_dict
from utils.request_utility import RequestUtility
from utils.utilities import ConfigLoader


ENTITY_CONFIG = {
    "trust": ["trustId", "trustName"],
    "university": ["universityId", "universityName"],
    "school": ["schoolId", "schoolName"],
    "program": ["programId", "programName"]
}

def build_payload(payload_factory: PayloadFactory, config_name:str, key_id:Optional[int], key_name:Optional[str]) -> Dict[str, Any]:
    payload:Dict[str, Any] = payload_factory.build(config_name)
    if key_id is not None and key_name is not None:
        payload[key_name] = key_id
    payload.update(get_address_dict())
    return payload

def main() -> None:
    apps_yml_path: str = "../config/application-dev.yml"

    request_utility: RequestUtility = RequestUtility()
    prop: ConfigLoader = ConfigLoader(path=apps_yml_path)
    org_host: str = prop.get_property("app.outbound.org")
    org_setup_config:str=prop.get_list("setup.config","org")

    payload_factory: PayloadFactory = PayloadFactory(org_setup_config)
    # Trust
    trust_payload = build_payload(payload_factory=payload_factory, config_name="trust",
                                  key_id=None, key_name=None)
    trust: Dict[str, Any] = request_utility.create_entity(org_host, "/trust", trust_payload, ENTITY_CONFIG["trust"])
    # University
    university_payload = build_payload(payload_factory=payload_factory, config_name="university",
                                       key_id=trust["trustId"], key_name="trustId")
    university: Dict[str, Any] = request_utility.create_entity(org_host, "/university", university_payload,
                                                               ENTITY_CONFIG["university"])

    # School
    school_payload = build_payload(payload_factory=payload_factory, config_name="school",
                                   key_id=university["universityId"], key_name="universityId")
    school = request_utility.create_entity(org_host, "/school", school_payload, ENTITY_CONFIG["school"])

    # Program
    program_payload = build_payload(payload_factory=payload_factory, config_name="program",
                                    key_id=school["schoolId"], key_name="schoolId")
    del program_payload["city"]
    program = request_utility.create_entity(org_host, "/program", program_payload, ENTITY_CONFIG["program"])

    print(f"{program=}")
if __name__ == "__main__":
    main()