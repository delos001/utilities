"""
Entry point for the interactive app: python -m password_generator

Runs the unit tests first to verify the logic, then launches the CLI.
"""

from .cli import main
from .tests import run_tests

if __name__ == "__main__":
    # Run tests first to verify functionality.
    if run_tests():
        # If tests pass, run the interactive program.
        input("\nPress Enter to start the Password Generator...")
        main()
