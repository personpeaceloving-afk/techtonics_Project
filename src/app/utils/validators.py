"""
Module: validators.py

Description:
    Common validation utilities for API responses.
    Ensures consistent data format checks across the framework.
"""

from typing import Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_list(data: Any, field_name: str = "response") -> List:
    """
    Validates that the input data is a list.

    Args:
        data (Any): Input data to validate
        field_name (str): Name of the field for error context

    Returns:
        List: Validated list data

    Raises:
        ValueError: If data is not a list
    """

    if not isinstance(data, list):
        logger.error(f"{field_name} validation failed. Expected list, got {type(data)}")
        raise ValueError(
            f"Invalid response format for '{field_name}'. Expected list but got {type(data).__name__}"
        )

    logger.info(f"{field_name} validated successfully. Items: {len(data)}")
    return data