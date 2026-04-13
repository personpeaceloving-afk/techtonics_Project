import pytest

BASE_URL = "https://demo.inventree.org/api"
TOKEN = "inv-fb927bf626acaa2127a8f8279f3d4d6335585d9e-20260413"



HEADERS = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def headers():
    return {
        "Authorization": f"Token {TOKEN}",
        "Content-Type": "application/json"
    }