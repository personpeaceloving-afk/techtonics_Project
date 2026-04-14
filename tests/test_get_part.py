"""
Test Module: test_get_part.py

Description:
    Comprehensive test suite for GET Part APIs from InvenTree.

Coverage:
    - Get all parts
    - Get single part
    - Filtering
    - Pagination
    - Negative scenarios
    - Performance checks
"""

import os
import pytest
import time

from utils.logger import get_logger
from app.validators import validate_list

logger = get_logger(__name__)


# =========================
# CONFIG (better: move to config.py later)
# =========================
BASE_URL = os.getenv("BASE_URL", "https://demo.inventree.org/api")
PART_ENDPOINT = "/part/"

MAX_RESPONSE_TIME = float(os.getenv("MAX_RESPONSE_TIME", "2"))


# =========================
# PYTEST FIXTURE EXPECTED (API CLIENT)
# =========================
@pytest.fixture
def endpoint():
    return PART_ENDPOINT


# =========================
# RESPONSE HELPER
# =========================
def extract_results(response):
    """
    Normalize API response format.
    """
    try:
        data = response.json()
        return data.get("results", data)
    except Exception:
        logger.error("Invalid JSON response")
        return []


# =========================
# ASSERT HELPER
# =========================
def assert_response(response, expected_status, test_name=""):
    """
    Central assertion handler.
    """

    try:
        body = response.json()
    except Exception:
        body = response.text

    if response.status_code != expected_status:
        logger.error("❌ FAILED: %s", test_name)
        logger.error("URL: %s", response.url)
        logger.error("Expected: %s | Got: %s", expected_status, response.status_code)
        logger.error("Response: %s", body)

        pytest.fail(
            f"""
❌ TEST FAILED: {test_name}

➡ URL: {response.url}
➡ Expected: {expected_status}
➡ Got: {response.status_code}

📦 Response:
{body}
            """
        )

    logger.info("✅ PASSED: %s", test_name)


# =========================
# TEST CASES
# =========================

def test_get_all_parts(api_client, endpoint):
    response = api_client.get(endpoint)

    assert_response(response, 200, "TC_001 - Get all parts")

    data = extract_results(response)
    validated = validate_list(data, "parts")

    assert isinstance(validated, list)


def test_get_single_part_valid(api_client, endpoint):
    response = api_client.get(endpoint)

    data = extract_results(response)
    first = data[0]

    part_id = first.get("pk") or first.get("id")

    response = api_client.get(f"{endpoint}{part_id}/")

    assert_response(response, 200, "TC_002 - Get single valid part")

    single = response.json()
    actual_id = single.get("pk") or single.get("id")

    assert actual_id == part_id


@pytest.mark.parametrize("invalid_id", [999999, -1, 0, "abc"])
def test_get_single_part_invalid(api_client, endpoint, invalid_id):
    response = api_client.get(f"{endpoint}{invalid_id}/")

    expected = 400 if isinstance(invalid_id, str) else 404

    assert_response(
        response,
        expected,
        f"TC_003 - Invalid part ID {invalid_id}"
    )


@pytest.mark.parametrize("limit", [1, 5, 10, 50])
def test_part_list_pagination(api_client, endpoint, limit):
    response = api_client.get(endpoint + f"?limit={limit}")

    assert_response(response, 200, f"TC_004 - Pagination limit {limit}")

    data = extract_results(response)
    assert len(data) <= limit


@pytest.mark.parametrize("search_value", ["test", "PART", "abc", "", "@#$%"])
def test_part_filter_by_name(api_client, endpoint, search_value):
    response = api_client.get(endpoint + f"?name={search_value}")

    assert_response(response, 200, f"TC_005 - Filter by name '{search_value}'")

    parts = extract_results(response)

    for part in parts:
        assert search_value.lower() in part.get("name", "").lower()


def test_response_time(api_client, endpoint):
    start = time.time()

    response = api_client.get(endpoint)

    duration = time.time() - start

    assert_response(response, 200, "TC_007 - Response time check")

    assert duration < MAX_RESPONSE_TIME, f"Slow API: {duration}s"


def test_sql_injection_attempt(api_client, endpoint):
    response = api_client.get(endpoint + "?name=' OR '1'='1")

    assert_response(response, 200, "TC_012 - SQL injection safety")


def test_unicode_input(api_client, endpoint):
    response = api_client.get(endpoint + "?name=测试")

    assert_response(response, 200, "TC_013 - Unicode handling")


def test_missing_endpoint(api_client):
    response = api_client.get("/part_invalid/")

    assert_response(response, 404, "TC_014 - Missing endpoint")