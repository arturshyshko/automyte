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
            result = execute_task(ctx=ctx, task=preprocess_task, file=None)
            if result:
                return result

        for file in project.explorer.explore():
            for process_file_task in self.tasks:
                result = execute_task(ctx=ctx, task=process_file_task, file=file)
                if result:
                    return result

            ctx.cleanup_file_returns()

        # Has to be called prior to postprocess tasks, otherwise files changes are not reflected on disk before vcs calls.
        project.apply_changes()

        for post_task in self.postprocess_tasks:
            result = execute_task(ctx=ctx, task=post_task, file=None)
            if result:
                return result

        return AutomatonRunResult(status="success")


def execute_tasks_sequence(tasks: list[BaseTask], ctx: RunContext, file: File | None):
    """Similar to 'execute_task', except designed to run a sequence of tasks.

    This function is necessary to stop calls chain, if any of the tasks results in 'abort' or 'skip' instruction.
    """
    instruction: InstructionForAutomaton = "continue"
    for task in tasks:
        instruction = handle_task_call(task=task, ctx=ctx, file=file)
        # If any of the tasks in the sequence resulted in 'abort' or 'skip',
        # don't execute any of the remaining tasks and stop automaton run.
        if instruction != "continue":
            break

    if instruction == "skip":
        return AutomatonRunResult(status="skipped")
    elif instruction == "abort":
        return AutomatonRunResult(status="fail", error=str(ctx.previous_return.value))

    return None


def execute_task(ctx: "RunContext", task: BaseTask, file: File | None) -> AutomatonRunResult | None:
    """The main entrypoint for actually calling tasks inside automaton.

    Will wrap all returns into TaskReturns and save them to ctx;
    Handles exceptions inside tasks and sends abort instruction to automaton;

    If return value is None - flow is to just continue executing tasks,
        otherwise, need to interrupt.
    """
    instruction = handle_task_call(ctx=ctx, task=task, file=file)

    if instruction == "skip":
        return AutomatonRunResult(status="skipped")
    elif instruction == "abort":
        return AutomatonRunResult(status="fail", error=str(ctx.previous_return.value))

    return None


def handle_task_call(ctx: "RunContext", task: BaseTask, file: File | None) -> "InstructionForAutomaton":
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
