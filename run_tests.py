"""
Test runner script for the expense splitting project
"""

import subprocess
import sys
import os


def main():
    """Run all tests and display results."""
    print("Running comprehensive test suite for expense splitting project...")
    print("=" * 60)

    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    try:
        # Run pytest with verbose output
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--color=yes",
            ],
            capture_output=True,
            text=True,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(f"\nTest run completed with return code: {result.returncode}")

        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed.")

        return result.returncode

    except FileNotFoundError:
        print("Error: pytest not found. Please install it with: pip install pytest")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
