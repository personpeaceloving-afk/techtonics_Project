"""
Test Module: test_part_validation.py

Description:
    Negative validation test suite for Part API.

Coverage:
    - Field validation (name)
    - Boundary conditions
    - Data type validation
    - Idempotency checks
    - Rate limiting simulation
"""

import pytest
import uuid

from utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# ASSERT HELPER
# =========================
def assert_response(response, expected_status, scenario=""):
    try:
        body = response.json()
    except Exception:
        body = response.text

    if response.status_code != expected_status:
        logger.error("❌ FAILED: %s", scenario)
        logger.error("URL: %s", response.url)
        logger.error("Expected: %s | Got: %s", expected_status, response.status_code)
        logger.error("Response: %s", body)

        pytest.fail(
            f"""
❌ TEST FAILED: {scenario}

➡ URL: {response.url}
➡ Expected: {expected_status}
➡ Got: {response.status_code}

📦 Response:
{body}
            """
        )

    logger.info("✅ PASSED: %s", scenario)


# =========================
# TEST DATA (DDT)
# =========================
@pytest.mark.parametrize("payload, expected_status, scenario", [
    ({"description": "No name"}, 400, "Missing name"),
    ({"name": 123}, 400, "Name as integer"),
    ({"name": ""}, 400, "Empty string"),
    ({"name": "A" * 300}, 400, "Exceeds max length"),
    ({"name": None}, 400, "Null name"),
])
def test_part_validation_negative(api_client, payload, expected_status, scenario):
    """
    TC_VAL_001:
    Validate API rejects invalid 'name' field inputs.
    """

    url = "/part/"

    # Add uniqueness if applicable
    if isinstance(payload.get("name"), str) and payload["name"]:
        payload["name"] = f"{payload['name']}-{uuid.uuid4()}"

    logger.info(f"Scenario: {scenario}")
    logger.info(f"Payload: {payload}")

    response = api_client.post(url, payload)

    assert_response(response, expected_status, scenario)

    # Optional response structure validation
    try:
        resp_json = response.json()
        assert isinstance(resp_json, dict)

        assert any(
            key in resp_json
            for key in ["name", "error", "detail", "message"]
        ), "Expected validation error message"

    except Exception:
        logger.warning("Response is not JSON or missing expected error structure")


# =========================
# IDEMPOTENCY TEST
# =========================
def test_missing_name_idempotency(api_client):
    """
    TC_VAL_002:
    Repeated invalid requests should consistently fail.
    """

    payload = {"description": "No name"}
    url = "/part/"

    response1 = api_client.post(url, payload)
    response2 = api_client.post(url, payload)

    logger.info("First Response: %s", response1.status_code)
    logger.info("Second Response: %s", response2.status_code)

    assert response1.status_code == 400
    assert response2.status_code == 400


# =========================
# RATE LIMIT SIMULATION
# =========================
def test_validation_rate_limit(api_client):
    """
    TC_VAL_003:
    System should handle repeated invalid payloads safely.
    """

    url = "/part/"
    statuses = []

    for i in range(10):
        payload = {"name": 123}

        response = api_client.post(url, payload)

        logger.info("Iteration %s | Status: %s", i + 1, response.status_code)

        statuses.append(response.status_code)

    assert all(code in [400, 429] for code in statuses)