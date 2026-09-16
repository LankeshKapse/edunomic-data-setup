from google.oauth2 import service_account
import google.auth.transport.requests

class OauthClient:

    def __init__(self, service_file:str):
        if service_file is None:
            raise ValueError("service file can not be none")

        self.service_file = service_file


    def get_token(self) -> str:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        credentials = service_account.Credentials.from_service_account_file(
            self.service_file, scopes=scopes)

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

        return credentials.token


