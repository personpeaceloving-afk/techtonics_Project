"""
Module: agent_runner.py

Description:
    CLI-based AI Test Agent to execute pytest suites dynamically
    based on user natural language input.
"""

import subprocess
from app.intent_parser import parse_intent
from utils.logger import get_logger

logger = get_logger(__name__)


def run_tests(file_name: str):
    """
    Execute pytest based on selected test file.
    """

    if file_name == "ALL":
        cmd = ["pytest", "-v", "-s"]
    else:
        cmd = ["pytest", f"tests/{file_name}", "-v", "-s"]

    logger.info(f"Executing command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, text=True)
        logger.info(f"Test execution completed with code: {result.returncode}")
        return result.returncode

    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        return -1


def start_agent():
    """
    Interactive CLI agent loop.
    """

    print("\n🤖 API TEST AGENT READY")
    print("Commands: get, post, put, patch, delete, all")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("👉 Enter command: ")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting agent...")
            break

        file_name = parse_intent(user_input)

        if not file_name:
            print("❌ Unknown command. Try again.")
            continue

        exit_code = run_tests(file_name)

        if exit_code == 0:
            print("✅ Tests Passed")
        else:
            print("❌ Some Tests Failed")