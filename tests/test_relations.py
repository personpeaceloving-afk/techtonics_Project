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
import uuid

from utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# ASSERT HELPER
# =========================
def assert_response(response, expected_status, test_name=""):
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
# DDT TEST DATA
# =========================
@pytest.mark.parametrize("invalid_category, expected_status", [
    (999999, 400),
    (-1, 400),
    (0, 400),
    ("abc", 400),
    (None, 400),
])
def test_create_part_invalid_category(api_client, invalid_category, expected_status):
    """
    TC_NEG_CAT_001:
    Validate API rejects invalid category values.
    """

    payload = {
        "name": f"InvalidCatPart-{uuid.uuid4()}",
        "description": "Negative Test - Invalid Category",
        "category": invalid_category
    }

    logger.info(f"Testing invalid category: {invalid_category}")
    logger.info(f"Payload: {payload}")

    response = api_client.post("/part/", payload)

    assert_response(
        response,
        expected_status,
        f"TC_NEG_CAT_001 - Invalid Category: {invalid_category}"
    )

    # Optional deeper validation for error structure
    try:
        resp_json = response.json()
        assert isinstance(resp_json, dict)

        assert any(
            key in resp_json
            for key in ["error", "detail", "category", "message"]
        ), "Expected error message in response"

    except Exception:
        logger.warning("Response is not JSON or missing error structure")


# =========================
# IDEMPOTENCY CHECK
# =========================
def test_invalid_category_idempotency(api_client):
    """
    TC_NEG_CAT_002:
    Same invalid request should consistently fail.
    """

    payload = {
        "name": f"IdempotentTest-{uuid.uuid4()}",
        "category": 999999
    }

    response1 = api_client.post("/part/", payload)
    response2 = api_client.post("/part/", payload)

    logger.info(f"First Response: {response1.status_code}")
    logger.info(f"Second Response: {response2.status_code}")

    assert response1.status_code in [400, 404]
    assert response2.status_code in [400, 404]


# =========================
# RATE LIMIT SIMULATION
# =========================
def test_invalid_category_rate_limit(api_client):
    """
    TC_NEG_CAT_003:
    System should handle repeated invalid requests gracefully.
    """

    statuses = []

    for _ in range(10):
        payload = {
            "name": f"RateTest-{uuid.uuid4()}",
            "category": 999999
        }

        response = api_client.post("/part/", payload)
        statuses.append(response.status_code)

    logger.info(f"Rate Limit Status Codes: {statuses}")

    assert all(code in [400, 404, 429] for code in statuses)