import typing as t

from automyte.automaton import BaseTask, RunContext
from automyte.automaton.flow import execute_tasks_sequence
from automyte.automaton.types import TaskReturn
from automyte.discovery import File


class RunIf:
    def __init__(self, *tasks: BaseTask, condition: bool):
        self.condition = condition
        self.tasks = list(tasks)

    def __call__(self, ctx: RunContext, file: File | None):
        if not self.condition:
            return TaskReturn(status="skipped")

        return execute_tasks_sequence(tasks=self.tasks, ctx=ctx, file=file)


class RunOn:
    def __init__(self, *tasks: BaseTask, on: t.Callable[[RunContext, File | None], bool]) -> None:
        self.validator = on
        self.tasks = list(tasks)

    def __call__(self, ctx: RunContext, file: File | None):
        if not self.validator(ctx, file):
            return TaskReturn(status="skipped")

        return execute_tasks_sequence(tasks=self.tasks, ctx=ctx, file=file)
