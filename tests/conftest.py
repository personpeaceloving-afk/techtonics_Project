"""
Module: conftest.py

Description:
    Pytest configuration file for API test framework.
    Provides reusable fixtures for API client and test data setup.

Design Principles:
    - Centralized test setup
    - Reusable fixtures
    - Logging enabled for debugging CI/CD runs
"""

import pytest
import uuid

from config.settings import BASE_URL, AUTH_TOKEN
from utils.api_client import APIClient
from utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# HEADERS CONFIGURATION
# =========================
HEADERS = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
} if AUTH_TOKEN else {}

logger.info("Test framework initialization started")


# =========================
# API CLIENT FIXTURE
# =========================
@pytest.fixture(scope="session")
def api_client():
    """
    Creates a single API client instance for entire test session.
    """
    logger.info("Creating API client session fixture")

    client = APIClient(BASE_URL, HEADERS)

    logger.info(f"API Client initialized with base URL: {BASE_URL}")

    return client


# =========================
# CATEGORY SETUP FIXTURE
# =========================
@pytest.fixture
def create_category(api_client):
    """
    Creates a test category before test execution.
    Returns category primary key (pk).
    """

    logger.info("Creating test category setup")

    payload = {
        "name": f"Category-{uuid.uuid4()}",
        "description": "Test Category"
    }

    logger.info(f"Category payload: {payload}")

    response = api_client.post("/part/category/", payload)

    logger.info(f"Category creation response status: {response.status_code}")

    try:
        response_data = response.json()
    except Exception as e:
        logger.error(f"Failed to parse category response JSON: {str(e)}")
        pytest.fail("Setup failed: Invalid JSON response")

    if response.status_code not in [200, 201]:
        logger.error(f"Category creation failed: {response.text}")
        pytest.fail(f"Setup failed with status {response.status_code}")

    category_id = response_data.get("pk")

    logger.info(f"Category created successfully with PK: {category_id}")

    return category_id