import enum
import os
import sys
import typing as t


@t.final
class ExitCode(enum.IntEnum):
    OK = 0
    MIGRATION_FAILED = 1


def main() -> ExitCode:
    return ExitCode.OK


def console_main() -> int:
    """The CLI entry point of automyte.

    This function is not meant for programmable use; use `main()` instead.
    """
    # https://docs.python.org/3/library/signal.html#note-on-sigpipe
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 1  # Python exits with error code 1 on EPIPE
    else:
        return code
