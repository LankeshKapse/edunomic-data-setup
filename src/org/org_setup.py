from typing import Any, Dict

from utils import request_utility
from utils.utilities import get_random_suffix, ConfigLoader
from datetime import date

ENTITY_CONFIG = {
    "trust": ["trustId", "trustName"],
    "university": ["universityId", "universityName"],
    "school": ["schoolId", "schoolName"],
    "program": ["programId", "programName"]
}

def get_address_dict()->dict:
    return {
        "address": get_random_suffix("addr_"),
        "pincode": "4000",
        "country": "INDIA",
        "state": "MAHARASHTRA",
        "city": "PUNE",
        "isActive": True
    }

def get_trust_payload() -> dict:
     trust_payload= {
        "trustRegNo": get_random_suffix("Test_"),
        "trustAbbreviation": get_random_suffix("Test_abr_"),
        "trustName": get_random_suffix("Test_name_"),
        "primaryContactNo": "9876543210"
    }
     trust_payload.update(get_address_dict())
     return trust_payload

def get_university_payload(trust_id:int) -> dict:
    if trust_id is None or trust_id == -1:
        raise ValueError("Trust ID cannot be None : "+trust_id)
    university_payload = {
        "universityName": get_random_suffix("Edunomic_"),
        "abbreviation": get_random_suffix("Test_abr_"),
        "registrationNumber": get_random_suffix("123456_"),
        "primaryContactNumber": "9876543210",
        "trustId": trust_id
    }
    university_payload.update(get_address_dict())
    return university_payload

def get_school_payload(university_id:int) -> dict:
    if university_id is None or university_id == -1:
        raise ValueError("University ID cannot be None : "+university_id)

    school_payload = {
          "schoolName": get_random_suffix("Test_school_"),
          "schoolRegistrationNumber": get_random_suffix("RegistrationNumber_"),
          "schoolAbbreviation": get_random_suffix("Abbr_"),
          "primaryContactNumber": "9876543210",
          "schoolCode": "string",
          "campusCode": "string",
          "universityId": university_id
        }
    school_payload.update(get_address_dict())
    return school_payload

def get_program_payload(school_id:int) -> dict:
    if school_id is None or school_id == -1:
        raise ValueError("School ID cannot be None : "+school_id)
    # Get today's date
    today = date.today()
    # Format as YYYY-MM-DD
    formatted_date = today.strftime("%Y-%m-%d")

    program_payload = {
        "programName": get_random_suffix("MBA"),
        "programCode": get_random_suffix("",4),
        "registrationNumber": get_random_suffix("123456_"),
        "abbreviation": get_random_suffix("abr_",4),
        "streamId": 1,
        "establishmentDate": formatted_date,
        "creditFrameworkId": 1,
        "duration": 2,
        "noOfSemester": 4,
        "programTitle": "PERCENTAGE",
        "programType": "PHD",
        "contactNumber": "9876543210",
        "schoolId": school_id
    }
    program_payload.update(get_address_dict())
    del program_payload["city"]
    return program_payload


if __name__ == "__main__":
    request_utility: request_utility.RequestUtility = request_utility.RequestUtility()
    prop: ConfigLoader  = ConfigLoader()
    org_host: str = prop.get_property("app.outbound.org")
    # Trust
    trust:Dict[str, Any] = request_utility.create_entity(org_host, "/trust",
                                             get_trust_payload(), ENTITY_CONFIG["trust"])
    # University
    university:Dict[str, Any] = request_utility.create_entity(org_host, "/university",
                                                  get_university_payload(trust["trustId"]), ENTITY_CONFIG["university"])

    # School
    school = request_utility.create_entity(org_host, "/school",
                                              get_school_payload(university["universityId"]), ENTITY_CONFIG["school"])

    # Program
    program = request_utility.create_entity(org_host, "/program",
                                               get_program_payload(school["schoolId"]), ENTITY_CONFIG["program"])

    print(f"{program=}")
