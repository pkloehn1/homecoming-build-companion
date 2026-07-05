"""CLI entry point: ``python -m coh_engine``."""

import sys


def main() -> int:
    """Print engine status. Real subcommands land with CP2+ (calc, validate, ingest)."""
    print("coh_engine: MidsReborn build-math port (CP1 scaffold).")
    print("Spec: docs/engine/mids-port-spec.md. Reference: MidsReborn golden fixtures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
