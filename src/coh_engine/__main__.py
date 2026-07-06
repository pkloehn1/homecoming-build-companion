"""CLI entry point: ``python -m coh_engine``.

The registries are code; this is the thin execution surface a build run touches
(.claude/rules/check-registry.md § Execution during build). ``rules`` lists the
registered legality rules + scoring metrics — the introspectable registry. The
``validate``/``score`` subcommands (running the registries over a loaded build) land
with the build-evaluation pipeline that wires the engine modules together.
"""

import argparse
import sys
from collections.abc import Sequence

from coh_engine.legality import registered_rules
from coh_engine.scoring import registered_metrics


def _print_rules() -> None:
    print("legality rules (a new dimension is a new @legality_rule):")
    for name in registered_rules():
        print(f"  {name}")
    print("scoring metrics (a new metric is a new @metric):")
    for name in registered_metrics():
        print(f"  {name}")


def main(argv: Sequence[str] | None = None) -> int:
    """Dispatch the CLI. ``rules`` introspects the registries; no args prints status."""
    parser = argparse.ArgumentParser(prog="coh_engine", description="MidsReborn build-math port.")
    parser.add_subparsers(dest="command").add_parser("rules", help="list the registered legality rules + metrics")
    args = parser.parse_args(argv)

    if args.command == "rules":
        _print_rules()
        return 0
    print("coh_engine: MidsReborn build-math port.")
    print("Spec: docs/engine/mids-port-spec.md. Commands: rules (validate/score land with the build-eval pipeline).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
