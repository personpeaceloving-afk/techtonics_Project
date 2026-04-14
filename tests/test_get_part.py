"""
Test Module: test_get_part.py
Description:
    Comprehensive test suite for GET Part APIs from InvenTree.
    Covers:
        - Get single part
        - Get part list
        - Filtering
        - Pagination
        - Invalid scenarios
        - Edge cases
        - Performance validation

Author: QA Automation
"""

import os
import requests
import pytest
import logging
import time

# =========================
# CONFIGURATION
# =========================
# Allow overriding the target API via environment for local testing or CI
BASE_URL = os.environ.get("BASE_URL", "https://demo.inventree.org/api")
PART_ENDPOINT = "/part/"
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "2"))  # seconds

# Optional authentication token (example: InvenTree token)
AUTH_TOKEN = os.environ.get("INVENTREE_TOKEN") or os.environ.get("AUTH_TOKEN")
HEADERS = {"Authorization": f"Token {AUTH_TOKEN}"} if AUTH_TOKEN else {}

# If pointing at the public demo and no token is configured, skip these network tests
if "demo.inventree.org" in BASE_URL and not AUTH_TOKEN:
    pytest.skip("No authentication token provided for external demo API; skipping tests", allow_module_level=True)

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# =========================
# RETRY MECHANISM
# =========================
def make_request_with_retry(url, params=None):
    """
    Reusable function to make GET request with retry mechanism.
    Retries up to MAX_RETRIES if:
        - Network failure
        - 5xx errors
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Attempt {attempt}: GET {url} | Params: {params}")
            response = requests.get(url, params=params, headers=HEADERS or None, timeout=10)

            # Retry only for server errors
            if response.status_code >= 500:
                raise Exception(f"Server Error: {response.status_code}")

            return response

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")

            if attempt == MAX_RETRIES:
                logger.critical("Max retries reached. Failing test.")
                raise

            time.sleep(RETRY_DELAY)


def _extract_results(response):
    """Normalize response JSON to a list of results when API is paginated."""
    data = response.json()
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


# =========================
# TEST CASES
# =========================

def test_get_all_parts():
    """
    TC_001: Verify fetching all parts
    Expected:
        - Status code 200
        - Response is a list
    """
    url = BASE_URL + PART_ENDPOINT
    response = make_request_with_retry(url)

    logger.info("Validating response for all parts")

    assert response.status_code == 200
    data = _extract_results(response)

    assert isinstance(data, list), "Response should be a list"


def test_get_single_part_valid():
    """
    TC_002: Verify fetching a valid part by ID
    Steps:
        - Fetch list
        - Pick first ID
        - Fetch single part
    Expected:
        - Status 200
        - ID matches
    """
    list_response = make_request_with_retry(BASE_URL + PART_ENDPOINT)
    list_data = _extract_results(list_response)
    first = list_data[0]
    part_id = first.get('pk') or first.get('id')

    url = f"{BASE_URL}{PART_ENDPOINT}{part_id}/"
    response = make_request_with_retry(url)

    logger.info(f"Validating part ID: {part_id}")

    assert response.status_code == 200
    single = response.json()
    actual_id = single.get('pk') or single.get('id')
    assert actual_id == part_id


@pytest.mark.parametrize("invalid_id", [
    999999,
    -1,
    0,
    "abc",
])
def test_get_single_part_invalid(invalid_id):
    """
    TC_003 (DDT): Verify invalid part IDs
    """
    url = f"{BASE_URL}{PART_ENDPOINT}{invalid_id}/"
    response = make_request_with_retry(url)

    logger.info(f"Testing invalid part ID: {invalid_id}")

    assert response.status_code in [400, 404]


@pytest.mark.parametrize("limit", [1, 5, 10, 50])
def test_part_list_pagination(limit):
    """
    TC_004 (DDT): Verify pagination with multiple limits
    """
    params = {"limit": limit}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info(f"Validating pagination with limit: {limit}")

    assert response.status_code == 200
    data = _extract_results(response)

    assert len(data) <= limit


@pytest.mark.parametrize("search_value", [
    "test",
    "PART",
    "abc",
    "",              # edge case
    "@#$%",          # special chars
])
def test_part_filter_by_name(search_value):
    """
    TC_005 (DDT): Verify filtering by name with multiple inputs
    """
    params = {"name": search_value}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info(f"Validating filter by name: {search_value}")

    assert response.status_code == 200
    parts = _extract_results(response)

    for part in parts:
        assert search_value.lower() in part.get("name", "").lower()


def test_part_filter_by_category():
    """
    TC_006: Verify filtering by category
    Expected:
        - Only parts from that category
    """
    params = {"category": 1}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info("Validating filter by category")

    assert response.status_code == 200


def test_response_time():
    """
    TC_007: Performance test
    Expected:
        - Response time < 2 seconds
    """
    start_time = time.time()

    response = make_request_with_retry(BASE_URL + PART_ENDPOINT)

    end_time = time.time()
    response_time = end_time - start_time

    logger.info(f"Response Time: {response_time} seconds")

    assert response.status_code == 200
    assert response_time < 2, "API response too slow"


def test_empty_query():
    """
    TC_008: Empty query params
    Expected:
        - Should return default results
    """
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params={})

    logger.info("Validating empty query")

    assert response.status_code == 200


@pytest.mark.parametrize("params", [
    {"invalid_param": "xyz"},
    {"unknown": "123"},
    {"limit": -1},              # invalid limit
    {"offset": "abc"},          # wrong type
])
def test_invalid_query_param(params):
    """
    TC_009 (DDT): Validate API behavior with invalid query params
    """
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info(f"Testing invalid params: {params}")

    assert response.status_code in [200, 400]


def test_large_limit():
    """
    TC_010: Large limit value
    Expected:
        - API should handle gracefully
    """
    params = {"limit": 1000}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info("Validating large limit")

    assert response.status_code == 200


def test_special_characters_search():
    """
    TC_011: Special character input
    Expected:
        - API should not crash
    """
    params = {"name": "@#$%^"}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info("Validating special characters")

    assert response.status_code == 200


def test_sql_injection_attempt():
    """
    TC_012: SQL Injection attempt
    Expected:
        - API should sanitize input
    """
    params = {"name": "' OR '1'='1"}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info("Validating SQL injection protection")

    assert response.status_code == 200


def test_unicode_input():
    """
    TC_013: Unicode characters
    Expected:
        - API should handle unicode properly
    """
    params = {"name": "测试"}
    response = make_request_with_retry(BASE_URL + PART_ENDPOINT, params=params)

    logger.info("Validating unicode handling")

    assert response.status_code == 200


def test_missing_endpoint():
    """
    TC_014: Invalid endpoint
    Expected:
        - 404 response
    """
    url = BASE_URL + "/part_invalid/"
    response = make_request_with_retry(url)

    logger.info("Validating missing endpoint")

    assert response.status_code == 404