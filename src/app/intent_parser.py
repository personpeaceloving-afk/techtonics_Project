"""
Module: intent_parser.py

Description:
    Parses user natural language input into test execution targets.
"""

from utils.logger import get_logger

logger = get_logger(__name__)


INTENT_MAP = {
    "get": "test_get_part.py",
    "post": "test_edge_cases.py",
    "put": "test_filters.py",
    "patch": "test_parts_crud.py",
    "delete": "test_delete_part.py",
    "all": "ALL"
}


def parse_intent(user_input: str):
    """
    Convert user command into pytest file mapping.

    Args:
        user_input (str): Natural language input

    Returns:
        str | None: test file or ALL
    """

    if not user_input:
        logger.warning("Empty user input received")
        return None

    user_input = user_input.lower().strip()

    for key, value in INTENT_MAP.items():
        if key in user_input:
            logger.info(f"Intent matched: {key} → {value}")
            return value

    logger.warning(f"No intent matched for input: {user_input}")
    return None