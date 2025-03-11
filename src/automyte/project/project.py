from __future__ import annotations

import contextlib
import typing as t
from pathlib import Path
from urllib.parse import urlparse

from automyte.config import Config
from automyte.discovery import LocalFilesExplorer, ProjectExplorer
from automyte.utils.filesystem import parse_dir
from automyte.utils.random import random_hash
from automyte.vcs import VCS, Git


class Project:
    def __init__(
        self,
        project_id: str | None = None,
        rootdir: str | None = None,
        explorer: ProjectExplorer | None = None,
        vcs: VCS | None = None,
    ):
        if not rootdir and not explorer:
            raise ValueError("Need to supply at least one of: rootdir | explorer")
        if rootdir:
            rootdir = str(parse_dir(rootdir))

        self.explorer = explorer or LocalFilesExplorer(rootdir=t.cast(str, rootdir))
        self.rootdir = rootdir or self.explorer.get_rootdir()
        self.vcs = vcs or Git(rootdir=self.rootdir)

        if not project_id:
            dir = Path(self.rootdir).resolve()
            self.project_id = project_id or f"{random_hash(str(dir.parent))}_{dir.name}"
        else:
            self.project_id = project_id

    @contextlib.contextmanager
    def in_working_state(self, config: Config):
        """Hook for doing any initial project setup and cleanup after the work is done.

        Real use case for now - adjusting rootdir to point to worktree dir if dont_disrupt_prior_state = True for Git.
        """
        # Setup phase:
        original_rootdir = self.rootdir
        with self.vcs.preserve_state(config=config.vcs) as current_project_dir:
            self.rootdir = str(current_project_dir)
            self.explorer.set_rootdir(newdir=str(current_project_dir))

            yield

        self.rootdir = original_rootdir
        self.explorer.set_rootdir(newdir=self.rootdir)

    def apply_changes(self):
        self.explorer.flush()

    @classmethod
    def from_uri(cls, uri: str) -> "Project":
        parsed_uri = urlparse(uri)
        # TODO: Add processing for file:///... schema
        if not parsed_uri.scheme:
            path = parse_dir(uri)
            project_id = f"{random_hash(str(path.parent))}_{path.name}"
            return cls(rootdir=str(path), project_id=project_id)

        else:
            raise NotImplementedError("Cloud path or 'file:///...' is not available yet.")
