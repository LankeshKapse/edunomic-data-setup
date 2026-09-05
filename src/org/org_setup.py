from utils.utilities import get_random_suffix, ConfigLoader
import requests
import json


def post_func(payload:dict, host: str, api_path:str) -> dict:
    print("calling post function")
    post_uri = host + api_path
    try:
        response = requests.post(post_uri, json=payload, timeout=10)

        # Accept only 2xx responses
        if not response.ok or response.status_code < 200 or response.status_code >= 300:
            return {
                "success": False,
                "error": f"Unexpected status {response.status_code}",
                "details": response.text
            }

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response",
                "details": response.text
            }

        return {"success": True, "data": response_data}

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": "Network error",
            "details": str(e)
        }


if __name__ == "__main__":

    prop: ConfigLoader  = ConfigLoader()
    org_host: str = prop.get_property("app.outbound.org")
    trust_payload:dict = {
            "trustRegNo": get_random_suffix("Test_"),
            "trustAbbreviation": get_random_suffix("Test_abr_"),
            "trustName": get_random_suffix("Test_name_"),
            "address": "Test_address",
            "pincode": "4000",
            "country": "Test_country",
            "state": "Test_State",
            "city": "Test_City",
            "primaryContactNo": "9876543210",
            "isActive": True
        }
    trust_id: int=-1
    trust_res: dict = post_func(payload=trust_payload, host=org_host, api_path="/trust")
    if trust_res["success"]:
        response_dict:dict =  trust_res["data"]
        trust_id = response_dict.get("trustId",-1)
    else:
        print(f"{trust_res["error"]} -> {trust_res['details']} -> Request: {trust_payload=}")


    university_payload:dict = {
              "universityName":  get_random_suffix("Edunomic_"),
              "abbreviation":  get_random_suffix("Test_abr_"),
              "registrationNumber": get_random_suffix("123456_"),
              "address":  get_random_suffix("addr_"),
              "pincode": "4000",
              "country": "INDIA",
              "state": "MH",
              "city": "PN",
              "primaryContactNumber": "9876543210",
              "isActive": True,
              "trustId": trust_id
    }

    university_id: int = -1
    university_res: dict = post_func(payload=university_payload, host=org_host, api_path="/university")
    if university_res["success"]:
        university_res_data: dict = university_res["data"]
        print(university_res_data)
        university_id = university_res_data.get("universityId", -1)
    else:
        print(f"{university_res["error"]} -> {university_res['details']} -> Request: {university_payload=}")



