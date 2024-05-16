"""prime shell-out stuff"""

import logging
import os
import shlex
import threading
from subprocess import PIPE, STDOUT, Popen, check_output  # nosec: considered
from typing import TYPE_CHECKING, Final, List, Literal

from .config import Config

logger = logging.getLogger(__name__)

DROPDB_BIN: Final = "/usr/bin/dropdb"
CREATEDB_BIN: Final = "/usr/bin/createdb"
PGDUMP_BIN: Final = "/usr/bin/pg_dump"
PGRESTORE_BIN: Final = "/usr/bin/pg_restore"


def log_output(stream, logger_method):
    """Reads from stream line by line and logs using the provided logger method."""
    try:
        for line in iter(stream.readline, ""):
            logger_method(line.rstrip("\n"))
    finally:
        stream.close()


def drop_dest_db(config: Config):
    """call the dropdb command on the destination database"""
    libpq_cmd(config, "dest", [DROPDB_BIN, "--if-exists", config.dest_name])


def create_dest_db(config: Config) -> None:
    """create the destination database from template0"""
    libpq_cmd(config, "dest", [CREATEDB_BIN, "-T", "template0", config.dest_name])


def libpq_cmd(
    config: Config,
    db_selection: Literal["source", "dest"],
    cmd: List[str],
) -> None:
    """execute an external command with the selected set of libpq envvars"""
    # https://www.postgresql.org/docs/current/libpq-envars.html
    logger.debug("running %s", " ".join([shlex.quote(word) for word in cmd]))
    cmd_output = check_output(  # nosec: filtered input
        cmd,
        env=config.libpq_env(db_selection),
        stderr=STDOUT,
        encoding="utf8",
        errors="strict",
    )
    if cmd_output:
        logger.debug("%s: %s", os.path.basename(cmd[0]), cmd_output)


def pg_xfer(config: Config) -> bool:
    """pipe between pg_dump and pg_restore"""

    dump_cmd = [PGDUMP_BIN, "--format=custom", "--verbose"]
    restore_cmd = [
        PGRESTORE_BIN,
        "--format=custom",
        "--verbose",
        "--verbose",
        f"--dbname={config.dest_name}",
    ]
    if config.clean_dest:
        restore_cmd.append("--clean")
    if config.init_dest:
        drop_dest_db(config)
        create_dest_db(config)
    if not config.owner:
        restore_cmd.append("--no-owner")
    if not config.acl:
        restore_cmd.append("--no-acl")

    logger.debug("pg_dump command: %s", " ".join(dump_cmd))
    dump = Popen(
        dump_cmd,
        stdout=PIPE,
        stderr=PIPE,
        shell=False,  # nosec: no untrusted inputs
        env=config.libpq_env("source"),
        encoding="utf8",
        errors="strict",
    )

    logger.debug("pg_restore command: %s", " ".join(restore_cmd))
    restore = Popen(
        restore_cmd,
        stdin=dump.stdout,
        stdout=PIPE,
        stderr=STDOUT,
        shell=False,  # nosec: no untrusted inputs
        env=config.libpq_env("dest"),
        encoding="utf8",
        errors="strict",
    )

    if TYPE_CHECKING:
        assert dump.stdout is not None
        assert dump.stderr is not None

    # Start a thread to log pg_dump stderr output in real-time
    dump_logger_thread = threading.Thread(
        target=log_output,
        args=(dump.stderr, logger.debug),
        daemon=True,
    )

    # Start a thread to log pg_restore stdout/stderr output in real-time
    restore_logger_thread = threading.Thread(
        target=log_output,
        args=(restore.stdout, logger.debug),
        daemon=True,
    )

    dump_logger_thread.start()
    restore_logger_thread.start()

    # result: bool = False

    with dump, restore:
        dump.stdout.close()  # allow dump to receive a SIGPIPE if restore exits
        logger.info("starting dump/restore process...")

        # Wait for the threads to finish
        dump.wait()
        restore.wait()
        dump_logger_thread.join()
        restore_logger_thread.join()

        # check the pipeline in reverse order starting with restore
        if restore.returncode != 0:
            logger.error(
                "pg_restore non-zero exit %s; (pg_dump exit: %s)",
                restore.returncode,
                dump.returncode,
            )
            raise RuntimeError(
                restore.returncode,
                restore.args,
            )

        # check the dump process
        if dump.returncode != 0:
            logger.error("pg_dump non-zero exit (%s)", dump.returncode)
            raise RuntimeError(dump.returncode, dump.args)

        result = dump.returncode == 0 and restore.returncode == 0

    logger.info("dump/restore process complete")
    return result
