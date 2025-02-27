import typing as t

from automyte.config import Config
from automyte.history import AutomatonRunResult, History, InMemoryHistory
from automyte.project import Project

from .flow import TasksFlow
from .run_context import RunContext


class Automaton:
    def __init__(
        self,
        name: str,
        projects: list[Project],
        flow: TasksFlow,
        config: Config | None = None,
        history: History | None = None,
    ):
        self.name = name
        self.config: Config = config or Config.get_default()
        self.history: History = history or InMemoryHistory()
        self.projects = projects
        self.flow = flow

    def run(self):
        for project in self._get_target_projects():
            result = AutomatonRunResult(status="running")
            previous_result = self.history.get_status(project.project_id)

            try:
                ctx = RunContext(
                    config=self.config,
                    vcs=project.vcs,
                    project=project,
                    current_status=result,
                    previous_status=previous_result,
                    global_tasks_returns=[],
                    file_tasks_returns=[],
                )
                result = self._execute_for_project(project, ctx)

            except Exception as e:
                result = AutomatonRunResult(status="fail", error=str(e))

            finally:
                self._update_history(project, result)

            if self.config.stop_on_fail and result.status == "fail":
                break

    def _get_target_projects(self) -> t.Generator[Project, None, None]:
        targets = {p.project_id: p for p in self.projects}
        filter_by_status = lambda status: {  # Get projects from targets based on their status in history.
            proj_id: targets[proj_id] for proj_id, run in self.history.read().items() if run.status == status
        }

        match self.config.target:
            case "all":
                pass
            case "new":
                targets = filter_by_status("new")
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
        self.history.set_status(project.project_id, result)
