"""
Test Module: test_category_crud.py
Description:
    CRUD Test Suite for Category APIs
"""

import os
import requests
import pytest
import logging
import uuid

BASE_URL = os.environ.get("BASE_URL", "https://demo.inventree.org/api")
CATEGORY_ENDPOINT = "/part/category/"
AUTH_TOKEN = os.environ.get("INVENTREE_TOKEN")

HEADERS = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
} if AUTH_TOKEN else {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================
# FIXTURE
# =========================
@pytest.fixture
def create_category():
    payload = {
        "name": f"Category-{uuid.uuid4()}",
        "description": "Test Category"
    }
    response = requests.post(BASE_URL + CATEGORY_ENDPOINT, json=payload, headers=HEADERS)

    assert response.status_code in [200, 201]
    return response.json()["pk"]


# =========================
# POST CATEGORY
# =========================
@pytest.mark.parametrize("payload, expected", [
    ({"name": f"Cat-{uuid.uuid4()}"}, 201),
    ({}, 400),
])
def test_create_category(payload, expected):
    response = requests.post(BASE_URL + CATEGORY_ENDPOINT, json=payload, headers=HEADERS)

    assert response.status_code == expected


# =========================
# PUT CATEGORY
# =========================
def test_put_category(create_category):
    cat_id = create_category

    payload = {
        "name": f"Updated-{uuid.uuid4()}",
        "description": "Updated"
    }

    url = f"{BASE_URL}{CATEGORY_ENDPOINT}{cat_id}/"
    response = requests.put(url, json=payload, headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["name"] == payload["name"]


# =========================
# PATCH CATEGORY
# =========================
def test_patch_category(create_category):
    cat_id = create_category

    payload = {"description": "Patched"}

    url = f"{BASE_URL}{CATEGORY_ENDPOINT}{cat_id}/"
    response = requests.patch(url, json=payload, headers=HEADERS)

    assert response.status_code == 200


# =========================
# DELETE CATEGORY
# =========================
def test_delete_category(create_category):
    cat_id = create_category

    url = f"{BASE_URL}{CATEGORY_ENDPOINT}{cat_id}/"
    response = requests.delete(url, headers=HEADERS)

    assert response.status_code in [200, 204]


# =========================
# NEGATIVE CATEGORY
# =========================
def test_invalid_category_update():
    url = f"{BASE_URL}{CATEGORY_ENDPOINT}999999/"
    response = requests.put(url, json={"name": "X"}, headers=HEADERS)

    assert response.status_code in [404, 400]


# =========================
# IDEMPOTENCY
# =========================
def test_category_delete_idempotency(create_category):
    cat_id = create_category
    url = f"{BASE_URL}{CATEGORY_ENDPOINT}{cat_id}/"

    first = requests.delete(url, headers=HEADERS)
    second = requests.delete(url, headers=HEADERS)

    assert first.status_code in [200, 204]
    assert second.status_code in [404, 400]


# =========================
# BOUNDARY TEST
# =========================
@pytest.mark.parametrize("name", [
    "A" * 255,   # max length
    "",          # empty
])
def test_category_name_boundary(name):
    payload = {"name": name}
    response = requests.post(BASE_URL + CATEGORY_ENDPOINT, json=payload, headers=HEADERS)

    assert response.status_code in [201, 400]