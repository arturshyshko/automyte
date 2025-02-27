from __future__ import annotations

import abc
import contextlib
import typing as t
from pathlib import Path

from automyte.config import VCSConfig
from automyte.discovery import File, Filter


class VCS(abc.ABC):
    """NOTE: VCS operations are to rely on RunContext to get access to project rootdir and stuff."""

    def switch(self, to: str) -> "VCS":
        raise NotImplementedError

    def add(self, path: str | Path | File | Filter) -> "VCS":
        raise NotImplementedError

    def commit(self, msg: str) -> "VCS":
        raise NotImplementedError

    def pull(self, branch: str) -> "VCS":
        """Mode to be configured in init of the specific implementation."""
        raise NotImplementedError

    def assure_remote(self) -> "VCS":
        """Function to make sure remote is present - either create one or check if it exists, throw error otherwise."""
        raise NotImplementedError

    def push(self, to: str) -> "VCS":
        raise NotImplementedError

    # TODO: Think on how this should be implemented.
    def pr(self, create: bool) -> None:
        raise NotImplementedError

    # Will be using worktrees for git. Think if need to return smth?
    @contextlib.contextmanager
    def preserve_state(self, config: VCSConfig):
        raise NotImplementedError

    def run(self, subcommand):
        raise NotImplementedError
