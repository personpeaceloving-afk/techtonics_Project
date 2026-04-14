"""
Service Module: category_service.py

Description:
    This module acts as a SERVICE LAYER for Category APIs.
    It abstracts raw API calls and provides reusable business-level methods.

Design Principles:
    - No hardcoded requests in tests
    - Centralized API interaction via APIClient
    - Supports logging, scalability, and maintainability
    - Suitable for enterprise-level automation frameworks
"""

from utils.logger import get_logger

logger = get_logger(__name__)


class CategoryService:
    """
    Service class for handling Category-related API operations.
    """

    def __init__(self, api_client):
        self.api_client = api_client

    # =========================
    # GET ALL CATEGORIES
    # =========================
    def get_categories(self):
        logger.info("Fetching all categories")

        response = self.api_client.get("/part/category/")

        logger.info(f"Status Code: {response.status_code}")

        try:
            data = response.json()
        except Exception:
            logger.error("Failed to parse response JSON")
            return None

        return data

    # =========================
    # GET CATEGORY NAMES ONLY
    # =========================
    def get_category_names(self):
        logger.info("Fetching category names only")

        response = self.get_categories()

        if not response:
            logger.error("No category data received")
            return []

        try:
            return [c["name"] for c in response]
        except Exception:
            logger.error("Error extracting category names from response")
            return []