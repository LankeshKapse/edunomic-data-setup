import requests
import json
import logging
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestUtility:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def post_func(self, payload: Dict[str, Any], host: str, api_path: str) -> Dict[str, Any]:
        logger.info("Calling POST function {}".format(api_path))
        post_uri = host + api_path
        try:
            response = self.session.post(post_uri, json=payload, timeout=self.timeout)

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
        extractor: List[str],
        default_value: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generic helper to POST an entity and return selected keys from the response.
        """
        res = self.post_func(payload=payload, host=host, api_path=api_path)
        if res["success"]:
            data = res["data"]
            logger.info(f"Entity created: {data}")
            return {k: data.get(k, default_value) for k in extractor}
        else:
            logger.error(f"{res['error']} -> {res['details']} -> Request: {payload=}")
            return {k: default_value for k in extractor}