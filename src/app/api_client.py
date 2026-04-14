"""
Module: api_client.py

Description:
    Centralized HTTP client wrapper for API requests.
    Provides reusable methods with logging, timeouts, and error handling.
"""

import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    """
    Wrapper around requests library for API operations.
    """

    def __init__(self, base_url: str, headers: dict = None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"GET {url}")

        try:
            response = self.session.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )
            logger.info(f"Status Code: {response.status_code}")
            return response

        except requests.RequestException as e:
            logger.error(f"GET request failed: {str(e)}")
            raise

    def post(self, endpoint: str, payload: dict):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"POST {url} | Payload: {payload}")

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            logger.info(f"Status Code: {response.status_code}")
            return response

        except requests.RequestException as e:
            logger.error(f"POST request failed: {str(e)}")
            raise

    def patch(self, endpoint: str, payload: dict):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"PATCH {url}")

        return self.session.patch(url, json=payload, headers=self.headers)

    def delete(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"DELETE {url}")

        return self.session.delete(url, headers=self.headers)