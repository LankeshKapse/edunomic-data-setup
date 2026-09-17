import requests
import json
import logging
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def response_extractor(data: Dict[str, Any], extractor: List[str] | None = None, default_value: Any = None) -> Dict[str, Any]:
    if extractor is None:
        return data
    else:
        return {k: data.get(k, default_value) for k in extractor}


class RequestUtility:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def post_func(self, payload: Dict[str, Any], host: str, api_path: str,
                  token: str,
                  tokentype: str
                 ) -> Dict[str, Any]:

        logger.info("Calling POST function {}".format(api_path))
        post_uri = host + api_path
        try:
            headers: dict[str,str] = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "tokentype": tokentype
            }
            response = self.session.post(post_uri, json=payload, headers=headers, timeout=self.timeout)

            if not response.ok:
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

    def create_entity(
        self,
        host: str,
        api_path: str,
        payload: Dict[str, Any],
        extractor: List[str] | None = None,
        default_value: Optional[str] = None,
        token: str | None =None,
        tokentype: str | None =None
    ) -> Dict[str, Any]:
        """
        Generic helper to POST an entity and return selected keys from the response.
        """
        res = self.post_func(payload=payload,
                             host=host,
                             api_path=api_path,
                             token=token,
                             tokentype=tokentype
                        )
        if res["success"]:
            data = res["data"]
            logger.info(f"Entity created: {data}")
            return response_extractor(data=data, extractor=extractor, default_value=default_value)
        else:
            logger.error(f"{res['error']} -> {res['details']} -> Request: {payload=}")
            if extractor is not None:
                return {k: default_value for k in extractor}
            else:
                return res