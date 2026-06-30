"""
password_generator: create compliant, cryptographically secure passwords.

Public API for reuse in other programs:

    from password_generator import generate_password, estimate_entropy, strength_label

    pw = generate_password(20, ["digits", "uppercase", "lowercase", "special"])
    bits, pool = estimate_entropy(20, ["digits", "lowercase"])
    label = strength_label(bits)

To run the interactive app instead, see __main__.py (python -m password_generator).
"""

from .core import (
    CHARACTER_TYPES,
    SPECIAL_CHAR_SETS,
    estimate_entropy,
    generate_password,
    strength_label,
)

__all__ = [
    "generate_password",
    "estimate_entropy",
    "strength_label",
    "CHARACTER_TYPES",
    "SPECIAL_CHAR_SETS",
]
