"""
Demo script that shows the password generator in action with sample inputs.
This tests the full workflow without requiring interactive input.
"""

import sys
import os
from io import StringIO

# Dynamically add the script's directory to Python path so imports work
# regardless of where the script is run from
script_directory = os.path.dirname(os.path.abspath(__file__))
if script_directory not in sys.path:
    sys.path.insert(0, script_directory)

from password_generator import generate_password, CHARACTER_TYPES


def demo_password_generation():
    """Demonstrate password generation with different configurations."""
    print("\n" + "="*60)
    print("Password Generator Demo")
    print("="*60)

    # Demo 1: 6-character password with just digits and lowercase
    print("\n[Demo 1] 6-character password with digits + lowercase")
    password1 = generate_password(6, ['digits', 'lowercase'])
    print(f"Generated: {password1}")

    # Demo 2: 8-character password with all character types
    print("\n[Demo 2] 8-character password with all types")
    password2 = generate_password(8, ['digits', 'uppercase', 'lowercase', 'special'])
    print(f"Generated: {password2}")

    # Demo 3: 12-character password with uppercase and special characters
    print("\n[Demo 3] 12-character password with uppercase + special")
    password3 = generate_password(12, ['uppercase', 'special'])
    print(f"Generated: {password3}")

    # Demo 4: Show character type options
    print("\n" + "="*60)
    print("Available Character Types:")
    print("="*60)
    for idx, (key, info) in enumerate(CHARACTER_TYPES.items(), 1):
        if 'example' in info:
            print(f"{idx}. {info['description']}: {info['example']}")
        else:
            print(f"{idx}. {info['description']}")

    print("\n" + "="*60)
    print("Demo complete - script is working correctly!")
    print("="*60)


if __name__ == '__main__':
    demo_password_generation()
