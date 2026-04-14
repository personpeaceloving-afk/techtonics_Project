"""
Module: logger.py

Description:
    Centralized logging configuration for the framework.
    Provides structured and consistent logging across modules.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name (str): Module name using __name__

    Returns:
        logging.Logger: Configured logger object
    """

    logger = logging.getLogger(name)

    # Avoid duplicate handlers (important in pytest / frameworks)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Log format (very important for debugging in enterprise systems)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger