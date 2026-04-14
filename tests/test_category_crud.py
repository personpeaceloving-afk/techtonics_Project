"""
Test Module: test_category_crud.py

Description:
    CRUD + Negative + Boundary test suite for Category APIs.
    Uses service layer + centralized client for maintainability.
"""

import os
import uuid
import pytest

from src.app.api_client import APIClient
from src.app.services.category_service import CategoryService
from utils.logger import get_logger
from utils.validators import validate_list

# =========================
# CONFIGURATION
# =========================

BASE_URL = os.environ.get("BASE_URL", "https://demo.inventree.org/api")
AUTH_TOKEN = os.environ.get("INVENTREE_TOKEN")

HEADERS = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
} if AUTH_TOKEN else {}

logger = get_logger(__name__)

api_client = APIClient(base_url=BASE_URL, headers=HEADERS)
category_service = CategoryService(api_client)


# =========================
# FIXTURE
# =========================

@pytest.fixture
def create_category():
    """
    Creates a category for reuse in test cases.
    """

    logger.info("Creating category via fixture")

    payload = {
        "name": f"Category-{uuid.uuid4()}",
        "description": "Test Category"
    }

    response = api_client.post("/part/category/", payload)

    assert response.status_code in [200, 201], response.text

    data = response.json()
    assert "pk" in data, "Primary key missing in response"

    return data["pk"]


# =========================
# CREATE CATEGORY
# =========================

@pytest.mark.parametrize("payload, expected_status", [
    ({"name": f"Cat-{uuid.uuid4()}"}, 201),
    ({}, 400),
])
def test_create_category(payload, expected_status):
    logger.info("TEST: create_category")

    response = api_client.post("/part/category/", payload)

    logger.info(f"Status Code: {response.status_code}")

    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code} | {response.text}"
    )


# =========================
# UPDATE CATEGORY (PUT)
# =========================

def test_put_category(create_category):
    logger.info("TEST: put_category")

    cat_id = create_category

    payload = {
        "name": f"Updated-{uuid.uuid4()}",
        "description": "Updated"
    }

    response = api_client.put(f"/part/category/{cat_id}/", payload)

    assert response.status_code == 200, response.text
    assert response.json()["name"] == payload["name"]


# =========================
# PATCH CATEGORY
# =========================

def test_patch_category(create_category):
    logger.info("TEST: patch_category")

    cat_id = create_category

    payload = {"description": "Patched"}

    response = api_client.patch(f"/part/category/{cat_id}/", payload)

    assert response.status_code == 200, response.text
    assert response.json().get("description") == "Patched"


# =========================
# DELETE CATEGORY
# =========================

def test_delete_category(create_category):
    logger.info("TEST: delete_category")

    cat_id = create_category

    response = api_client.delete(f"/part/category/{cat_id}/")

    assert response.status_code in [200, 204], response.text


# =========================
# NEGATIVE TEST
# =========================

def test_invalid_category_update():
    logger.info("TEST: invalid_category_update")

    response = api_client.put(
        "/part/category/999999/",
        {"name": "X"}
    )

    assert response.status_code in [404, 400]


# =========================
# IDEMPOTENCY TEST
# =========================

def test_category_delete_idempotency(create_category):
    logger.info("TEST: delete_idempotency")

    cat_id = create_category

    first = api_client.delete(f"/part/category/{cat_id}/")
    second = api_client.delete(f"/part/category/{cat_id}/")

    assert first.status_code in [200, 204]
    assert second.status_code in [404, 400]


# =========================
# BOUNDARY TEST
# =========================

@pytest.mark.parametrize("name", [
    "A" * 255,
    "",
])
def test_category_name_boundary(name):
    logger.info(f"TEST: boundary_name = {name}")

    payload = {"name": name}

    response = api_client.post("/part/category/", payload)

    assert response.status_code in [201, 400]