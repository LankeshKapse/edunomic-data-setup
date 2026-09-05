import json
import requests

def create_app_form(json_file:str):
    with open(json_file,"r") as f:
        json_data = json.load(f)

    url = "http://localhost:8084/admission/config/applicationForm"
    response = requests.post(url,json=json_data)
    if response.status_code == 200:
        print("Application form created")
    else:
        print("Application form not created")
        print(response.text)
