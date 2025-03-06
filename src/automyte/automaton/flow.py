import typing as t

from automyte.discovery import File
from automyte.history import AutomatonRunResult
from automyte.project import Project

from .run_context import RunContext
from .types import BaseTask, FileTask, InstructionForAutomaton, TaskReturn


class TasksFlow:
    def __init__(
        self,
        *tasks: FileTask | list[FileTask],
        preprocess: list[BaseTask] | None = None,
        postprocess: list[BaseTask] | None = None,
    ):
        self.preprocess_tasks = preprocess or []
        self.postprocess_tasks = postprocess or []

        self.tasks = []
        for task in tasks:
            if isinstance(task, list):
                self.tasks.extend(task)
            else:
                self.tasks.append(task)

    def execute(self, project: Project, ctx: "RunContext"):
        for preprocess_task in self.preprocess_tasks:
            instruction = self._handle_task_call(ctx=ctx, task=preprocess_task, file=None)

            if instruction == "skip":
                return AutomatonRunResult(status="skipped")
            elif instruction == "abort":
                return AutomatonRunResult(status="fail", error=str(ctx.previous_return.value))

        for file in project.explorer.explore():
            for process_file_task in self.tasks:
                instruction = self._handle_task_call(ctx=ctx, task=process_file_task, file=file)

                if instruction == "skip":
                    return AutomatonRunResult(status="skipped")
                elif instruction == "abort":
                    return AutomatonRunResult(status="fail", error=str(ctx.previous_return.value))

            ctx.cleanup_file_returns()

        # Has to be called prior to postprocess tasks, otherwise files changes are not reflected on disk before vcs calls.
        project.apply_changes()

        for post_task in self.postprocess_tasks:
            instruction = self._handle_task_call(ctx=ctx, task=post_task, file=None)

            if instruction == "skip":
                return AutomatonRunResult(status="skipped")
            elif instruction == "abort":
                return AutomatonRunResult(status="fail", error=str(ctx.previous_return.value))

        return AutomatonRunResult(status="success")

    def _handle_task_call(self, ctx: "RunContext", task: BaseTask, file: File | None) -> "InstructionForAutomaton":
        """Convenience wrapper for calling and handling all tasks.

        Wraps plain python values into TaskReturns,
            so that user doesn't have to do it unless they want to specify behaviour;
        Save task return into ctx;
        Return instruction for automaton on what to do next (like skip the project, continue or abort right away).

        If the task raised an Exception - save it's value into task return with "errored" status and instruct to abort.
        """
        try:
            task_result = wrap_task_result(task(ctx, file))

        except Exception as e:
            ctx.save_task_result(result=TaskReturn(instruction="abort", value=str(e), status="errored"), file=file)
            return "abort"

        else:
            ctx.save_task_result(result=task_result, file=file)
            return task_result.instruction


def wrap_task_result(value: t.Any) -> TaskReturn:
    if isinstance(value, TaskReturn):
        return value
    else:
        return TaskReturn(instruction="continue", status="processed", value=value)
