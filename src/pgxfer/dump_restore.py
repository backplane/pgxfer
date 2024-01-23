""" prime shell-out stuff"""
import logging
from subprocess import PIPE, STDOUT, CalledProcessError, Popen  # nosec: considered
from typing import TYPE_CHECKING

from .config import Config

logger = logging.getLogger(__name__)


def pg_xfer(config: Config) -> bool:
    """pipe between pg_dump and pg_restore"""

    dump_cmd = [
        "/usr/bin/pg_dump",
        "--format=custom",
    ]

    restore_cmd = [
        "/usr/bin/pg_restore",
        "--format=custom",
        f"--dbname={config.dest_name}",
    ]
    if config.clean_dest:
        restore_cmd.append("--clean")
        restore_cmd.append("--if-exists")
    if config.create_dest:
        restore_cmd.append("--create")
    if config.job_count:
        restore_cmd.append(f"--jobs={config.job_count}")

    dump = Popen(
        dump_cmd,
        stdout=PIPE,
        stderr=PIPE,
        shell=False,  # nosec: no untrusted inputs
        env={
            "PGHOST": config.source_host,
            "PGPORT": str(config.source_port),
            "PGUSER": config.source_username,
            "PGPASSWORD": config.source_password,
            "PGDATABASE": config.source_name,
        },
        encoding="utf8",
        errors="strict",
    )
    restore = Popen(
        restore_cmd,
        stdin=dump.stdout,
        stdout=PIPE,
        stderr=STDOUT,
        shell=False,  # nosec: no untrusted inputs
        env={
            "PGHOST": config.dest_host,
            "PGPORT": str(config.dest_port),
            "PGUSER": config.dest_username,
            "PGPASSWORD": config.dest_password,
            "PGDATABASE": config.dest_name,
        },
        encoding="utf8",
        errors="strict",
    )

    if TYPE_CHECKING:
        assert dump.stdout is not None
        assert dump.stderr is not None

    result: bool = False

    with dump, restore:
        dump.stdout.close()  # allow src to receive a SIGPIPE if dest exits
        logger.info("starting dump/restore process...")
        restore_output, _ = restore.communicate()  # stdout + stderr combined
        dump.wait()  # Make sure src has finished
        dump_stderr = dump.stderr.read()

        # check the pipeline in reverse order starting with restore
        if restore.returncode != 0:
            logger.error(
                "pg_restore non-zero exit (%s); output: %s",
                restore.returncode,
                restore_output,
            )
            # knowing the status of the dump command may be helpful as well...
            logger.info("pg_dump exit: %s; stderr: %s", dump.returncode, dump_stderr)
            raise CalledProcessError(
                restore.returncode,
                restore.args,
                output=restore_output,
            )
        if restore_output:
            logger.info("pg_restore output: %s", restore_output)

        # check the dump process
        if dump.returncode != 0:
            logger.error(
                "pg_dump non-zero exit (%s); stderr: %s",
                dump.returncode,
                dump_stderr,
            )
            raise CalledProcessError(dump.returncode, dump.args, stderr=dump_stderr)
        if dump_stderr:
            logger.error("pg_dump stderr: %s", dump_stderr)

        result = dump.returncode == 0 and restore.returncode == 0

    logger.info("dump/restore process complete")
    return result
