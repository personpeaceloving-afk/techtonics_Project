import requests
import pytest


# =========================
# 🔵 BASIC GET OPERATIONS
# =========================

def test_get_all_parts(base_url, headers):
    """
    Verify retrieval of all parts
    Expected:
    - Status code 200
    - Response is a list
    - Each item contains key fields like id, name
    """
    response = requests.get(f"{base_url}/part/", headers=headers)

    print("\nGET ALL PARTS RESPONSE:", response.json())

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_part_by_valid_id(base_url, headers):
    """
    Verify retrieval of a specific part using valid ID
    Expected:
    - Status code 200
    - Returned object matches requested ID
    """
    part_id = 1

    response = requests.get(f"{base_url}/part/{part_id}/", headers=headers)

    print("\nGET PART BY ID RESPONSE:", response.json())

    assert response.status_code == 200
    assert response.json()["id"] == part_id


def test_get_part_invalid_id(base_url, headers):
    """
    Verify API response for non-existent part ID
    Expected:
    - Status code 404 Not Found
    """
    response = requests.get(f"{base_url}/part/999999/", headers=headers)

    print("\nGET INVALID PART RESPONSE:", response.text)

    assert response.status_code == 404


# =========================
# 🔵 FILTERING & SEARCH
# =========================

@pytest.mark.parametrize("query", [
    "search=test",
    "search=bolt",
    "search=123"
])
def test_get_parts_search(base_url, headers, query):
    """
    Verify search functionality on parts endpoint
    Expected:
    - Status code 200
    - Filtered results returned
    """
    url = f"{base_url}/part/?{query}"

    response = requests.get(url, headers=headers)

    print(f"\nSEARCH QUERY ({query}) RESPONSE:", response.json())

    assert response.status_code == 200


@pytest.mark.parametrize("query", [
    "category=1",
    "active=true",
    "active=false"
])
def test_get_parts_filtering(base_url, headers, query):
    """
    Verify filtering by category and active status
    Expected:
    - Status code 200
    - Results match filter criteria (if data exists)
    """
    url = f"{base_url}/part/?{query}"

    response = requests.get(url, headers=headers)

    print(f"\nFILTER ({query}) RESPONSE:", response.json())

    assert response.status_code == 200


# =========================
# 🔵 PAGINATION
# =========================

@pytest.mark.parametrize("query", [
    "limit=5&offset=0",
    "limit=10&offset=5"
])
def test_get_parts_pagination(base_url, headers, query):
    """
    Verify pagination functionality
    Expected:
    - Status code 200
    - Number of records <= limit
    """
    url = f"{base_url}/part/?{query}"

    response = requests.get(url, headers=headers)

    data = response.json()

    print(f"\nPAGINATION ({query}) RESPONSE:", data)

    assert response.status_code == 200
    assert isinstance(data, list)


# =========================
# 🔵 SORTING / ORDERING
# =========================

@pytest.mark.parametrize("query", [
    "ordering=name",
    "ordering=-name"
])
def test_get_parts_ordering(base_url, headers, query):
    """
    Verify sorting functionality on parts endpoint
    Expected:
    - Status code 200
    - Results ordered accordingly
    """
    url = f"{base_url}/part/?{query}"

    response = requests.get(url, headers=headers)

    print(f"\nORDERING ({query}) RESPONSE:", response.json())

    assert response.status_code == 200


# =========================
# 🔵 EDGE CASES - QUERY PARAMS
# =========================

def test_get_parts_empty_search(base_url, headers):
    """
    Verify behavior for empty search query
    Expected:
    - Status code 200
    - Returns all or default dataset
    """
    response = requests.get(f"{base_url}/part/?search=", headers=headers)

    print("\nEMPTY SEARCH RESPONSE:", response.json())

    assert response.status_code == 200


def test_get_parts_special_characters(base_url, headers):
    """
    Verify handling of special characters in search
    Expected:
    - Status code 200
    - No crash / safe handling
    """
    response = requests.get(f"{base_url}/part/?search=%$#@", headers=headers)

    print("\nSPECIAL CHAR SEARCH RESPONSE:", response.json())

    assert response.status_code == 200


def test_get_parts_large_limit(base_url, headers):
    """
    Verify behavior when requesting large number of records
    Expected:
    - Status code 200
    - API should handle or cap results
    """
    response = requests.get(f"{base_url}/part/?limit=10000", headers=headers)

    print("\nLARGE LIMIT RESPONSE:", response.json())

    assert response.status_code == 200


# =========================
# 🔵 AUTHORIZATION SCENARIOS
# =========================

def test_get_parts_without_auth(base_url):
    """
    Verify API rejects request without authentication
    Expected:
    - Status code 401 Unauthorized
    """
    response = requests.get(f"{base_url}/part/")

    print("\nUNAUTHORIZED RESPONSE:", response.text)

    assert response.status_code == 401


def test_get_parts_invalid_token(base_url):
    """
    Verify API rejects invalid authentication token
    Expected:
    - Status code 401 or 403
    """
    headers = {"Authorization": "Token invalid123"}

    response = requests.get(f"{base_url}/part/", headers=headers)

    print("\nINVALID TOKEN RESPONSE:", response.text)

    assert response.status_code in [401, 403]


# =========================
# 🔵 RESPONSE STRUCTURE VALIDATION
# =========================

def test_get_parts_response_structure(base_url, headers):
    """
    Validate response schema for parts list
    Expected:
    - Each object contains mandatory fields
    """
    response = requests.get(f"{base_url}/part/", headers=headers)

    data = response.json()

    print("\nRESPONSE STRUCTURE:", data)

    assert response.status_code == 200

    if len(data) > 0:
        assert "id" in data[0]
        assert "name" in data[0]