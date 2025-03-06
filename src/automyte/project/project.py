import contextlib
import typing as t

from automyte.config import Config
from automyte.discovery import LocalFilesExplorer, ProjectExplorer
from automyte.vcs import VCS, Git


class Project:
    def __init__(
        self,
        project_id: str,
        rootdir: str | None = None,
        explorer: ProjectExplorer | None = None,
        vcs: VCS | None = None,
    ):
        if not rootdir and not explorer:
            raise ValueError("Need to supply at least one of: rootdir | explorer")

        self.project_id = project_id
        self.explorer = explorer or LocalFilesExplorer(rootdir=t.cast(str, rootdir))
        self.rootdir = rootdir or self.explorer.get_rootdir()
        self.vcs = vcs or Git(rootdir=self.rootdir)

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
