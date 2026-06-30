"""
Core password-generation logic.

This module is pure: importing it has no side effects, runs no prompts, and
prints nothing. Import these functions from another program to generate
passwords without the interactive CLI:

    from password_generator.core import generate_password, estimate_entropy
"""

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
