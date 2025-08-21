from pathlib import Path
from automyte.automaton import RunContext
from automyte.automaton.types import TaskReturn
from automyte.discovery import File
from automyte.discovery.file.os_file import OSFile


class flush:
    """Util to force flushing of the file.

    Might be useful if you need to flush the file to the disk, before postprocess.
    """

    def __call__(self, ctx: RunContext, file: File | None):
        if file:
            file.flush()
        else:
            ctx.project.apply_changes()


class create:
    def __init__(self, path: Path | str, content: str = ""):
        self.path = Path(path) if isinstance(path, str) else path
        self.content = content

    def __call__(self, ctx: RunContext, file: File | None) -> TaskReturn:
        try:
            # point to worktree if dont_disrupt_prior_state is set to true
            if ctx.config.vcs.dont_disrupt_prior_state:
                self.path = self.get_worktree_path(self.path, ctx.project.rootdir)

            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()

            file = OSFile(fullname=str(self.path))
            file.edit(self.content)
            file.flush()

            return TaskReturn(
                status="processed",
                instruction="continue",
                value=file,
            )

        except Exception as e:
            return TaskReturn(status="errored", instruction="abort", value=str(e))

    def get_worktree_path(self, user_path: str | Path, worktree_path: str | Path):
        user_path = Path(user_path) if isinstance(user_path, str) else user_path
        worktree_path = Path(worktree_path) if isinstance(worktree_path, str) else worktree_path

        repo_root = worktree_path.parent
        relative_path = user_path.relative_to(repo_root)
        result = worktree_path / relative_path
        return result
