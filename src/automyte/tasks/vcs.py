from __future__ import annotations

from pathlib import Path

from automyte.automaton.run_context import RunContext
from automyte.automaton.types import TaskReturn
from automyte.discovery import File


class WithFlagsMixin:
    _flags: list[str]

    def flags(self, *args: str):
        self._flags.extend(list(args))
        return self


class VCSTask(WithFlagsMixin):
    def __init__(self):
        self._flags: list[str] = []

    def __call__(self, ctx: RunContext, file: File | None = None):
        raise NotImplementedError


class add(VCSTask):
    def __init__(self, paths: str | Path | list[str | Path]):
        super().__init__()
        if isinstance(paths, str) or isinstance(paths, Path):
            self.paths = [paths]
        else:
            self.paths = paths

    def __call__(self, ctx: RunContext, file: File | None = None):
        result = ctx.vcs.run("add", "--", *[str(p) for p in self.paths], *self._flags)

        if result.status == "fail":
            return TaskReturn(status="errored", instruction="abort", value=result.output)
        else:
            return TaskReturn(status="processed", instruction="continue", value=result.output)


class commit(VCSTask):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def __call__(self, ctx: RunContext, file: File | None = None):
        result = ctx.vcs.run("commit", "-m", self.msg, *self._flags)

        if result.status == "fail":
            return TaskReturn(status="errored", instruction="abort", value=result.output)
        else:
            return TaskReturn(status="processed", instruction="continue", value=result.output)


class push(VCSTask):
    def __init__(self, to: str, remote: str = "origin"):
        super().__init__()
        self.to = to
        self.remote = remote

    def __call__(self, ctx: RunContext, file: File | None = None):
        result = ctx.vcs.run("push", *self._flags, self.remote, self.to)

        if result.status == "fail":
            return TaskReturn(status="errored", instruction="abort", value=result.output)
        else:
            return TaskReturn(status="processed", instruction="continue", value=result.output)


class pull(VCSTask):
    def __init__(self, branch: str, remote: str = "origin"):
        super().__init__()
        self.branch = branch
        self.remote = remote

    def __call__(self, ctx: RunContext, file: File | None = None):
        result = ctx.vcs.run("pull", *self._flags, self.remote, self.branch)

        if result.status == "fail":
            return TaskReturn(status="errored", instruction="abort", value=result.output)
        else:
            return TaskReturn(status="processed", instruction="continue", value=result.output)
