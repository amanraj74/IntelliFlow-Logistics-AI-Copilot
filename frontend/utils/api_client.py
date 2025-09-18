import requests
from typing import Any, Dict, List, Optional

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_health(self) -> Dict[str, str]:
        return self._make_request("GET", "/health")

    def list_drivers(self) -> List[Dict[str, Any]]:
        return self._make_request("GET", "/drivers/")

    def get_driver(self, driver_id: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/drivers/{driver_id}")

    def list_incidents(self) -> List[Dict[str, Any]]:
        return self._make_request("GET", "/incidents/")

    def list_alerts(self) -> List[Dict[str, Any]]:
        return self._make_request("GET", "/alerts/")

    def query_ai(self, question: str) -> Dict[str, Any]:
        return self._make_request("POST", "/ai/query", json={"question": question})
