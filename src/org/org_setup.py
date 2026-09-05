from typing import Any, Dict

from utils.payload_factory import PayloadFactory
from utils.request_utility import RequestUtility
from utils.utilities import get_random_suffix, ConfigLoader, get_today_date

ENTITY_CONFIG = {
    "trust": ["trustId", "trustName"],
    "university": ["universityId", "universityName"],
    "school": ["schoolId", "schoolName"],
    "program": ["programId", "programName"]
}

def get_address_dict()->dict:
    return {
        "pincode": "4000",
        "country": "INDIA",
        "state": "MAHARASHTRA",
        "city": "PUNE"
    }

def get_trust_payload(payload_factory: PayloadFactory) -> Dict[str, Any]:
     trust_payload= payload_factory.build("trust")
     trust_payload.update(get_address_dict())
     return trust_payload

def get_university_payload(payload_factory: PayloadFactory,trust_id:int) -> Dict[str, Any]:
    if trust_id is None or trust_id == -1:
        raise ValueError("Trust ID cannot be None : "+trust_id)
    university_payload = payload_factory.build("university")
    university_payload["trustId"] = trust_id
    university_payload.update(get_address_dict())
    return university_payload

def get_school_payload(payload_factory: PayloadFactory,university_id:int) -> Dict[str, Any]:
    if university_id is None or university_id == -1:
        raise ValueError("University ID cannot be None : "+university_id)
    school_payload = payload_factory.build("school")
    school_payload["universityId"] = university_id
    school_payload.update(get_address_dict())
    return school_payload

def get_program_payload(payload_factory: PayloadFactory, school_id:int) -> Dict[str, Any]:
    if school_id is None or school_id == -1:
        raise ValueError("School ID cannot be None : "+school_id)

    program_payload = payload_factory.build("program")
    program_payload["schoolId"] = school_id
    program_payload.update(get_address_dict())
    del program_payload["city"]
    return program_payload


if __name__ == "__main__":
    request_utility: RequestUtility = RequestUtility()
    prop: ConfigLoader  = ConfigLoader()
    org_host: str = prop.get_property("app.outbound.org")

    payload_factory: PayloadFactory = PayloadFactory("../../config/org_setup_config.yml")
    # Trust
    trust:Dict[str, Any] = request_utility.create_entity(org_host, "/trust",
                                             get_trust_payload(payload_factory), ENTITY_CONFIG["trust"])
    # University
    university:Dict[str, Any] = request_utility.create_entity(org_host, "/university",
                                                  get_university_payload(payload_factory,trust["trustId"]), ENTITY_CONFIG["university"])

    # School
    school = request_utility.create_entity(org_host, "/school",
                                              get_school_payload(payload_factory,university["universityId"]), ENTITY_CONFIG["school"])

    # Program
    program = request_utility.create_entity(org_host, "/program",
                                               get_program_payload(payload_factory,school["schoolId"]), ENTITY_CONFIG["program"])

    print(f"{program=}")
