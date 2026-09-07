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

MASTER_URI_CONFIG = {
    "designation": "/designation",
    # "role": "/roles",
    "quota": "/quota",
    "category": "/category",
    "document": "/document",
    "credit-framework": "/credit-framework",
}

MASTER_EXTRACT_CONFIG = {
    "designation": ["designationId","designationName"],
    # "role": ["roleId","roleName"],
    "quota": ["quotaId","quotaName"],
    "document": ["documentId","documentName"],
    "category": ["categoryId","categoryName"],
    "credit-framework": ["creditFrameworkId","qualificationTitle"],
}

def build_payload(payload_factory: PayloadFactory,
                  config_name:str,
                  key_id:Optional[int],
                  key_name:Optional[str],
                  include_address: bool = False
                  ) -> Dict[str, Any]:
    payload:Dict[str, Any] = payload_factory.build(config_name)
    if key_id is not None and key_name is not None:
        payload[key_name] = key_id

    if include_address:
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
                                  key_id=None, key_name=None, include_address=True)
    trust: Dict[str, Any] = request_utility.create_entity(org_host, "/trust", trust_payload, ENTITY_CONFIG["trust"])
    # University
    university_payload = build_payload(payload_factory=payload_factory, config_name="university",
                                       key_id=trust["trustId"], key_name="trustId", include_address=True)
    university: Dict[str, Any] = request_utility.create_entity(org_host, "/university", university_payload,
                                                               ENTITY_CONFIG["university"])

    # School
    school_payload = build_payload(payload_factory=payload_factory, config_name="school",
                                   key_id=university["universityId"], key_name="universityId", include_address=True)
    school = request_utility.create_entity(org_host, "/school", school_payload, ENTITY_CONFIG["school"])

    # Program
    program_payload = build_payload(payload_factory=payload_factory, config_name="program",
                                    key_id=school["schoolId"], key_name="schoolId", include_address=True)
    del program_payload["city"]
    program = request_utility.create_entity(org_host, "/program", program_payload, ENTITY_CONFIG["program"])

    master_config = prop.get_list("setup.config","master")
    master_host: str = prop.get_property("app.outbound.master")
    master_payload_factory: PayloadFactory = PayloadFactory(master_config)
    for master_uri_config in MASTER_URI_CONFIG.items():
        payload = build_payload(payload_factory=master_payload_factory, config_name=master_uri_config[0],
                                key_id=None,
                                key_name=None)
        request_utility.create_entity(master_host, master_uri_config[1], payload, MASTER_EXTRACT_CONFIG[master_uri_config[0]])


if __name__ == "__main__":
    main()