#!/usr/bin/env python3
"""
Command-line interface for MixedAssembly package.
Handles subcommands: remove-frameshifts, build-priors, run-mixed-assembly
"""
import argparse
import sys
from . import remove_frameshifts as rf
from . import build_priors as bp
from . import run_mixed_assembly as rma

def main(argv=None):
    """
    Entry point for the mixedassembly CLI.
    """
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="mixedassembly",
        description="MixedAssembly: tools for consensus sequence assembly and frameshift correction"
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="Available commands",
        dest="command",
        required=True
    )

    # ---- Subcommands ----
    subparsers.add_parser("remove-frameshifts", help="Remove frameshifts from an alignment")
    subparsers.add_parser("build-priors", help="Build priors parquet file")
    subparsers.add_parser("run-mixed-assembly", help="Run mixed assembly pipeline")

    # Parse hasta el primer subcomando, todo lo demás va como extra
    args, extra = parser.parse_known_args(argv)

    # Dispatch a la función main() de cada subcomando pasando extra
    if args.command == "remove-frameshifts":
        sys.exit(rf.main(extra))
    elif args.command == "build-priors":
        sys.exit(bp.main(extra))
    elif args.command == "run-mixed-assembly":
        sys.exit(rma.main(extra))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
