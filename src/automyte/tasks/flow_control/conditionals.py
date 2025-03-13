import typing as t

from automyte.automaton import BaseTask, RunContext
from automyte.automaton.flow import execute_tasks_sequence
from automyte.automaton.types import TaskReturn
from automyte.discovery import File, Filter


class If:
    """Tasks wrapper, which decides whether to run a task or not.

    If `filter` is provided - will skip, unless file passes filtering, even if other conditions match.
    If `condition` or `check` are provided:
        `condition` - just a boolean expression, if true - run tasks, otherwise - skip
        `check` - a function, which will be given ctx and file and has to return bool

    Cannot pass both `condition` and `check` params.
    """

    def __init__(
        self,
        *tasks: BaseTask,
        condition: bool | None = None,
        check: t.Callable[[RunContext, File | None], bool] | None = None,
        filter: Filter | None = None,
    ):
        if condition is not None and check is not None:
            raise ValueError("Can only provide one: either `condition` or `check`.")

        self.condition = condition
        self.check = check
        self.filter = filter
        self.tasks = list(tasks)

    def __call__(self, ctx: RunContext, file: File | None):
        result = TaskReturn(status="skipped")

        if file is not None and self.filter is not None:
            if not self.filter.filter(file):
                return result

        if self.condition is not None:
            if self.condition:
                return execute_tasks_sequence(tasks=self.tasks, ctx=ctx, file=file)

        elif self.check is not None:
            if self.check(ctx, file):
                return execute_tasks_sequence(tasks=self.tasks, ctx=ctx, file=file)

        return result
