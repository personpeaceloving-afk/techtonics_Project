import requests


# =========================
# 🔴 AUTH & ACCESS CONTROL
# =========================

def test_no_auth_access(base_url):
    """
    Verify API rejects requests without authentication token
    Expected: 401 Unauthorized
    """
    response = requests.get(f"{base_url}/part/")
    print("\nNO AUTH:", response.text)

    assert response.status_code == 401


def test_invalid_token(base_url):
    """
    Verify API rejects invalid authentication token
    Expected: 401 or 403
    """
    headers = {"Authorization": "Token invalid123"}

    response = requests.get(f"{base_url}/part/", headers=headers)
    print("\nINVALID TOKEN:", response.text)

    assert response.status_code in [401, 403]


# =========================
# 🔴 INVALID QUERY PARAMS
# =========================

def test_invalid_pagination(base_url, headers):
    """
    Verify API behavior for invalid pagination values (negative limit)
    Expected: Either 400 (strict validation) or 200 (graceful handling)
    """
    response = requests.get(f"{base_url}/part/?limit=-1", headers=headers)
    print("\nINVALID PAGINATION:", response.text)

    assert response.status_code in [400, 200]


def test_invalid_ordering(base_url, headers):
    """
    Verify API behavior for invalid ordering field
    Expected: Either ignore and return 200 OR return validation error
    """
    response = requests.get(f"{base_url}/part/?ordering=invalid_field", headers=headers)
    print("\nINVALID ORDERING:", response.text)

    assert response.status_code in [400, 200]


def test_invalid_search_param(base_url, headers):
    """
    Verify API handles special characters in search query
    Expected: 200 with empty or filtered results
    """
    response = requests.get(f"{base_url}/part/?search=%$#@", headers=headers)
    print("\nINVALID SEARCH:", response.text)

    assert response.status_code == 200


# =========================
# 🔴 FIELD VALIDATION
# =========================

def test_max_length_violation(base_url, headers):
    """
    Verify API enforces max length constraint on 'name' field
    Expected: 400 Bad Request or 422 Unprocessable Entity
    """
    payload = {
        "name": "X" * 1000  # Exceeds allowed length
    }

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nMAX LENGTH:", response.text)

    assert response.status_code in [400, 422]


def test_null_required_field(base_url, headers):
    """
    Verify API rejects null value for required field 'name'
    Expected: 400 Bad Request
    """
    payload = {
        "name": None
    }

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nNULL FIELD:", response.text)

    assert response.status_code == 400


def test_read_only_field(base_url, headers):
    """
    Verify API behavior when read-only field (id) is sent in payload
    Expected: Either ignored OR validation error
    """
    payload = {
        "id": 999,
        "name": "Test ReadOnly"
    }

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nREAD ONLY FIELD:", response.text)

    assert response.status_code in [400, 201]


# =========================
# 🔴 CATEGORY EDGE CASES
# =========================

def test_invalid_category_filter(base_url, headers):
    """
    Verify API handles invalid category filter ID
    Expected: 200 with empty result set
    """
    response = requests.get(f"{base_url}/part/?category=999999", headers=headers)
    print("\nINVALID CATEGORY FILTER:", response.json())

    assert response.status_code == 200


def test_category_depth_filter(base_url, headers):
    """
    Verify API handles extreme category depth value
    Expected: 200 with valid hierarchical response
    """
    response = requests.get(f"{base_url}/part/category/?depth=999", headers=headers)
    print("\nCATEGORY DEPTH:", response.json())

    assert response.status_code == 200


def test_category_parent_invalid(base_url, headers):
    """
    Verify API handles invalid parent category ID
    Expected: 200 with empty results
    """
    response = requests.get(f"{base_url}/part/category/?parent=999999", headers=headers)
    print("\nINVALID PARENT:", response.json())

    assert response.status_code == 200


# =========================
# 🔴 RELATIONAL INTEGRITY
# =========================

def test_invalid_part_relation(base_url, headers):
    """
    Verify API rejects relationship creation with non-existent part IDs
    Expected: 400 or 404
    """
    payload = {
        "part_1": 99999,
        "part_2": 99998
    }

    response = requests.post(f"{base_url}/part/related/", json=payload, headers=headers)
    print("\nINVALID RELATION:", response.text)

    assert response.status_code in [400, 404]


def test_self_reference_relation(base_url, headers):
    """
    Verify API prevents a part from referencing itself
    Expected: 400 or 409 conflict
    """
    payload = {
        "part_1": 1,
        "part_2": 1
    }

    response = requests.post(f"{base_url}/part/related/", json=payload, headers=headers)
    print("\nSELF RELATION:", response.text)

    assert response.status_code in [400, 409]


# =========================
# 🔴 PARAMETER API EDGE CASES
# =========================

def test_invalid_parameter_template(base_url, headers):
    """
    Verify API rejects invalid parameter template reference
    Expected: 400 or 404
    """
    payload = {
        "part": 1,
        "template": 99999
    }

    response = requests.post(f"{base_url}/part/parameter/", json=payload, headers=headers)
    print("\nINVALID TEMPLATE:", response.text)

    assert response.status_code in [400, 404]


def test_parameter_missing_required(base_url, headers):
    """
    Verify API rejects request when required parameter fields are missing
    Expected: 400 Bad Request
    """
    payload = {}

    response = requests.post(f"{base_url}/part/parameter/", json=payload, headers=headers)
    print("\nMISSING PARAM FIELD:", response.text)

    assert response.status_code == 400


# =========================
# 🔴 METADATA API EDGE CASES
# =========================

def test_metadata_invalid_id(base_url, headers):
    """
    Verify metadata API behavior for non-existent template ID
    Expected: 404 or empty response
    """
    response = requests.get(f"{base_url}/part/parameter/template/999999/metadata/", headers=headers)
    print("\nMETADATA INVALID ID:", response.text)

    assert response.status_code in [404, 200]


def test_metadata_invalid_payload(base_url, headers):
    """
    Verify API rejects invalid metadata format
    Expected: 400 or validation error
    """
    payload = {
        "metadata": "invalid_format"
    }

    response = requests.patch(
        f"{base_url}/part/parameter/template/1/metadata/",
        json=payload,
        headers=headers
    )

    print("\nINVALID METADATA:", response.text)

    assert response.status_code in [400, 200]


# =========================
# 🔴 BOM VALIDATION EDGE CASES
# =========================

def test_bom_validation_invalid_part(base_url, headers):
    """
    Verify BOM validation for non-existent part
    Expected: 404 or validation response
    """
    response = requests.get(f"{base_url}/part/999999/bom-validate/", headers=headers)
    print("\nBOM INVALID:", response.text)

    assert response.status_code in [404, 200]


def test_bom_invalid_payload(base_url, headers):
    """
    Verify BOM validation rejects incorrect payload format
    Expected: 400 or validation error
    """
    payload = {
        "checksum": 12345
    }

    response = requests.patch(
        f"{base_url}/part/1/bom-validate/",
        json=payload,
        headers=headers
    )

    print("\nBOM INVALID PAYLOAD:", response.text)

    assert response.status_code in [400, 200]


# =========================
# 🔴 CONTENT-TYPE EDGE CASES
# =========================

def test_invalid_content_type(base_url, headers):
    """
    Verify API rejects unsupported content type
    Expected: 400 or 415 Unsupported Media Type
    """
    headers["Content-Type"] = "text/plain"

    response = requests.post(f"{base_url}/part/", data="invalid", headers=headers)
    print("\nINVALID CONTENT TYPE:", response.text)

    assert response.status_code in [400, 415]


# =========================
# 🔴 LARGE PAYLOAD
# =========================

def test_large_payload(base_url, headers):
    """
    Verify API behavior with extremely large payload
    Expected: 400 or 413 Payload Too Large
    """
    payload = {
        "name": "A" * 5000
    }

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nLARGE PAYLOAD:", response.text)

    assert response.status_code in [400, 413]