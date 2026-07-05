"""CLI entry point: ``python -m coh_engine``."""

import sys


def main() -> int:
    """Print engine status. Real subcommands (calc, validate, ingest) land as they are built."""
    print("coh_engine: MidsReborn build-math port.")
    print("Spec: docs/engine/mids-port-spec.md. Reference: MidsReborn golden fixtures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
