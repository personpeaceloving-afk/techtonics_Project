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
import requests
import pytest
import logging
import time
import uuid

# =========================
# CONFIG
# =========================
BASE_URL = os.environ.get("BASE_URL", "https://demo.inventree.org/api")
PART_ENDPOINT = "/part/"
AUTH_TOKEN = os.environ.get("INVENTREE_TOKEN")

HEADERS = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
} if AUTH_TOKEN else {}

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================
# FIXTURE: CREATE PART
# =========================
@pytest.fixture
def create_part():
    payload = {
        "name": f"AutoPart-{uuid.uuid4()}",
        "description": "Test Part",
        "active": True
    }
    response = requests.post(BASE_URL + PART_ENDPOINT, json=payload, headers=HEADERS)
    assert response.status_code in [200, 201]
    return response.json()["pk"]


# =========================
# POST - CREATE PART
# =========================
@pytest.mark.parametrize("payload, expected_status", [
    ({"name": f"ValidPart-{uuid.uuid4()}"}, 201),
    ({}, 400),  # missing required
    ({"name": ""}, 400),
])
def test_create_part(payload, expected_status):
    logger.info(f"Creating part with payload: {payload}")

    response = requests.post(BASE_URL + PART_ENDPOINT, json=payload, headers=HEADERS)

    assert response.status_code == expected_status


# =========================
# PUT - FULL UPDATE
# =========================
def test_put_update_part(create_part):
    part_id = create_part

    payload = {
        "name": f"Updated-{uuid.uuid4()}",
        "description": "Updated Desc",
        "active": False
    }

    url = f"{BASE_URL}{PART_ENDPOINT}{part_id}/"
    response = requests.put(url, json=payload, headers=HEADERS)

    logger.info(f"PUT update response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]


# =========================
# PATCH - PARTIAL UPDATE
# =========================
def test_patch_update_part(create_part):
    part_id = create_part

    payload = {"description": "Patched Desc"}

    url = f"{BASE_URL}{PART_ENDPOINT}{part_id}/"
    response = requests.patch(url, json=payload, headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["description"] == "Patched Desc"


# =========================
# DELETE PART
# =========================
def test_delete_part(create_part):
    part_id = create_part

    url = f"{BASE_URL}{PART_ENDPOINT}{part_id}/"
    response = requests.delete(url, headers=HEADERS)

    assert response.status_code in [200, 204]


# =========================
# NEGATIVE DELETE
# =========================
def test_delete_invalid_part():
    url = f"{BASE_URL}{PART_ENDPOINT}999999/"
    response = requests.delete(url, headers=HEADERS)

    assert response.status_code in [404, 400]


# =========================
# IDEMPOTENCY TEST (DELETE)
# =========================
def test_delete_idempotency(create_part):
    part_id = create_part
    url = f"{BASE_URL}{PART_ENDPOINT}{part_id}/"

    first = requests.delete(url, headers=HEADERS)
    second = requests.delete(url, headers=HEADERS)

    assert first.status_code in [200, 204]
    assert second.status_code in [404, 400]  # already deleted


# =========================
# RATE LIMIT TEST
# =========================
def test_rate_limiting():
    url = BASE_URL + PART_ENDPOINT

    responses = []
    for _ in range(20):
        r = requests.get(url, headers=HEADERS)
        responses.append(r.status_code)

    logger.info(f"Rate test responses: {responses}")

    assert all(code in [200, 429] for code in responses)