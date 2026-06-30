"""
Unit tests for the password generator core logic.

Run directly with:  python -m password_generator.tests
They also run automatically before the CLI starts (see __main__.py).
"""

import math
import string

from .core import (
    SPECIAL_CHAR_SETS,
    estimate_entropy,
    generate_password,
    strength_label,
)


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
    Test that generated password does NOT contain unselected character types.
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


def run_tests() -> bool:
    """Run all unit tests. Returns True if all passed, False otherwise."""
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


if __name__ == "__main__":
    import sys

    sys.exit(0 if run_tests() else 1)
