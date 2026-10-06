import argparse
import os

from app.assistant import CodingAssistant


def main():
    parser = argparse.ArgumentParser(description="Run a coding task against a repository")
    parser.add_argument("description", help="What needs to be fixed or implemented")
    parser.add_argument("--repo-root", default=os.getenv("REPO_ROOT", "."), help="Repository root to inspect")
    args = parser.parse_args()

    assistant = CodingAssistant(args.repo_root)
    result = assistant.run_task(args.description)
    print(result)


if __name__ == "__main__":
    main()
