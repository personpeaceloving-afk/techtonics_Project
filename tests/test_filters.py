import requests
import pytest

@pytest.mark.parametrize("query", [
    "search=test",
    "limit=5&offset=0",
    "ordering=name"
])
def test_filters(base_url, headers, query):
    url = f"{base_url}/part/?{query}"

    response = requests.get(url, headers=headers)
    print(f"\nFILTER {query}:", response.json())

    assert response.status_code == 200