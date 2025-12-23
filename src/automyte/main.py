import enum
import logging
import os
import sys
import typing as t
from argparse import Namespace

from ._cmd import AutomyteArgParser, execute_automaton, find_automaton_module

logger = logging.getLogger(__name__)


@t.final
class ExitCode(enum.IntEnum):
    OK = 0
    AUTOMATON_FAILED = 1


def main(args: Namespace) -> ExitCode:
    try:
        execute_automaton(find_automaton_module(args))
    except Exception as e:
        logger.error(e)
        return ExitCode.AUTOMATON_FAILED

    return ExitCode.OK


def console_main() -> int:
    """The CLI entry point of automyte.

    This function is not meant for programmable use; use `main()` instead.
    """
    # https://docs.python.org/3/library/signal.html#note-on-sigpipe
    try:
        os.environ["AUTOMYTE_CLI_MODE"] = "true"
        args = AutomyteArgParser.parse_args()
        exit_code = main(args)
        sys.stdout.flush()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 1  # Python exits with error code 1 on EPIPE
    else:
        return exit_code
