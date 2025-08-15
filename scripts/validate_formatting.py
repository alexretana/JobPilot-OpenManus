#!/usr/bin/env python3
"""
Quick validation script to check if code formatting is correct before committing.
Run this to avoid pre-commit hook failures.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Checking Python environment...")

    # Check Python version
    result = subprocess.run(
        [sys.executable, "--version"], capture_output=True, text=True
    )
    print(f"Python: {result.stdout.strip()}")

    # Check required tools
    tools = ["black", "isort", "pre-commit"]
    for tool in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool}: {result.stdout.strip()}")
            else:
                print(f"❌ {tool}: Not available")
                return False
        except FileNotFoundError:
            print(f"❌ {tool}: Not installed")
            return False

    return True


def main():
    """Run formatting validation."""
    print("=" * 50)
    print("🧹 JobPilot-OpenManus Formatting Validator")
    print("=" * 50)

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please check DEVELOPMENT_SETUP.md")
        return False

    # Files to check (the ones that were causing issues)
    problem_files = [
        "api_research/tests/test_jsearch.py",
        "api_research/implementations/jsearch_client.py",
        "scripts/check_db.py",
        "scripts/run_mcp_server.py",
    ]

    all_passed = True

    # Check each file with isort
    for file in problem_files:
        if Path(file).exists():
            cmd = f"isort --profile black --check-only --diff {file}"
            if not run_command(cmd, f"isort check on {file}"):
                all_passed = False
                print(f"💡 To fix: isort --profile black {file}")

    # Check Black formatting
    black_cmd = "black --check --diff api_research/ scripts/"
    if not run_command(black_cmd, "Black formatting check"):
        all_passed = False
        print("💡 To fix: black api_research/ scripts/")

    # Run pre-commit on the problem files
    files_str = " ".join(problem_files)
    precommit_cmd = f"pre-commit run --files {files_str}"
    if not run_command(precommit_cmd, "Pre-commit hooks on problem files"):
        all_passed = False
        print("💡 To fix: Run the suggested fixes above, then try again")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All formatting checks PASSED! Ready to commit.")
    else:
        print(
            "❌ Some formatting checks FAILED. Fix the issues above before committing."
        )
    print("=" * 50)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
