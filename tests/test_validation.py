import requests

def test_missing_name(base_url, headers):
    payload = {"description": "No name"}

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nMISSING NAME:", response.text)

    assert response.status_code == 400


def test_invalid_type(base_url, headers):
    payload = {"name": 123}

    response = requests.post(f"{base_url}/part/", json=payload, headers=headers)
    print("\nINVALID TYPE:", response.text)

    assert response.status_code == 400