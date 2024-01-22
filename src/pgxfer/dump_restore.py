""" prime shell-out stuff"""
import logging
from subprocess import PIPE, STDOUT, CalledProcessError, Popen  # nosec: considered

from .config import Config

logger = logging.getLogger(__name__)


def pg_xfer(config: Config) -> bool:
    """pipe between pg_dump and pg_restore"""

    with (
        Popen(
            ("/usr/bin/pg_dump", "--format=custom"),
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
        ) as src,
        Popen(
            ("/usr/bin/pg_restore", "--format=custom", f"--dbname={config.dest_name}"),
            stdin=src.stdout,
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
        ) as dest,
    ):
        if src.stdout is not None:
            src.stdout.close()  # allow src to receive a SIGPIPE if dest exits
        dest_stdout, _ = dest.communicate()
        src.wait()  # Make sure src has finished

        # Log and handle src stderr & exitcode
        if src.stderr is None:
            raise RuntimeError("src.stderr is invalid")
        src_stderr = src.stderr.read()
        if src_stderr:
            logger.error("pg_dump stderr: %s", src_stderr)
        if src.returncode != 0:
            logger.error(
                "pg_dump non-zero exit (%s); stderr: %s",
                src.returncode,
                src_stderr,
            )
            raise CalledProcessError(
                src.returncode,
                src.args,
                stderr=src_stderr,
            )

        # Log and handle dest stdout, stderr & exitcode
        if dest_stdout:
            logger.info("pg_restore stdout: %s", dest_stdout)
        if dest.returncode != 0:
            logger.error(
                "pg_restore non-zero exit (%s); stderr: %s",
                dest.returncode,
                dest_stdout,
            )
            raise CalledProcessError(
                dest.returncode,
                dest.args,
                output=dest_stdout,
            )

    return src.returncode == 0 and dest.returncode == 0
