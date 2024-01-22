#!/usr/bin/env python3
""" utility """

import sys

import baselog

from .config import Config
from .dump_restore import pg_xfer


def main() -> int:
    """
    entrypoint for direct execution; returns an integer suitable for use with sys.exit
    """
    config = Config(
        prog=__package__,
        prog_description="util for running pgdump between postgres instances",
    )
    logger = baselog.BaseLog(
        root_name=__package__,
        log_dir=config.log_dir,
        console_log_level=config.log_level,
    )
    config.logcfg(logger)

    pg_xfer(config)

    return 0


if __name__ == "__main__":
    sys.exit(main())
