import typing as t

from automyte.automaton import BaseTask, RunContext
from automyte.automaton.flow import execute_task, execute_tasks_sequence
from automyte.automaton.types import TaskReturn
from automyte.discovery import File

_IgnorableInstructions: t.TypeAlias = t.Literal["skipped", "fail", "any"]


class IgnoreResult:
    """Wrapper for ignoring task results. Useful for when you don't care if the task has failed or skipped.

    Will prevent automaton from stopping / failing if the tasks passed here instruct it to abort.
    If multiple tasks are passed, will execute them in sequence, regardless if any of them has failed.
    """

    def __init__(self, *tasks: BaseTask, ignore: _IgnorableInstructions = "any"):
        self.tasks = list(tasks)
        if ignore == "any":
            self.ignore_instructions = ["skipped", "fail"]
        else:
            self.ignore_instructions = [ignore]

    def __call__(self, ctx: RunContext, file: File | None):
        for task in self.tasks:
            result = execute_task(task=task, ctx=ctx, file=file)
            if result and result.status in self.ignore_instructions:
                continue
            else:
                return result

        return None
