import math
import random
import secrets
import string

# CSPRNG-backed generator. secrets covers the per-character picks; its module
# has no shuffle(), so SystemRandom (also OS-CSPRNG-backed) provides that.
_secure_random = random.SystemRandom()

# Define special character presets
SPECIAL_CHAR_SETS = {
    "basic": {
        "chars": "!@#$%^&*",
        "description": "Basic",
    },
    "extended": {
        "chars": "!@#$%^&*()[]{}+-=.,:;|/<>_~?",
        "description": "Extended",
    },
    "full": {
        "chars": string.punctuation,
        "description": "Full",
    },
}

# Define available character sets for password generation
CHARACTER_TYPES = {
    "digits": {"chars": string.digits, "example": "0-9", "description": "Numbers"},
    "uppercase": {
        "chars": string.ascii_uppercase,
        "example": "A-Z",
        "description": "Uppercase letters",
    },
    "lowercase": {
        "chars": string.ascii_lowercase,
        "example": "a-z",
        "description": "Lowercase letters",
    },
    "special": {
        "description": "Special characters (see next step for preset options)",
    },
}


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
    print("exclude them in the next step — this lets you use a higher-level")
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


def _build_base_char_sets(character_types: list, special_chars: str = None) -> dict:
    """
    Build the unfiltered character pool for each selected type.
    'special' uses the supplied preset, or the basic preset as a fallback.
    Shared by generate_password() and the exclusion step so both agree on
    exactly which characters are in play.
    """
    char_sets = {}
    for char_type in character_types:
        if char_type == "special":
            char_sets[char_type] = special_chars or SPECIAL_CHAR_SETS["basic"]["chars"]
        else:
            char_sets[char_type] = CHARACTER_TYPES[char_type]["chars"]
    return char_sets


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


def generate_password(
    length: int,
    character_types: list,
    special_chars: str = None,
    excluded_chars: str = "",
) -> str:
    """
    Generate a random password of specified length using selected character types.
    Guarantees at least one character from each selected type.

    Args:
        length: Password length
        character_types: List of character type keys to include
        special_chars: Optional custom special characters string (overrides default)
        excluded_chars: Characters to remove from every selected type (e.g. look-alikes)

    Returns:
        A randomly generated password string with all selected types represented

    Raises:
        ValueError: if excluded_chars empties an entire selected character class.
    """
    # Guarantee-one-of-each is impossible if there are more types than slots.
    if length < len(character_types):
        raise ValueError(
            f"length {length} is smaller than the number of selected types "
            f"({len(character_types)}); cannot guarantee one character of each."
        )

    excluded_set = set(excluded_chars)

    # Build each type's pool, then remove any excluded characters from it.
    char_sets = {}
    for char_type, base_chars in _build_base_char_sets(character_types, special_chars).items():
        filtered = "".join(c for c in base_chars if c not in excluded_set)
        if not filtered:
            raise ValueError(
                f"Excluding {excluded_chars!r} leaves no characters for type '{char_type}'."
            )
        char_sets[char_type] = filtered

    # Combine all selected character sets into one string
    available_characters = ""
    for char_set in char_sets.values():
        available_characters += char_set

    # Ensure at least one character from each selected type
    password_chars = []
    for char_type in character_types:
        char_set = char_sets[char_type]
        password_chars.append(secrets.choice(char_set))

    # Fill remaining positions with random characters from all selected types
    remaining_positions = length - len(password_chars)
    for _ in range(remaining_positions):
        password_chars.append(secrets.choice(available_characters))

    # Shuffle the password so it doesn't look predictable
    _secure_random.shuffle(password_chars)

    # Convert list to string and return
    password = "".join(password_chars)
    return password


def estimate_entropy(
    length: int,
    character_types: list,
    special_chars: str = None,
    excluded_chars: str = "",
) -> tuple[float, int]:
    """
    Estimate password entropy in bits for the given settings.

    Entropy is approximated as length * log2(pool_size), where pool_size is the
    count of unique characters available across all selected types after
    exclusions. This is the standard estimate; it slightly overstates the true
    value because guaranteed-inclusion fixes one slot per class, so treat it as
    an upper-bound guide rather than an exact figure.

    Returns:
        A tuple of (entropy_bits, pool_size).
    """
    excluded_set = set(excluded_chars)
    pool = set()
    for base_chars in _build_base_char_sets(character_types, special_chars).values():
        pool.update(c for c in base_chars if c not in excluded_set)

    pool_size = len(pool)
    bits = length * math.log2(pool_size) if pool_size > 1 else 0.0
    return (bits, pool_size)


def strength_label(bits: float) -> str:
    """Map an entropy estimate (in bits) to a human-readable strength label."""
    if bits < 28:
        return "Very weak"
    if bits < 36:
        return "Weak"
    if bits < 60:
        return "Moderate"
    if bits < 128:
        return "Strong"
    return "Very strong"


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


# ============================================================================
# UNIT TESTS
# ============================================================================


def test_password_length() -> None:
    """Test that generated password has the correct length."""
    for length in [6, 8, 12]:
        password = generate_password(length, ["digits", "lowercase"])
        assert (
            len(password) == length
        ), f"Password length should be {length}, got {len(password)}"
    print("[PASS] Password length test passed")


def test_character_type_inclusion() -> None:
    """
    Test that generated password contains characters from selected types.
    This generates multiple passwords to increase likelihood of coverage.
    """
    # Test with digits
    password = generate_password(12, ["digits"])
    assert any(
        char in string.digits for char in password
    ), "Password should contain digits"

    # Test with uppercase
    password = generate_password(12, ["uppercase"])
    assert any(
        char in string.ascii_uppercase for char in password
    ), "Password should contain uppercase"

    # Test with lowercase
    password = generate_password(12, ["lowercase"])
    assert any(
        char in string.ascii_lowercase for char in password
    ), "Password should contain lowercase"

    # Test with special characters (basic set)
    basic_special = SPECIAL_CHAR_SETS["basic"]["chars"]
    password = generate_password(12, ["special"], basic_special)
    assert any(
        char in basic_special for char in password
    ), "Password should contain special characters"

    print("[PASS] Character type inclusion test passed")


def test_character_type_exclusion() -> None:
    """
    Test that generated password does NOT contain excluded character types.
    """
    # Generate password with only lowercase letters
    password = generate_password(20, ["lowercase"])
    # Check that no digits are present
    assert not any(
        char in string.digits for char in password
    ), "Password should not contain digits"
    # Check that no uppercase are present
    assert not any(
        char in string.ascii_uppercase for char in password
    ), "Password should not contain uppercase"

    print("[PASS] Character type exclusion test passed")


def test_special_character_exclusions() -> None:
    """
    Test that explicitly excluded special characters are not in the password.
    """
    # Use extended set but exclude specific characters
    extended = SPECIAL_CHAR_SETS["extended"]["chars"]
    excluded_chars = "~[]"
    filtered_chars = "".join(c for c in extended if c not in excluded_chars)

    password = generate_password(20, ["special"], filtered_chars)

    # Check that excluded characters are not present
    assert not any(
        char in excluded_chars for char in password
    ), f"Password should not contain excluded characters: {excluded_chars}"

    # Check that non-excluded characters from the set can appear
    assert any(
        char in filtered_chars for char in password
    ), "Password should contain characters from filtered set"

    print("[PASS] Special character exclusions test passed")


def test_special_character_presets() -> None:
    """
    Test that different special character presets work correctly.
    """
    basic = SPECIAL_CHAR_SETS["basic"]["chars"]
    extended = SPECIAL_CHAR_SETS["extended"]["chars"]
    full = SPECIAL_CHAR_SETS["full"]["chars"]

    # Test basic preset
    password_basic = generate_password(12, ["special"], basic)
    assert all(
        char in basic for char in password_basic
    ), "Basic password should only contain basic special chars"

    # Test extended preset
    password_extended = generate_password(12, ["special"], extended)
    assert all(
        char in extended for char in password_extended
    ), "Extended password should only contain extended special chars"

    # Test full preset
    password_full = generate_password(12, ["special"], full)
    assert all(
        char in full for char in password_full
    ), "Full password should only contain punctuation"

    print("[PASS] Special character presets test passed")


def test_special_without_special_chars() -> None:
    """
    Regression test: selecting 'special' without passing special_chars must
    not raise. It should fall back to the basic preset (see generate_password).
    """
    basic = SPECIAL_CHAR_SETS["basic"]["chars"]

    # No special_chars argument supplied alongside the 'special' type.
    password = generate_password(12, ["digits", "special"])

    # Must contain at least one basic special character (guaranteed inclusion).
    assert any(
        char in basic for char in password
    ), "Password should contain a basic special character from the fallback set"

    # Every special character present must come from the basic fallback set.
    specials_in_password = [
        char for char in password if char not in string.digits
    ]
    assert all(
        char in basic for char in specials_in_password
    ), "Special characters should only come from the basic fallback set"

    print("[PASS] Special-without-special_chars fallback test passed")


def test_excluded_characters_across_classes() -> None:
    """
    Cross-class exclusion: excluding look-alike characters that span digits
    and letters must remove them from the output while keeping every selected
    class represented.
    """
    excluded = "0O1lI"  # zero/oh, one/ell/eye look-alikes across three classes
    password = generate_password(
        30, ["digits", "uppercase", "lowercase"], excluded_chars=excluded
    )

    # None of the excluded characters may appear.
    assert not any(
        c in excluded for c in password
    ), f"Password should not contain excluded characters: {excluded}"

    # Each selected class is still represented after exclusion.
    assert any(c in string.digits for c in password), "Password should contain a digit"
    assert any(
        c in string.ascii_uppercase for c in password
    ), "Password should contain uppercase"
    assert any(
        c in string.ascii_lowercase for c in password
    ), "Password should contain lowercase"

    print("[PASS] Cross-class exclusion test passed")


def test_exclusion_emptying_class_raises() -> None:
    """
    Excluding every character of a selected class must fail loudly rather than
    silently dropping that class from the password.
    """
    raised = False
    try:
        # Exclude all 10 digits while 'digits' is a selected type.
        generate_password(12, ["digits", "lowercase"], excluded_chars=string.digits)
    except ValueError:
        raised = True

    assert raised, "Excluding an entire class should raise ValueError"
    print("[PASS] Exclusion-empties-class guard test passed")


def test_length_smaller_than_types_raises() -> None:
    """
    Contract guard: requesting fewer characters than selected types must raise,
    rather than silently returning a password longer than requested.
    """
    raised = False
    try:
        generate_password(2, ["digits", "uppercase", "lowercase"])
    except ValueError:
        raised = True

    assert raised, "length < number of types should raise ValueError"
    print("[PASS] Length-smaller-than-types guard test passed")


def test_entropy_estimate() -> None:
    """
    Entropy estimate must equal length * log2(pool_size) and report the correct
    unique-pool size, and strength labels must bucket bits sensibly.
    """
    # Lowercase only -> pool of 26 unique characters.
    bits, pool_size = estimate_entropy(10, ["lowercase"])
    assert pool_size == 26, f"Pool size should be 26, got {pool_size}"
    assert abs(bits - 10 * math.log2(26)) < 1e-9, "Entropy formula mismatch"

    # Exclusions shrink the pool.
    bits_excl, pool_excl = estimate_entropy(10, ["lowercase"], excluded_chars="abcde")
    assert pool_excl == 21, f"Pool size after exclusion should be 21, got {pool_excl}"
    assert bits_excl < bits, "Excluding characters should lower entropy"

    # Label boundaries.
    assert strength_label(10) == "Very weak"
    assert strength_label(30) == "Weak"
    assert strength_label(50) == "Moderate"
    assert strength_label(90) == "Strong"
    assert strength_label(200) == "Very strong"

    print("[PASS] Entropy estimate test passed")


def test_password_randomness() -> None:
    """
    Test that multiple generated passwords are different.
    Ensures the generator is actually random.
    """
    passwords = [
        generate_password(8, ["digits", "lowercase", "uppercase"]) for _ in range(10)
    ]

    # Check that not all passwords are identical
    assert len(set(passwords)) > 1, "Generated passwords should be different"

    print("[PASS] Password randomness test passed")


def run_tests() -> None:
    """Run all unit tests to verify password generator functionality."""
    print("\n" + "=" * 60)
    print("Running Unit Tests...")
    print("=" * 60 + "\n")

    try:
        test_password_length()
        test_character_type_inclusion()
        test_character_type_exclusion()
        test_special_character_exclusions()
        test_special_character_presets()
        test_special_without_special_chars()
        test_excluded_characters_across_classes()
        test_exclusion_emptying_class_raises()
        test_length_smaller_than_types_raises()
        test_entropy_estimate()
        test_password_randomness()
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return False

    return True


# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run tests first to verify functionality
    if run_tests():
        # If tests pass, run the main program
        input("\nPress Enter to start the Password Generator...")
        main()
