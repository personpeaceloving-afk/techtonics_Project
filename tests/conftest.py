import pytest

BASE_URL = "https://demo.inventree.org/api"
TOKEN = "inv-61024d3ac9cd26e883afdc67848baaa137a46512-20260414"



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