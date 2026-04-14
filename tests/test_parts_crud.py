"""
Test Module: test_part_crud.py

Description:
    CRUD Test Suite for Part APIs (InvenTree)

Coverage:
    - POST (Create Part)
    - PUT (Full Update)
    - PATCH (Partial Update)
    - DELETE
    - Positive / Negative / Boundary
    - Idempotency
    - Rate limiting simulation
"""

import os
import pytest
import uuid

from utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# CONFIG
# =========================
BASE_URL = os.getenv("BASE_URL", "https://demo.inventree.org/api")
PART_ENDPOINT = "/part/"


# =========================
# FIXTURE: CREATE PART
# =========================
@pytest.fixture
def create_part(api_client):
    """
    Creates a test part and returns its ID.
    """

    payload = {
        "name": f"AutoPart-{uuid.uuid4()}",
        "description": "Test Part",
        "active": True
    }

    response = api_client.post(PART_ENDPOINT, payload)

    assert response.status_code in [200, 201], "Failed to create part in fixture"

    data = response.json()

    part_id = data.get("pk") or data.get("id")

    logger.info(f"Created part with ID: {part_id}")

    return part_id


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
# POST - CREATE PART
# =========================
@pytest.mark.parametrize("payload, expected_status", [
    ({"name": f"ValidPart-{uuid.uuid4()}"}, 201),
    ({}, 400),
    ({"name": ""}, 400),
])
def test_create_part(api_client, payload, expected_status):
    logger.info(f"Creating part: {payload}")

    response = api_client.post(PART_ENDPOINT, payload)

    assert_response(
        response,
        expected_status,
        f"TC_CRUD_001 - Create Part {payload}"
    )


# =========================
# PUT - FULL UPDATE
# =========================
def test_put_update_part(api_client, create_part):
    payload = {
        "name": f"Updated-{uuid.uuid4()}",
        "description": "Updated Desc",
        "active": False
    }

    url = f"{PART_ENDPOINT}{create_part}/"
    response = api_client.api_client.put(url, json=payload, headers=api_client.headers)

    assert_response(response, 200, "TC_CRUD_002 - PUT Update Part")

    assert response.json()["name"] == payload["name"]


# =========================
# PATCH - PARTIAL UPDATE
# =========================
def test_patch_update_part(api_client, create_part):
    payload = {"description": "Patched Desc"}

    url = f"{PART_ENDPOINT}{create_part}/"
    response = api_client.api_client.patch(url, json=payload, headers=api_client.headers)

    assert_response(response, 200, "TC_CRUD_003 - PATCH Update Part")

    assert response.json()["description"] == "Patched Desc"


# =========================
# DELETE PART
# =========================
def test_delete_part(api_client, create_part):
    url = f"{PART_ENDPOINT}{create_part}/"
    response = api_client.delete(url)

    assert_response(response, 200, "TC_CRUD_004 - DELETE Part")


# =========================
# NEGATIVE DELETE
# =========================
def test_delete_invalid_part(api_client):
    response = api_client.delete(f"{PART_ENDPOINT}999999/")

    assert response.status_code in [404, 400]


# =========================
# IDEMPOTENCY TEST
# =========================
def test_delete_idempotency(api_client, create_part):
    url = f"{PART_ENDPOINT}{create_part}/"

    first = api_client.delete(url)
    second = api_client.delete(url)

    assert first.status_code in [200, 204]

    assert second.status_code in [404, 400]


# =========================
# RATE LIMIT TEST
# =========================
def test_rate_limiting(api_client):
    responses = []

    for _ in range(20):
        r = api_client.get(PART_ENDPOINT)
        responses.append(r.status_code)

    logger.info(f"Rate limit responses: {responses}")

    assert all(code in [200, 429] for code in responses)