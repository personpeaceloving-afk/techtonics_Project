import requests

def test_invalid_category(base_url, headers):
    payload = {
        "name": "Invalid Category Part",
        "category": 99999
    }

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nINVALID CATEGORY:", response.text)

    assert response.status_code in [400, 404]