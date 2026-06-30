

Main Script: password_generator.py

Key Features:

1. User-Friendly Input Flow
  - Asks for password length (4-128 characters) with clear descriptions
  - Displays all 4 character type options with examples before asking for selection
  - Allows users to choose any combination of character types
  - If special characters are selected, presents 3 preset options (Basic, Extended, Full)
  - Offers a single exclusion step to remove specific characters from any selected type
    (digits, letters, and special), e.g. look-alikes like 0/O or 1/l/I
  - Generates one or many passwords per batch, and offers more rounds with the
    same settings without restarting
  - Reports an estimated strength (bits of entropy) for the chosen settings

2. Character Types Available
  - Numbers (0-9)
  - Uppercase letters (A-Z)
  - Lowercase letters (a-z)
  - Special characters with 3 presets:
    * Basic: !@#$%^&*
    * Extended: Basic + ()[]{}+-=.,:;|/<>_~?
    * Full: Basic + Extended + "'`\

3. Character Customization & Exclusions
  - Users can select any of the 3 preset special character sets
  - A single exclusion step then applies across every selected type, not just special
  - This allows optimization: e.g., select Extended but exclude ~, or strip
    look-alike digits/letters (0/O, 1/l/I) that some systems or users disallow
  - Exclusions that would empty an entire selected class are rejected
  - Maximizes password strength within system constraints

4. Robust Error Handling
  - Invalid length selection: loops until valid choice (4-128)
  - Invalid character type selection: validates numeric input
  - Prevents duplicate selections
  - Requires at least one character type selected
  - Validates character exclusions and rejects emptying a whole class
  - Guards the generator contract: a length smaller than the number of selected
    types raises an error instead of silently over-generating
  - All error messages use clear, non-technical language

5. Code Quality
  - Each function has a docstring explaining its purpose
  - Inline comments explain what each code section does
  - Type hints for function parameters and returns
  - Modular design with separate functions for each responsibility

6. Unit Tests (11 Total)
  - Password length test: Verifies correct length generation
  - Character type inclusion test: Ensures selected types appear in password
  - Character type exclusion test: Confirms unselected types don't appear
  - Special character exclusions test: Validates excluded chars are not in password
  - Special character presets test: Verifies preset functionality works correctly
  - Special-without-special_chars test: Confirms the basic-preset fallback when no set is passed
  - Cross-class exclusion test: Confirms look-alike exclusions span digits and letters
  - Exclusion-empties-class guard test: Confirms emptying a whole class raises an error
  - Length-smaller-than-types guard test: Confirms the generator contract is enforced
  - Entropy estimate test: Confirms the entropy formula, pool sizing, and strength labels
  - Randomness test: Validates that multiple passwords are different
  - Uses the secrets module (CSPRNG) for cryptographically secure generation
  - All tests passed successfully

How to Use

Run the script with:
python password_generator.py

It will:
1. Run all unit tests automatically (you'll see [PASS] messages)
2. Prompt you to press Enter to start
3. Ask for password length
4. Display available character types with examples
5. Ask which types to include
6. If special characters selected, choose a preset (Basic, Extended, or Full)
7. Optionally exclude specific characters from any selected type (e.g. look-alikes)
8. Choose how many passwords to generate (press Enter for 1)
9. Display the password(s) plus an estimated strength
10. Offer to generate more with the same settings, or quit
