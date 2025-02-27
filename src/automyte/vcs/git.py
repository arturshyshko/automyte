from __future__ import annotations

import contextlib
import hashlib  # TODO: Move this to utils or smth.
import typing as t
import uuid
from pathlib import Path

from automyte.config import VCSConfig
from automyte.discovery import File, Filter
from automyte.utils import bash
from automyte.utils.random import random_hash

from .base import VCS


# TODO: Figure out authentication.
# TODO: Setup proper implementations when splitting into files. (probably use builder pattern for commands, like lazygit)
class Git(VCS):
    def __init__(
        self,
        rootdir: str,
        preferred_workflow: t.Literal["rebase", "merge"] = "rebase",
        remote: str
        | None = "origin",  # TODO: Figure out how to work properly with remote, like validation, origin/custom_name, check if it's been setup and stuff.
    ) -> None:
        self.preferred_workflow = preferred_workflow
        self.remote = remote
        self.original_rootdir = rootdir
        self.workdir = rootdir

    def switch(self, to: str) -> "Git":
        # TODO: Handle the case for when the branch already exists.
        bash.execute(["git", "-C", f"{self.workdir}", "switch", "-c", "{to}", "2>/dev/null"])
        return self

    def add(self, path: str | Path | File | Filter) -> "Git":
        bash.execute(["git", "-C", f"{self.workdir}", "add", f"{path}"])
        return self

    def commit(self, msg: str) -> "Git":
        bash.execute(["git", "-C", f"{self.workdir}", "commit", "-m", f'"{msg}"'])
        return self

    def pull(self, branch: str) -> "Git":
        if self.preferred_workflow == "rebase":
            bash.execute(["git", "-C", f"{self.workdir}", "pull", "--rebase", f"{self.remote}", f"{branch}"])
        else:
            bash.execute(["git", f"-C{self.workdir}", "pull", f"{self.remote}", f"{branch}"])

        return self

    def assure_remote(self) -> "Git":
        """Function to make sure remote is present - either create one or check if it exists, throw error otherwise."""
        # TODO: Implement
        return self

    def push(self, to: str) -> "Git":
        bash.execute(["git", "-C", f"{self.workdir}", "push", "--force-with-lease", "origin", f"{to}"])
        return self

    # TODO: Think on how this should be implemented.
    def pr(self, create: bool) -> None:
        raise NotImplementedError

    def run(self, subcommand: str):
        return bash.execute(["git", "-C", f"{self.workdir}", subcommand])

    @contextlib.contextmanager
    def preserve_state(self, config: VCSConfig):
        if config.dont_disrupt_prior_state:
            # TODO: Maybe add a check if a work_branch already exists in run mode, then have to process this somehow, as worktree will not be created?
            relative_worktree_path = f"./auto_{random_hash()}"
            bash.execute(
                [
                    "git",
                    "-C",
                    self.original_rootdir,
                    "worktree",
                    "add",
                    "-b",
                    f"{config.work_branch}",
                    relative_worktree_path,
                ]
            )

            self.workdir = Path(self.original_rootdir) / relative_worktree_path
            yield str(self.workdir)

            bash.execute(["git", "-C", self.original_rootdir, "worktree", "remove", "-f", relative_worktree_path])

        else:
            yield self.original_rootdir
