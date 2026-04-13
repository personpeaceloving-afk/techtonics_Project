import requests

BASE_URL = "https://demo.inventree.org/api"

def get_parts():
    response = requests.get(f"{BASE_URL}/part/")
    return response.json()

def create_part(name, description):
    payload = {
        "name": name,
        "description": description,
        "active": True
    }

    response = requests.post(f"{BASE_URL}/part/", json=payload)
    return response.json()