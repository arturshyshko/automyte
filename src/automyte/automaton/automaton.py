import typing as t

from automyte.config import Config
from automyte.history import AutomatonRunResult, History, InMemoryHistory
from automyte.project import Project

from .flow import TasksFlow
from .run_context import RunContext
from .types import FileTask


class Automaton:
    def __init__(
        self,
        name: str,
        projects: list[Project],
        tasks: TasksFlow | list[FileTask],
        config: Config | None = None,
        history: History | None = None,
    ):
        self.name = name
        self.config: Config = config or Config.get_default()
        self.history: History = history or InMemoryHistory()
        self.projects = projects

        if isinstance(tasks, TasksFlow):
            self.flow = tasks
        else:
            self.flow = TasksFlow(*tasks)

    def run(self):
        for project in self._get_target_projects():
            result = AutomatonRunResult(status="running")
            previous_result = self.history.get_status(self.name, project.project_id)
            ctx = RunContext(
                automaton_name=self.name,
                config=self.config,
                vcs=project.vcs,
                project=project,
                current_status=result,
                previous_status=previous_result,
                global_tasks_returns=[],
                file_tasks_returns=[],
            )

            try:
                result = self._execute_for_project(project, ctx)

            except Exception as e:
                result = AutomatonRunResult(status="fail", error=str(e))

            finally:
                self._update_history(project, result)

            if self.config.stop_on_fail and result.status == "fail":
                break

    def _get_target_projects(self) -> t.Generator[Project, None, None]:
        targets = {p.project_id: p for p in self.projects}
        projects_in_history = self.history.read(self.name)
        filter_by_status = lambda status: {  # Get projects from targets based on their status in history.
            proj_id: targets[proj_id] for proj_id, run in projects_in_history.items() if run.status == status
        }

        match self.config.target:
            case "all":
                pass
            case "new":
                new_targets = filter_by_status("new")
                targets = {  # Including projects that are not in the history yet (if added for 2nd run for example).
                    **new_targets,
                    **{pid: proj for pid, proj in targets.items() if pid not in projects_in_history},
                }
            case "failed":
                targets = filter_by_status("fail")
            case "successful":
                targets = filter_by_status("success")
            case "skipped":
                targets = filter_by_status("skipped")
            case _:  # Passed target_id explicitly.
                targets = {pid: proj for pid, proj in targets.items() if pid == self.config.target}

        for project in targets.values():
            yield project

    def _execute_for_project(self, project: Project, ctx: RunContext) -> AutomatonRunResult:
        with project.in_working_state(ctx.config):
            result = self.flow.execute(project=project, ctx=ctx)

        return result

    def _update_history(self, project: Project, result: AutomatonRunResult):
        self.history.set_status(automaton_name=self.name, project_id=project.project_id, status=result)
