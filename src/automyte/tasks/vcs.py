from __future__ import annotations

from pathlib import Path

from automyte.automaton.run_context import RunContext
from automyte.discovery import File


class VCSTask:
    def __init__(self):
        self._flags: list[str] = []

    def __call__(self, ctx: RunContext, file: File | None = None):
        raise NotImplementedError

    def flags(self, *args: str) -> "VCSTask":
        self._flags.extend(list(args))
        return self


class add(VCSTask):
    def __init__(self, paths: str | Path | list[str | Path]):
        super().__init__()
        if isinstance(paths, str) or isinstance(paths, Path):
            self.paths = [paths]
        else:
            self.paths = paths

    def __call__(self, ctx: RunContext, file: File | None = None):
        ctx.vcs.run("add", "--", *[str(p) for p in self.paths], *self._flags)


class commit(VCSTask):
    def __init__(self, msg: str):
        super().__init__()
        self.msg = msg

    def __call__(self, ctx: RunContext, file: File | None = None):
        ctx.vcs.run("commit", "-m", self.msg, *self._flags)


class push(VCSTask):
    def __init__(self, to: str, remote: str = "origin"):
        super().__init__()
        self.to = to
        self.remote = remote

    def __call__(self, ctx: RunContext, file: File | None = None):
        ctx.vcs.run("push", *self._flags, self.remote, self.to)
