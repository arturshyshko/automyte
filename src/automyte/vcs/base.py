from __future__ import annotations

import abc
import contextlib
import typing as t
from pathlib import Path

from automyte.config import VCSConfig
from automyte.config.vcs import SupportedVCS
from automyte.discovery import File, Filter


class VCSException(Exception):
    """To be raised in case if any actual vcs cli command fails, or you want to interrupt automaton execution."""


class VCS(abc.ABC):
    """Class used for 2 purposes: providing means of local project state preservation
        and 'run' util for vcs cli interface

    'preserve_state' is a context manager which allows automatons not to interfere with a local working state
    of a project (if a dev was working on some feature - we don't want to simply discard the changes)

    'run' method basically accepts args as a bash executable array of commands to call any vcs command
    of arbitrary difficulty; it will call those commands inside project's current working dir.

    NOTE: VCS tasks in contrib or core utils are to rely on RunContext to get access to project rootdir and stuff
        and then call corresponding vcs commands or directly call 'run' method for any vcs command with flags, etc.
    """

    @contextlib.contextmanager
    def preserve_state(self, config: VCSConfig):
        raise NotImplementedError

    def run(self, *subcommand_with_flags):
        raise NotImplementedError


class VCSCmdBuilder:
    def __init__(self, vcs: SupportedVCS):
        self._vcs = vcs
        self._command = ""
        self._command_args = []
        self._dir = None

    def cmd(self, vcs_command: str):
        self._command = vcs_command
        return self

    def args(self, *args: str) -> "VCSCmdBuilder":
        self._command_args.extend(list(args))
        return self

    def in_dir(self, dir: Path | str) -> "VCSCmdBuilder":
        self._dir = str(dir)
        return self

    def to_cmd(self):
        result = [self._vcs]

        if self._dir:
            if self._vcs == "git":
                result.extend(["-C", self._dir])
            else:
                raise ValueError("Add support for new VCS systems.")

        result.append(self._command)
        result.extend(self._command_args)

        return result
