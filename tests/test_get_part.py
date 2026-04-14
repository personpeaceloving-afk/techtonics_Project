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
import requests
import pytest
import logging
import time

# =========================
# CONFIG
# =========================
BASE_URL = os.environ.get("BASE_URL", "https://demo.inventree.org/api")
PART_ENDPOINT = "/part/"

MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "2"))

AUTH_TOKEN = os.environ.get("INVENTREE_TOKEN") or os.environ.get("AUTH_TOKEN")
HEADERS = {"Authorization": f"Token {AUTH_TOKEN}"} if AUTH_TOKEN else {}


# =========================
# LOGGER
# =========================
logger = logging.getLogger(__name__)


# =========================
# SKIP SAFELY (FIXED)
# =========================
def pytest_configure():
    """
    Skip only at runtime, NOT import time (important fix).
    """
    if "demo.inventree.org" in BASE_URL and not AUTH_TOKEN:
        pytest.skip(
            "No auth token provided for demo API. Skipping tests.",
            allow_module_level=True
        )


# =========================
# RETRY LOGIC
# =========================
def make_request_with_retry(url, params=None):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("Attempt %s: GET %s | Params: %s", attempt, url, params)

            response = requests.get(
                url,
                params=params,
                headers=HEADERS or None,
                timeout=10
            )

            if response.status_code >= 500:
                raise Exception(f"Server Error: {response.status_code}")

            return response

        except Exception as e:
            logger.error("Attempt %s failed: %s", attempt, str(e))

            if attempt == MAX_RETRIES:
                raise

            time.sleep(RETRY_DELAY)


# =========================
# RESPONSE NORMALIZER
# =========================
def _extract_results(response):
    try:
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data
    except Exception:
        return response.text


# =========================
# ASSERT HELPER (IMPORTANT)
# =========================
def assert_response(response, expected_status, test_name=""):
    """
    Central assertion with full debug output.
    """

    try:
        body = response.json()
    except Exception:
        body = response.text

    if response.status_code != expected_status:

        logger.error("\n❌ FAILED: %s", test_name)
        logger.error("URL: %s", response.url)
        logger.error("Expected: %s | Got: %s", expected_status, response.status_code)
        logger.error("Response Body:\n%s", body)

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

def test_get_all_parts():
    url = BASE_URL + PART_ENDPOINT
    response = make_request_with_retry(url)

    assert_response(response, 200, "TC_001 - Get all parts")

    data = _extract_results(response)
    assert isinstance(data, list)


def test_get_single_part_valid():
    list_response = make_request_with_retry(BASE_URL + PART_ENDPOINT)
    list_data = _extract_results(list_response)

    first = list_data[0]
    part_id = first.get("pk") or first.get("id")

    url = f"{BASE_URL}{PART_ENDPOINT}{part_id}/"
    response = make_request_with_retry(url)

    assert_response(response, 200, "TC_002 - Get single valid part")

    single = response.json()
    actual_id = single.get("pk") or single.get("id")

    assert actual_id == part_id


@pytest.mark.parametrize("invalid_id", [999999, -1, 0, "abc"])
def test_get_single_part_invalid(invalid_id):
    url = f"{BASE_URL}{PART_ENDPOINT}{invalid_id}/"
    response = make_request_with_retry(url)

    assert_response(response, 400 if isinstance(invalid_id, str) else 404,
                    f"TC_003 - Invalid part ID {invalid_id}")


@pytest.mark.parametrize("limit", [1, 5, 10, 50])
def test_part_list_pagination(limit):
    response = make_request_with_retry(
        BASE_URL + PART_ENDPOINT,
        params={"limit": limit}
    )

    assert_response(response, 200, f"TC_004 - Pagination limit {limit}")

    data = _extract_results(response)
    assert len(data) <= limit


@pytest.mark.parametrize("search_value", ["test", "PART", "abc", "", "@#$%"])
def test_part_filter_by_name(search_value):
    response = make_request_with_retry(
        BASE_URL + PART_ENDPOINT,
        params={"name": search_value}
    )

    assert_response(response, 200, f"TC_005 - Filter by name '{search_value}'")

    parts = _extract_results(response)

    for part in parts:
        assert search_value.lower() in part.get("name", "").lower()


def test_response_time():
    start = time.time()

    response = make_request_with_retry(BASE_URL + PART_ENDPOINT)

    duration = time.time() - start

    assert_response(response, 200, "TC_007 - Response time check")

    assert duration < 2, f"Slow API: {duration}s"


def test_sql_injection_attempt():
    response = make_request_with_retry(
        BASE_URL + PART_ENDPOINT,
        params={"name": "' OR '1'='1"}
    )

    assert_response(response, 200, "TC_012 - SQL injection safety")


def test_unicode_input():
    response = make_request_with_retry(
        BASE_URL + PART_ENDPOINT,
        params={"name": "测试"}
    )

    assert_response(response, 200, "TC_013 - Unicode handling")


def test_missing_endpoint():
    response = make_request_with_retry(BASE_URL + "/part_invalid/")

    assert_response(response, 404, "TC_014 - Missing endpoint")