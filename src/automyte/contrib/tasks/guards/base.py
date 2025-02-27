import typing as t

# from automyte.tasks.types import FileTask
from automyte.automaton import FileTask, RunContext
from automyte.discovery import File


class TaskGuard:
    def __init__(self, *args: FileTask) -> None:
        self.tasks = list(args)

    def __call__(self, ctx: RunContext, file: File):
        if self.guard(ctx):
            for task in self.tasks:
                result = task(ctx, file)
            else:
                # TODO: Need to actually properly handle cases when tasks fail.
                return locals().get("result", None)  # Just preventing linter from complaining
        else:
            # TODO: What should be done here? Supposedly, RunResult('skip')
            ...

    def guard(self, ctx: RunContext) -> bool:
        raise NotImplementedError


class Conditional(TaskGuard):
    def __init__(self, *args: FileTask, on: t.Callable[[RunContext], bool]) -> None:
        super().__init__(*args)
        self.validator = on

    def guard(self, ctx: RunContext) -> bool:
        return self.validator(ctx)
