"""
Service Module: part_service.py

Description:
    This module acts as a SERVICE LAYER for Part APIs.
    It abstracts raw API calls and provides reusable business-level methods.

Design Principles:
    - No hardcoded requests in tests
    - Centralized API interaction via APIClient
    - Supports logging, scalability, and maintainability
    - Suitable for enterprise-level automation frameworks
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class PartService:
    """
    Service class for handling Part-related API operations.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    # =========================
    # GET ALL PARTS
    # =========================
    def get_parts(self):
        logger.info("Fetching all parts")

        response = self.api_client.get("/part/")

        logger.info(f"Status Code: {response.status_code}")

        try:
            data = response.json()
        except Exception:
            logger.error("Failed to parse response JSON")
            return None

        return data

    # =========================
    # CREATE PART
    # =========================
    def create_part(self, name, description=""):
        logger.info(f"Creating part: {name}")

        payload = {
            "name": name,
            "description": description,
            "active": True
        }

        response = self.api_client.post("/part/", payload)

        logger.info(f"Status Code: {response.status_code}")

        try:
            data = response.json()
        except Exception:
            logger.error("Invalid JSON response while creating part")
            return None

        return data