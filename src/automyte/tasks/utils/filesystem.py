from automyte.automaton import RunContext
from automyte.discovery import File


class flush:
    """Util to force flushing of the file.

    Might be useful if you need to flush the file to the disk, before postprocess.
    """

    def __call__(self, ctx: RunContext, file: File | None):
        if file:
            file.flush()
        else:
            ctx.project.apply_changes()
