#!/usr/bin/env python3
"""
FoxIntel - Professional OSINT Intelligence Gathering Tool
Entry Point
"""

import argparse
import sys
from cli.parser import create_parser
from cli.runner import CommandRunner
from core.config import Config
from core.logger import setup_logger
from core.exceptions import FoxIntelError


def main():
    try:
        parser = create_parser()
        args = parser.parse_args()

        if args.command is None:
            parser.print_help()
            sys.exit(0)

        config = Config.from_args(args)
        logger = setup_logger(config.debug, config.output_format if config.output_format else 'text')
        runner = CommandRunner(config, logger)

        success = runner.execute(args)
        sys.exit(0 if success else 1)

    except FoxIntelError as e:
        print(f"FoxIntel Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if '--debug' in sys.argv or '-d' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()