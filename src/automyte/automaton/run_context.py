import contextlib
from dataclasses import dataclass

from automyte.config import Config
from automyte.discovery import File
from automyte.history import AutomatonRunResult
from automyte.project import Project
from automyte.vcs import VCS

# from automyte.tasks import TaskReturn
from .types import TaskReturn


@dataclass
class RunContext:
    automaton_name: str
    config: Config
    vcs: VCS
    project: Project
    current_status: AutomatonRunResult
    previous_status: AutomatonRunResult
    global_tasks_returns: list[TaskReturn]
    file_tasks_returns: list[TaskReturn]
    # NOTE: These fields are not used for now, so not gonna bother implementing them for now.
    # previous_task: BaseTask | None = None
    # next_task: BaseTask | None = None
    # current_file: File | None = None  # None for pre/post process tasks.

    @property
    def previous_return(self):
        """Return previously saved task execution result.

        pre/post process tasks returns are saved indefinitely inside automaton run
        main tasks section returns get cleaned up between each file.
        """
        with contextlib.suppress(IndexError):
            if self.file_tasks_returns:
                return self.file_tasks_returns[-1]
            elif self.global_tasks_returns:
                return self.global_tasks_returns[-1]

        return TaskReturn(instruction="continue", value=None)

    def save_task_result(self, result: TaskReturn, file: File | None):
        if file is None:
            self.global_tasks_returns.append(result)
        else:
            self.file_tasks_returns.append(result)
        return result

    def cleanup_file_returns(self):
        self.file_tasks_returns.clear()
