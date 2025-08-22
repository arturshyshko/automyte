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
    """Util to create a new file.
    Input:
        path: path relative to the project rootdir for the new file to be created
        content: string content to be written into the file
    """

    def __init__(self, path: Path | str, content: str = ""):
        self.path = Path(path) if isinstance(path, str) else path
        self.content = content

    def __call__(self, ctx: RunContext, file: File | None) -> TaskReturn:
        try:
            self.path = ctx.project.rootdir / self.path
            file = ctx.project.explorer.add_file(path=self.path, content=self.content)
            file.flush()

        except Exception as e:
            return TaskReturn(status="errored", instruction="abort", value=str(e))

        return TaskReturn(
            status="processed",
            instruction="continue",
            value=file,
        )
