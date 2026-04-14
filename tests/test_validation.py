"""
Test Module: test_part_validation.py
"""

import pytest
import requests
import logging
import uuid
import json

# =========================
# LOGGING SETUP
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =========================
# HELPER: PRETTY PRINT
# =========================
def print_api_details(url, payload, response, scenario):
    print("\n" + "=" * 70)
    print(f"SCENARIO: {scenario}")
    print("=" * 70)

    print("\nREQUEST:")
    print(f"URL: {url}")
    print("Payload:")
    print(json.dumps(payload, indent=4))

    print("\nRESPONSE:")
    print(f"Status Code: {response.status_code}")

    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
    except Exception:
        print("Raw Response:")
        print(response.text)

    print("=" * 70 + "\n")


# =========================
# PARAMETERIZED TEST DATA
# =========================
@pytest.mark.parametrize("payload, expected_status, scenario", [

    ({"description": "No name"}, 400, "Missing name"),
    ({"name": 123}, 400, "Name as integer"),
    ({"name": ""}, 400, "Empty string"),
    ({"name": "A" * 300}, 400, "Exceeds max length"),
    ({"name": None}, 400, "Null name"),

])
def test_part_validation_negative(base_url, headers, payload, expected_status, scenario):

    url = f"{base_url}/part/"

    # Add unique identifier if valid string
    if isinstance(payload.get("name"), str) and payload.get("name"):
        payload["name"] = f"{payload['name']}-{uuid.uuid4()}"

    response = requests.post(url, json=payload, headers=headers)

    # ✅ PRINT TO TERMINAL
    print_api_details(url, payload, response, scenario)

    # =========================
    # ASSERTIONS
    # =========================
    assert response.status_code == expected_status, \
        f"{scenario} failed. Expected {expected_status}, got {response.status_code}"

    try:
        resp_json = response.json()
        assert isinstance(resp_json, dict)

        assert any(key in resp_json for key in ["name", "error", "detail"]), \
            "Expected validation error message"

    except ValueError:
        pytest.fail("Response is not valid JSON")


# =========================
# IDEMPOTENCY CHECK
# =========================
def test_missing_name_idempotency(base_url, headers):

    payload = {"description": "No name"}
    url = f"{base_url}/part/"

    response1 = requests.post(url, json=payload, headers=headers)
    response2 = requests.post(url, json=payload, headers=headers)

    print_api_details(url, payload, response1, "Idempotency - First Call")
    print_api_details(url, payload, response2, "Idempotency - Second Call")

    assert response1.status_code == 400
    assert response2.status_code == 400


# =========================
# RATE LIMIT SIMULATION
# =========================
def test_validation_rate_limit(base_url, headers):

    url = f"{base_url}/part/"
    statuses = []

    for i in range(10):
        payload = {"name": 123}
        response = requests.post(url, json=payload, headers=headers)

        print_api_details(url, payload, response, f"Rate Test Iteration {i+1}")

        statuses.append(response.status_code)

    assert all(code in [400, 429] for code in statuses)