import subprocess
from app.intent_parser import parse_intent


def run_tests(file_name):
    if file_name == "ALL":
        cmd = ["pytest", "-v", "-s"]
    else:
        cmd = ["pytest", f"tests/{file_name}", "-v", "-s"]

    print(f"\n🚀 Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False, text=True)

    return result.returncode


def start_agent():
    print("\n🤖 API TEST AGENT READY")
    print("Type your command (e.g., 'run get tests', 'run all tests', 'edge cases')\n")

    while True:
        user_input = input("👉 Enter command: ")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting agent...")
            break

        file_name = parse_intent(user_input)

        if not file_name:
            print("❌ Unknown command. Try again.")
            continue

        run_tests(file_name)