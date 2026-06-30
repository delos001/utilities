# Password Generator

Creates compliant, cryptographically secure passwords. You pick the length and
character types, optionally exclude specific characters (like look-alikes 0/O or
1/l/I), and it generates one or many passwords with a strength estimate.

## How to run it

Important: this is a Python **package**, not a single script. You **cannot** run
it by opening a `.py` file and clicking the Run / play button. That button runs
one file by itself, which breaks the package's internal imports. There are
exactly two ways that work.

### Option 1: PowerShell

Open a terminal in the **`utilities`** folder (the one that *contains*
`password_generator`), then run:

```powershell
python -m password_generator
```

Note the `-m` and that there is **no `.py`**. You run the package by name, not a
file. Don't `cd` into the `password_generator` folder first; run it from the
parent (`utilities`), or Python won't find it.

### Option 2: VS Code (press F5)

1. Open the **`utilities`** folder in VS Code (File > Open Folder). Open the
   parent folder, **not** `password_generator` itself.
2. Press **F5**.

You do not open or run the `launch.json` file yourself. VS Code reads it
automatically, and that is what F5 uses. (Opening `launch.json` and pressing F5
is what causes the confusing "JSON with comments" error.)

### What happens either way

1. It runs its own tests (you'll see `[PASS]` lines).
2. You press Enter to start.
3. It asks for length, character types, an optional special-character preset,
   and any characters to exclude.
4. It asks how many passwords you want, then shows them plus a strength rating.
5. It offers to generate more with the same settings, or quit.

## Features

- Length from 4 to 128 characters
- Any mix of numbers, uppercase, lowercase, and special characters
- Three special-character presets (Basic, Extended, Full)
- Exclude any specific characters across all selected types (e.g. look-alikes),
  with a guard that won't let you empty an entire character class
- Guarantees at least one character from each selected type
- Cryptographically secure (uses Python's `secrets` module)
- Generates single passwords or batches, with a strength estimate

## Using the generator in your own code

The generation logic lives in `core.py` and has no prompts or printing, so you
can import it without launching the interactive app. From the `utilities`
folder (or with it on your path):

```python
from password_generator import generate_password, estimate_entropy, strength_label

# A 20-character password with all four character types
pw = generate_password(20, ["digits", "uppercase", "lowercase", "special"])

# Exclude look-alikes, letters only
pw = generate_password(16, ["uppercase", "lowercase"], excluded_chars="0O1lI")

# Estimate strength for a given configuration
bits, pool_size = estimate_entropy(20, ["digits", "lowercase"])
label = strength_label(bits)   # e.g. "Very strong"
```

Valid character type keys: `"digits"`, `"uppercase"`, `"lowercase"`, `"special"`.

For a flat, copy-paste reference covering this plus launching the app and
running the tests, see [`example_usage.py`](example_usage.py).

## Files

| File | Purpose |
|------|---------|
| `core.py` | Pure generation logic and data. No input/output. Import this to reuse. |
| `cli.py` | Interactive prompts and the `main()` flow. |
| `tests.py` | Unit tests (`python -m password_generator.tests`). |
| `__main__.py` | Entry point that runs tests then launches the CLI. |
| `__init__.py` | Exposes the public functions for import. |
| `example_usage.py` | Copy-paste reference for using the package from your own code. |

## Requirements

Python 3.9+ (standard library only; nothing to install). See `requirements.txt`.
