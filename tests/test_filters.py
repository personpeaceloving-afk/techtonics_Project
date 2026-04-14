"""
Test Module: test_filters.py

Description:
    Validates filtering functionality of Part API.
    Ensures query parameters like search, limit, offset, ordering work correctly.
"""

import pytest
from utils.logger import get_logger
from utils.validators import validate_list

logger = get_logger(__name__)


@pytest.mark.parametrize("query", [
    "search=test",
    "limit=5&offset=0",
    "ordering=name"
])
def test_filters(api_client, query):
    """
    Test API filters for Part endpoint.
    """

    endpoint = f"/part/?{query}"

    logger.info(f"Testing filter: {query}")

    response = api_client.get(endpoint)

    logger.info(f"Status Code: {response.status_code}")

    assert response.status_code == 200, f"Failed for query: {query}"

    try:
        data = response.json()
    except Exception as e:
        logger.error(f"Invalid JSON response for query {query}: {str(e)}")
        pytest.fail("Response is not valid JSON")

    # Validate response format
    data = validate_list(data, field_name=f"filter-{query}")

    logger.info(f"Filter test passed for: {query}, items returned: {len(data)}")