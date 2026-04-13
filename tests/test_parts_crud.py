import requests

def test_create_part(base_url, headers):
    payload = {
        "name": "AI Part",
        "description": "Test",
        "active": True
    }

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nCREATE:", response.json())

    assert response.status_code in [200, 201]


def test_get_parts(base_url, headers):
    response = requests.get(f"{base_url}/part/", headers=headers)
    print("\nGET:", response.json())

    assert response.status_code == 200


def test_update_part(base_url, headers):
    part_id = 1

    response = requests.patch(
        f"{base_url}/part/{part_id}/",
        json={"description": "Updated"},
        headers=headers
    )

    print("\nPATCH:", response.json())

    assert response.status_code == 200


def test_delete_part(base_url, headers):
    part_id = 1

    response = requests.delete(f"{base_url}/part/{part_id}/", headers=headers)
    print("\nDELETE:", response.status_code)

    assert response.status_code in [200, 204]