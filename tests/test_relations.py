"""
Test Case: Invalid Category While Creating Part
Description:
    Validate API behavior when invalid / edge category IDs are used
    during part creation.

Coverage:
    - Negative scenarios
    - Boundary values
    - Parameterized inputs (DDT)
    - Logging
    - Strong assertions
"""

import pytest
import requests
import logging
import uuid

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================
# TEST DATA (DDT)
# =========================
@pytest.mark.parametrize("invalid_category, expected_status", [
    (999999, 400),     # non-existent category
    (-1, 400),         # negative ID
    (0, 400),          # boundary (invalid ID)
    ("abc", 400),      # wrong data type
    (None, 400),       # null value
])
def test_create_part_invalid_category(base_url, headers, invalid_category, expected_status):
    """
    TC_NEG_CAT_001:
    Verify API response when invalid category is provided

    Steps:
        1. Send POST request with invalid category
        2. Capture response

    Expected:
        - API should reject request
        - Return 400/404
        - Proper error message in response
    """

    # =========================
    # TEST DATA
    # =========================
    payload = {
        "name": f"InvalidCatPart-{uuid.uuid4()}",
        "description": "Negative Test - Invalid Category",
        "category": invalid_category
    }

    url = f"{base_url}/part/"

    logger.info(f"Testing invalid category: {invalid_category}")
    logger.info(f"Request Payload: {payload}")

    # =========================
    # API CALL
    # =========================
    response = requests.post(url, json=payload, headers=headers)

    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Body: {response.text}")

    # =========================
    # ASSERTIONS
    # =========================
    assert response.status_code in [400, 404], \
        f"Expected failure for invalid category, got {response.status_code}"

    # Validate error structure (if JSON)
    try:
        resp_json = response.json()

        assert isinstance(resp_json, dict), "Error response should be JSON object"

        # Optional: check error message exists
        assert any(key in resp_json for key in ["error", "category", "detail"]), \
            "Expected error message in response"

    except ValueError:
        pytest.fail("Response is not valid JSON")


# =========================
# IDEMPOTENCY CHECK (OPTIONAL)
# =========================
def test_invalid_category_idempotency(base_url, headers):
    """
    TC_NEG_CAT_002:
    Same invalid request should consistently fail
    """

    payload = {
        "name": f"IdempotentTest-{uuid.uuid4()}",
        "category": 999999
    }

    url = f"{base_url}/part/"

    response1 = requests.post(url, json=payload, headers=headers)
    response2 = requests.post(url, json=payload, headers=headers)

    logger.info(f"First Response: {response1.status_code}")
    logger.info(f"Second Response: {response2.status_code}")

    assert response1.status_code in [400, 404]
    assert response2.status_code in [400, 404]


# =========================
# RATE LIMIT SIMULATION
# =========================
def test_invalid_category_rate_limit(base_url, headers):
    """
    TC_NEG_CAT_003:
    Rapid invalid requests should not crash system
    """

    url = f"{base_url}/part/"
    statuses = []

    for _ in range(10):
        payload = {
            "name": f"RateTest-{uuid.uuid4()}",
            "category": 999999
        }

        response = requests.post(url, json=payload, headers=headers)
        statuses.append(response.status_code)

    logger.info(f"Rate Limit Status Codes: {statuses}")

    assert all(code in [400, 404, 429] for code in statuses)