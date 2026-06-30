# utilities

A home for finished, standalone scripts that actually do something.

Each subfolder is a self-contained utility with its own README. These are
not experiments (those live in the sandbox); they are tools that are
complete and usable as-is.

## Contents

| Utility | Description |
|---------|-------------|
| [password_generator](password_generator/) | Interactive generator for compliant, cryptographically secure passwords with selectable character types, cross-class exclusions, strength estimates, and batch generation. |

## Installing (optional, lets you import the tools from anywhere)

By default you can use a tool only from this `utilities` folder (so Python can
find it). To import the packages from any script, anywhere, install the
collection once in editable mode. From this folder:

```powershell
pip install -e .
```

After that, `import password_generator` works from any folder and any script,
with no path setup. "Editable" means it points at these files in place, so your
edits take effect immediately without reinstalling.

Each tool folder that is a Python package becomes its own importable top-level
package (e.g. `import password_generator`). Adding a new tool later needs no
changes to `pyproject.toml`.

## Using a tool from your own script

See [`password_generator/example_usage.py`](password_generator/example_usage.py)
for a reference showing the three ways to use `password_generator` from your own
code: calling the generator functions directly, launching its interactive app,
and running its tests.
