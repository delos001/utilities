"""
Interactive command-line interface for the password generator.

All user prompts and console output live here. The generation logic itself
is in core.py and has no I/O, so it can be reused without this module.
"""

from .core import (
    CHARACTER_TYPES,
    SPECIAL_CHAR_SETS,
    _build_base_char_sets,
    estimate_entropy,
    generate_password,
    strength_label,
)


def get_password_length() -> int:
    """
    Prompt user to enter desired password length.
    Returns the entered length after validation.
    Handles invalid input with clear error messages.
    Supports exit command.
    """
    print("\nHow many characters would you like your password to be?")
    print("Consider your system's password requirements when choosing a length.")
    print("(Longer passwords are generally more secure.)")
    print("(Type 'exit' or 'quit' to exit)\n")

    while True:
        user_input = input("Enter the number of characters: ").strip()

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nExiting password generator. Goodbye!")
            exit()

        # Attempt to convert input to integer
        try:
            length = int(user_input)

            # Validate that length is a reasonable value
            if length < 4:
                print("Password must be at least 4 characters.")
                continue
            if length > 128:
                print("Password must be 128 characters or fewer.")
                continue

            print(f"You selected {length} characters.")
            return length

        except ValueError:
            print("Please enter a whole number between 4 and 128.")


def display_special_character_options() -> None:
    """
    Display special character preset options with their contents and deltas.
    Helps users understand the progression from basic to full.
    """
    basic = SPECIAL_CHAR_SETS["basic"]["chars"]
    extended = SPECIAL_CHAR_SETS["extended"]["chars"]

    # Calculate characters unique to extended
    extended_only = "".join(c for c in extended if c not in basic)

    print("\n" + "=" * 60)
    print("Special Character Options:")
    print("=" * 60)
    print(f"\n1. Basic: {basic}")
    print(f"\n2. Extended: Basic + {extended_only}")
    print("\n3. Full: Basic + Extended + \" ' ` \\")


def display_character_type_options() -> None:
    """
    Display all available character types with descriptions and examples.
    Helps users understand what's available before making selections.
    """
    print("\n" + "=" * 60)
    print("Available Character Types:")
    print("=" * 60)

    for index, (key, info) in enumerate(CHARACTER_TYPES.items(), 1):
        print(f"\n{index}. {info['description']}")
        if 'example' in info:
            print(f"   Examples: {info['example']}")


def get_special_character_set() -> tuple[str, str, str]:
    """
    Prompt user to select a special character preset (basic, extended, or full).
    Returns a tuple of (selected_set_key, special_chars_to_use, preset_description).
    Supports exit command.
    """
    display_special_character_options()

    print("\n" + "=" * 60)
    print("Note: You can select any predefined set below. If your system")
    print("restricts certain characters within the set you chose, you can")
    print("exclude them in the next step. This lets you use a higher-level")
    print("set while avoiding only the characters you can't use.")
    print("(Type 'exit' or 'quit' to exit)")
    print("=" * 60)

    while True:
        user_input = input("\nEnter the number of the set you'd like (1, 2, or 3): ").strip()

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nExiting password generator. Goodbye!")
            exit()

        try:
            selection = int(user_input)

            if selection not in [1, 2, 3]:
                print("Please enter 1, 2, or 3.")
                continue

            set_keys = ["basic", "extended", "full"]
            selected_key = set_keys[selection - 1]
            selected_chars = SPECIAL_CHAR_SETS[selected_key]["chars"]
            preset_description = SPECIAL_CHAR_SETS[selected_key]["description"]

            print(f"You selected: {preset_description}")
            return (selected_key, selected_chars, preset_description)

        except ValueError:
            print("Please enter a valid number (1, 2, or 3).")


def get_excluded_characters(selected_types: list, special_chars: str = None) -> str:
    """
    Ask the user to exclude any specific characters from the selected pools.
    Applies across every selected type (digits, letters, and special), so a
    user can strip look-alikes such as 0/O/o or 1/l/I in a single step.
    Returns a string of the characters to exclude (empty if none).
    Rejects any exclusion that would empty an entire character class, since
    every selected type must still be representable in the password.
    Supports exit command.
    """
    base_sets = _build_base_char_sets(selected_types, special_chars)

    print("\n" + "=" * 60)
    print("Do you want to exclude any specific characters?")
    print("Common reason: avoid look-alikes such as 0/O and 1/l/I.")
    print("=" * 60)
    print("\nYour selected character pools:")
    for char_type in selected_types:
        label = CHARACTER_TYPES[char_type]["description"]
        if char_type == "special":
            # Special characters are non-obvious, so show them literally.
            print(f"  - {label}: {base_sets[char_type]}")
        else:
            example = CHARACTER_TYPES[char_type].get("example", "")
            print(f"  - {label}: {example}")
    print("\n(Type 'exit' or 'quit' to exit)")

    # Every character that could actually be excluded.
    full_pool = set("".join(base_sets.values()))

    while True:
        user_input = input(
            "\nEnter characters to exclude (just type them, e.g., 0Ol1I), or press Enter to skip: "
        ).strip()

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nExiting password generator. Goodbye!")
            exit()

        if not user_input:
            print("No characters excluded.")
            return ""

        excluded_set = set(user_input)

        # Keep only the entered characters that are actually in some pool.
        relevant = [c for c in user_input if c in full_pool]
        if not relevant:
            print("None of the characters you entered are in your selected pools.")
            continue

        # Reject if any single class would be completely emptied.
        emptied = [
            CHARACTER_TYPES[ct]["description"]
            for ct, chars in base_sets.items()
            if all(c in excluded_set for c in chars)
        ]
        if emptied:
            print(
                "That would remove every character from: "
                + ", ".join(emptied)
                + ". Please exclude fewer characters."
            )
            continue

        # De-duplicate while preserving the order the user typed.
        excluded_display = "".join(dict.fromkeys(relevant))
        print(f"Excluded: {', '.join(excluded_display)}")
        return excluded_display


def get_character_type_selections() -> tuple[list, str, str, str]:
    """
    Show character type options and prompt user to select which types to include.
    Returns a tuple of (selected_types, special_chars_string, excluded_chars_display, preset_name).
    Handles special character preset selection and exclusions.
    """
    display_character_type_options()

    print("\n" + "=" * 60)
    print("Which character types would you like to include?")
    print("(Enter 5 to select all, or type 'exit' to quit)")
    print("=" * 60)

    special_chars = None
    excluded_chars_display = ""
    preset_name = ""

    while True:
        # Get user input for character type selections
        user_input = input(
            "\nEnter numbers separated by commas (example: 1,3,4), or 5 for all: "
        ).strip()

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nExiting password generator. Goodbye!")
            exit()

        # Parse and validate user input
        try:
            # Handle "select all" option
            if user_input == "5":
                selections = [1, 2, 3, 4]
            else:
                # Split input by comma and convert to integers
                selections = [int(x.strip()) for x in user_input.split(",")]

            # Check if selections are in valid range (1-4)
            if not all(1 <= s <= 4 for s in selections):
                print("Please enter numbers between 1 and 4, or 5 for all.")
                continue

            # Check if duplicate selections were made
            if len(selections) != len(set(selections)):
                print(
                    "You entered some options twice. Please select each option only once."
                )
                continue

            # Check if at least one type was selected
            if len(selections) == 0:
                print("You must select at least one character type.")
                continue

            # Convert numeric selections to character type keys
            selected_types = [list(CHARACTER_TYPES.keys())[s - 1] for s in selections]

            # If special characters are selected, choose the preset first.
            if "special" in selected_types:
                set_key, special_chars, preset_name = get_special_character_set()

            # Offer a single exclusion step across every selected type.
            excluded_chars_display = get_excluded_characters(selected_types, special_chars)

            # Build selection summary
            descriptions = []
            for t in selected_types:
                if t == "special":
                    # Show the actual preset selected instead of generic text
                    descriptions.append(f"Special characters ({preset_name})")
                else:
                    descriptions.append(CHARACTER_TYPES[t]['description'])

            print(f"\nYou selected: {', '.join(descriptions)}")

            if excluded_chars_display:
                print(f"Excluded characters: {', '.join(excluded_chars_display)}")

            return (selected_types, special_chars, excluded_chars_display, preset_name)

        except ValueError:
            print("Please enter valid numbers separated by commas (example: 1,2,3), or 5 for all.")


def get_password_count() -> int:
    """
    Ask how many passwords to generate in this batch.
    Pressing Enter defaults to 1. Supports exit command.
    """
    while True:
        user_input = input(
            "\nHow many passwords would you like? (press Enter for 1, max 50): "
        ).strip()

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "q"]:
            print("\nExiting password generator. Goodbye!")
            exit()

        if not user_input:
            return 1

        try:
            count = int(user_input)
            if count < 1:
                print("Please enter a number of 1 or more.")
                continue
            if count > 50:
                print("Please choose 50 or fewer at a time.")
                continue
            return count
        except ValueError:
            print("Please enter a whole number (or press Enter for 1).")


def main() -> None:
    """
    Main program flow: get user preferences, then generate passwords in
    batches, reusing the same settings until the user chooses to quit.
    """
    print("\n" + "=" * 60)
    print("Welcome to the Password Generator!")
    print("=" * 60)

    # Step 1: Get desired password length
    length = get_password_length()

    # Step 2: Get character type selections
    character_types, special_chars, excluded_chars, preset_name = get_character_type_selections()

    # Strength depends only on the settings, so compute it once for all batches.
    bits, pool_size = estimate_entropy(length, character_types, special_chars, excluded_chars)
    strength = strength_label(bits)

    # Step 3: Generate passwords, offering more rounds with the same settings.
    while True:
        count = get_password_count()

        print("\n" + "=" * 60)
        print("Your Generated Password" + ("s:" if count > 1 else ":"))
        print("=" * 60 + "\n")

        for i in range(count):
            password = generate_password(length, character_types, special_chars, excluded_chars)
            if count == 1:
                print(password)
            else:
                print(f"{i + 1}. {password}")

        print(f"\nEstimated strength: {strength} "
              f"(~{bits:.0f} bits of entropy, pool size {pool_size})")
        print("=" * 60)

        again = input(
            "\nGenerate more with the same settings? (Enter = yes, 'q' = quit): "
        ).strip().lower()
        if again in ["q", "quit", "exit"]:
            print("\nExiting password generator. Goodbye!")
            break
