""" declarative config for app"""
from typing import Any, Optional

from basecfg import BaseCfg, opt


def upper(arg: Any) -> str:
    """typed wrapper around str.upper"""
    if not isinstance(arg, str):
        raise ValueError("expected a string input")
    return arg.upper()


class Config(BaseCfg):
    """declarative config class"""

    clean_dest: bool = opt(
        default=True,
        doc=(
            "before restoring database objects, issue commands to DROP all "
            "the objects that will be restored"
        ),
    )
    create_dest: bool = opt(
        default=True,
        doc=(
            "Create the database before restoring into it. If CLEAN_DEST is "
            "also specified, drop and recreate the target database before "
            "connecting to it."
        ),
    )
    job_count: Optional[int] = opt(
        default=None,
        doc=(
            "Run the most time-consuming steps of pg_restore — those that "
            "load data, create indexes, or create constraints — concurrently, "
            "using up to JOB_COUNT concurrent sessions"
        ),
    )

    log_level: str = opt(
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"),
        parser=upper,
        doc="log level to use when writing to the console",
    )
    log_dir: Optional[str] = opt(
        default=None,
        doc="directory in which to write log files",
    )

    source_host: str = opt(
        default="localhost",
        doc="network address of source database server",
    )
    source_port: int = opt(
        default=5432,
        doc="network port number of source database server",
    )
    source_username: str = opt(
        default="postgres",
        doc="username to use when authenticating with source database server",
    )
    source_password: str = opt(
        default="postgres",
        doc="password to use when authenticating with source database server",
    )
    source_name: str = opt(
        default="postgres",
        doc="name of database to connect to on the source database server",
    )

    dest_host: str = opt(
        default="dest",
        doc="network address of dest database server",
    )
    dest_port: int = opt(
        default=5432,
        doc="network port number of dest database server",
    )
    dest_username: str = opt(
        default="postgres",
        doc="username to use when authenticating with dest database server",
    )
    dest_password: str = opt(
        default="postgres",
        doc="password to use when authenticating with dest database server",
    )
    dest_name: str = opt(
        default="postgres",
        doc="name of database to connect to on the dest database server",
    )
