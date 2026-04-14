"""
Module: test_part_edge_cases.py

Description:
    Comprehensive edge case and negative test scenarios for Part APIs.
    Focuses on authentication, validation, relational integrity, and API robustness.

Design Principles:
    - No direct requests usage
    - Uses APIClient / service layer abstraction
    - Structured logging instead of print
    - Maintainable enterprise-grade test design
"""

import pytest
from utils.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# 🔴 AUTH & ACCESS CONTROL
# =========================================================

def test_no_auth_access(api_client):
    """
    Verify API rejects requests without authentication token
    Expected: 401 Unauthorized
    """
    response = api_client.get("/part/")

    logger.info(f"NO AUTH RESPONSE: {response.text}")
    assert response.status_code == 401


def test_invalid_token(api_client):
    """
    Verify API rejects invalid authentication token
    Expected: 401 or 403
    """
    api_client.headers["Authorization"] = "Token invalid123"

    response = api_client.get("/part/")

    logger.info(f"INVALID TOKEN RESPONSE: {response.text}")
    assert response.status_code in [401, 403]


# =========================================================
# 🔴 INVALID QUERY PARAMETERS
# =========================================================

def test_invalid_pagination(api_client):
    response = api_client.get("/part/?limit=-1")

    logger.info(f"INVALID PAGINATION: {response.text}")
    assert response.status_code in [200, 400]


def test_invalid_ordering(api_client):
    response = api_client.get("/part/?ordering=invalid_field")

    logger.info(f"INVALID ORDERING: {response.text}")
    assert response.status_code in [200, 400]


def test_invalid_search_param(api_client):
    response = api_client.get("/part/?search=%$#@")

    logger.info(f"INVALID SEARCH: {response.text}")
    assert response.status_code == 200


# =========================================================
# 🔴 FIELD VALIDATION
# =========================================================

def test_max_length_violation(api_client):
    payload = {"name": "X" * 1000}

    response = api_client.post("/part/", payload)

    logger.info(f"MAX LENGTH RESPONSE: {response.text}")
    assert response.status_code in [400, 422]


def test_null_required_field(api_client):
    payload = {"name": None}

    response = api_client.post("/part/", payload)

    logger.info(f"NULL FIELD RESPONSE: {response.text}")
    assert response.status_code == 400


def test_read_only_field(api_client):
    payload = {"id": 999, "name": "Test ReadOnly"}

    response = api_client.post("/part/", payload)

    logger.info(f"READ ONLY FIELD RESPONSE: {response.text}")
    assert response.status_code in [400, 201]


# =========================================================
# 🔴 CATEGORY EDGE CASES
# =========================================================

def test_invalid_category_filter(api_client):
    response = api_client.get("/part/?category=999999")

    logger.info(f"INVALID CATEGORY FILTER: {response.text}")
    assert response.status_code == 200


def test_category_depth_filter(api_client):
    response = api_client.get("/part/category/?depth=999")

    logger.info(f"CATEGORY DEPTH: {response.text}")
    assert response.status_code == 200


def test_category_parent_invalid(api_client):
    response = api_client.get("/part/category/?parent=999999")

    logger.info(f"INVALID PARENT CATEGORY: {response.text}")
    assert response.status_code == 200


# =========================================================
# 🔴 RELATIONAL INTEGRITY
# =========================================================

def test_invalid_part_relation(api_client):
    payload = {"part_1": 99999, "part_2": 99998}

    response = api_client.post("/part/related/", payload)

    logger.info(f"INVALID RELATION: {response.text}")
    assert response.status_code in [400, 404]


def test_self_reference_relation(api_client):
    payload = {"part_1": 1, "part_2": 1}

    response = api_client.post("/part/related/", payload)

    logger.info(f"SELF REFERENCE: {response.text}")
    assert response.status_code in [400, 409]


# =========================================================
# 🔴 PARAMETER API EDGE CASES
# =========================================================

def test_invalid_parameter_template(api_client):
    payload = {"part": 1, "template": 99999}

    response = api_client.post("/part/parameter/", payload)

    logger.info(f"INVALID TEMPLATE: {response.text}")
    assert response.status_code in [400, 404]


def test_parameter_missing_required(api_client):
    response = api_client.post("/part/parameter/", {})

    logger.info(f"MISSING PARAMS: {response.text}")
    assert response.status_code == 400


# =========================================================
# 🔴 METADATA EDGE CASES
# =========================================================

def test_metadata_invalid_id(api_client):
    response = api_client.get(
        "/part/parameter/template/999999/metadata/"
    )

    logger.info(f"INVALID METADATA ID: {response.text}")
    assert response.status_code in [404, 200]


def test_metadata_invalid_payload(api_client):
    payload = {"metadata": "invalid_format"}

    response = api_client.patch(
        "/part/parameter/template/1/metadata/",
        payload
    )

    logger.info(f"INVALID METADATA: {response.text}")
    assert response.status_code in [400, 200]


# =========================================================
# 🔴 BOM EDGE CASES
# =========================================================

def test_bom_validation_invalid_part(api_client):
    response = api_client.get("/part/999999/bom-validate/")

    logger.info(f"BOM INVALID PART: {response.text}")
    assert response.status_code in [404, 200]


def test_bom_invalid_payload(api_client):
    payload = {"checksum": 12345}

    response = api_client.patch("/part/1/bom-validate/", payload)

    logger.info(f"BOM INVALID PAYLOAD: {response.text}")
    assert response.status_code in [400, 200]


# =========================================================
# 🔴 CONTENT TYPE EDGE CASES
# =========================================================

def test_invalid_content_type(api_client):
    headers = {"Content-Type": "text/plain"}

    response = api_client.post("/part/", "invalid", headers=headers)

    logger.info(f"INVALID CONTENT TYPE: {response.text}")
    assert response.status_code in [400, 415]


# =========================================================
# 🔴 LARGE PAYLOAD
# =========================================================

def test_large_payload(api_client):
    payload = {"name": "A" * 5000}

    response = api_client.post("/part/", payload)

    logger.info(f"LARGE PAYLOAD: {response.text}")
    assert response.status_code in [400, 413]