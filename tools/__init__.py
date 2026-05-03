"""homecoming-build-companion tools package.

Python migrations of the prior PowerShell scripts plus new validators and
utilities. Each subpackage is a self-contained tool with its own CLI entry
point at ``tools.<package>.__main__``.

Tooling layout:
    tools/_lib/         Shared helpers (frontmatter parsing, paths, etc.)
    tools/<tool>/       One package per migrated script or new tool
        main.py         Pure-logic functions (testable)
        __main__.py     CLI wrapper (parses argv, calls main)
        tests/          Co-located pytest suite + fixtures
"""
