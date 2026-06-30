"""
Reference: how to use the password_generator package from your own script.

This is a guide, not something you need to run. Copy the lines you need into
your own code. It assumes the package is importable, which it is once it has
been pip-installed (done, in the `agents` env) or run from a folder that has
`password_generator` on the path.
"""

from password_generator import generate_password, estimate_entropy, strength_label

# === Option 1: use the engine directly (runs top to bottom) ===
length = 20
types = ["digits", "uppercase", "lowercase", "special"]
exclude = "0O1lI"          # look-alikes to skip; set to "" for none

password = generate_password(length, types, excluded_chars=exclude)
print("Password:", password)

bits, pool = estimate_entropy(length, types, excluded_chars=exclude)
print("Strength:", strength_label(bits), f"(~{bits:.0f} bits, pool {pool})")


# === Option 2: launch the interactive app ===
# Uncomment these two lines to start the full prompt flow instead.
# from password_generator.cli import main
# main()

# === Option 3: run the package's unit tests ===
# Uncomment these two lines to run the bundled test suite.
# from password_generator.tests import run_tests
# run_tests()
