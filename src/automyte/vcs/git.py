from __future__ import annotations

# TODO: Switch logger message with errors, not to polute history?
import contextlib
import hashlib  # TODO: Move this to utils or smth.
import logging
import typing as t
import uuid
from pathlib import Path

from automyte.config import VCSConfig
from automyte.discovery import File, Filter
from automyte.utils import bash
from automyte.utils.random import random_hash

from .base import VCS, VCSCmdBuilder, VCSException

logger = logging.getLogger(__name__)


class Git(VCS):
    def __init__(
        self,
        rootdir: str,
        preferred_workflow: t.Literal["rebase", "merge"] = "rebase",
        remote: str = "origin",
    ) -> None:
        self.preferred_workflow = preferred_workflow
        self.remote = remote
        self.original_rootdir = rootdir
        self.workdir = rootdir

    def run(self, *subcommand_with_flags: str):
        return self._exec(subcommand_with_flags[0], *subcommand_with_flags[1:])

    @contextlib.contextmanager
    def preserve_state(self, config: VCSConfig):
        if config.dont_disrupt_prior_state:
            relative_worktree_path = f"./auto_{random_hash()}"
            result = bash.execute(
                VCSCmdBuilder("git")
                .cmd("worktree")
                .in_dir(self.original_rootdir)
                .args("add", "-b", config.work_branch)
                .args(relative_worktree_path)
                .to_cmd()
            )
            if result.status == "fail":
                logger.error(
                    "[Git]: Failed to create worktree at %s for %s branch:\n%s",
                    relative_worktree_path,
                    config.work_branch,
                    result.output,
                )
                raise VCSException("[Git]: Failed to create worktree")

            self.workdir = str(Path(self.original_rootdir) / relative_worktree_path)
            yield str(self.workdir)

            result = bash.execute(
                VCSCmdBuilder("git")
                .cmd("worktree")
                .in_dir(self.original_rootdir)
                .args("remove", "-f", relative_worktree_path)
                .to_cmd()
            )
            if result.status == "fail":
                logger.warning("[Git]: Failed to remove worktree %s:\n%s", relative_worktree_path, result.output)
            self.workdir = self.original_rootdir

        else:
            yield self.original_rootdir

    def _exec(self, cmd: str, *flags: str):
        return bash.execute(VCSCmdBuilder("git").cmd(cmd).in_dir(self.workdir).args(*flags).to_cmd())
