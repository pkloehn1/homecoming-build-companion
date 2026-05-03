# Rule: Python conventions

**Status:** MUST. Applies to every Python file authored or edited in this project.

This project is Python-first. New tooling, validators, and migrations are written in Python. PowerShell remains only for legacy scripts under `tools/` until the Phase 3 migration replaces them.

## Baseline

- **Python 3.14+ required.** No support for older versions.
- **Layout:** `src/<package>/` with co-located `tests/` directory; or `tools/<package>/<entrypoints>.py` with `tools/<package>/tests/` for thin tools.
- **CLI entry:** `__main__.py` so packages run as `python -m <package>`.
- **Imports:** absolute within the project; relative within a package only when traversing siblings.

## Linting and formatting

Use **ruff** for both lint and format. Match `repo-template`'s ruff config, adapted to py314:

- `line-length = 120`
- `target-version = "py314"`
- Lint rules selected: `E, W, F, I, B, C4, UP, SIM, N, D, RUF`
- Ignored: `E501` (handled by formatter), `SIM108`, `D100`-`D103`, `D107` (phased docstring rollout)
- `pydocstyle` convention: `google`
- Format quote style: `double`, indent `space`, line ending `lf`

Pylint is disabled — ruff is the sole linter.

## Type checking

**mypy** with `warn_return_any = true` and `warn_unused_configs = true`. `python_version = "3.14"`. Strict-leaning but not maximally strict; favor practical over pedantic.

## Testing — TDD mandatory

- **Write the failing test first.** Confirm it fails for the right reason before implementing.
- **100% coverage target.** `pytest --cov=<package> --cov-fail-under=100` in CI; coverage drops fail the build.
- **pytest** is the test runner. `python_files = ["test_*.py"]`, `python_functions = ["test_*"]`.
- **Co-locate tests** with the package under `tests/` immediately adjacent.
- **Fixtures live in `tests/fixtures/`** and are referenced by `conftest.py`.
- For each rule or unit of logic: author one passing fixture and one violating fixture, then write the test that exercises both.

Test discipline applies to **non-trivial logic**. Trivial wrappers (CLI plumbing, dataclass definitions) don't need bespoke tests but must be covered by integration tests that exercise them end-to-end.

## Pre-commit hooks

`.pre-commit-config.yaml` runs:

- `ruff check --fix`
- `ruff format`
- `mypy`

Hooks fail the commit on any violation. Hook bypassing (`--no-verify`) is **not** an option without explicit user direction.

## Make targets

Mirror `repo-template`'s Makefile structure. Every Python tool package supports:

- `make lint` — ruff check + format check
- `make fix` — ruff check --fix + ruff format
- `make test` — pytest with short tracebacks, no coverage
- `make cov` — pytest with coverage report and `--cov-fail-under=100`

VENV detection auto-handles Linux (`.venv/bin/`) vs Windows (`.venv/Scripts/`).

## Anti-patterns to reject

- `print()` debugging in landed code — use logging or remove.
- Global mutable state in rule modules — every check function is pure: `(build, canonical) -> list[Violation]`.
- Error-as-tradeoff conflation: errors get fixed, not disclosed in trade-offs sections.
- Bare `except:` — name the exception class.
- Untyped public function signatures — type-annotate every public function and method.

## Reference

- [`docs/repository-standards/style-guides/python-style-guide.md`](../../docs/repository-standards/style-guides/python-style-guide.md) — full canonical Python style guide imported from repo-template. This rule is the auto-loaded summary; that doc is the SSOT for detailed conventions.
- [`error-output.md`](./error-output.md) — diagnostic message standard for tool output.
- [`c:/Users/petek/repos/repo-template/pyproject.toml`](../../../repo-template/pyproject.toml) — origin of the ruff/mypy/pytest config adapted here to py314.
- [`c:/Users/petek/repos/repo-template/Makefile`](../../../repo-template/Makefile) — make-target template.
