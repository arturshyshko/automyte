from __future__ import annotations

import abc
import contextlib
import typing as t
from dataclasses import dataclass


RUN_MODES = t.Literal['run', 'amend']


class File(abc.ABC):
    @property
    def folder(self) -> str:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    def get(self) -> t.Self:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError

    def contains(self, text: str) -> bool:
        raise NotImplementedError

    def move(self, to: str | None = None, new_name: str | None = None) -> File:
        raise NotImplementedError

    def get_contents(self) -> str:
        raise NotImplementedError

    def edit(self, text: str) -> File:
        raise NotImplementedError

    def delete(self) -> File:
        raise NotImplementedError


@dataclass
class Config:
    mode: RUN_MODES
    stop_on_fail: bool = True


# TODO: Need to implement __and__ __or__ stuff, to be able to combine filters
class Filter:
    def filter(self, file: File) -> File | None:
        raise NotImplementedError

    def __call__(self, file: File) -> File | None:
        return self.filter(file=file)


# TODO: Maybe split it into FilesBackend + ProjectExplorer class, so then ProjectExplorer is responsible for filters, backend is for getting/saving files
class ProjectExplorer(abc.ABC):
    def __init__(self, filter_by: Filter):
        self.filter_by = filter_by

    """To be inherited from and override accessing/saving project's files logic"""
    def explore(self) -> t.Generator[File, None, None]:
        """Filter"""
        raise NotImplementedError


@dataclass
class Project:
    project_id: str
    explorer: ProjectExplorer


@dataclass
class TaskReturn:
    instruction: t.Literal['abort', 'skip', 'continue']
    value: t.Any


@dataclass
class BaseTask:
    def __call__(self, context: RunContext) -> TaskReturn:
        raise NotImplementedError


class TasksFlow:
    def __init__(
            self,
            *args: list[BaseTask],
            preprocess: list[BaseTask] | None = None,
            postprocess: list[BaseTask] | None = None
        ):
        self.preprocess_tasks = preprocess or []
        self.postprocess_tasks = postprocess or []
        self.tasks = list(*args)


@dataclass
class RunContext:
    config: Config
    project: Project
    current_status: AutomatonRunResult
    previous_task: BaseTask | None = None
    next_task: BaseTask | None = None
    tasks_returns: list[TaskReturn] | None = None
    current_file: File | None = None  # None for pre/post process tasks.

    @property
    def previous_return(self):
        if self.tasks_returns:
            with contextlib.suppress(IndexError):
                return self.tasks_returns[-1]
        return None

    def save_task_result(self, result: TaskReturn):
        if self.tasks_returns is None:
            self.tasks_returns = [result]
        else:
            self.tasks_returns.append(result)
        return result


@dataclass
class AutomatonRunResult:
    status: t.Literal['fail', 'success', 'skipped', 'running']
    error: str | None = None


class Automaton:
    def __init__(
            self,
            name: str,
            config: Config,
            projects: list[Project],
            flow: TasksFlow,
        ):
            self.name = name
            self.config = config
            self.projects = projects
            self.flow = flow

    def run(self):
        result = AutomatonRunResult(status='running')

        for project in self._get_target_projects():
            try:
                ctx = RunContext(config=self.config, project=project, current_status=result, tasks_returns=[])
                result = self._execute_for_project(project, ctx)
            except Exception as e:
                result = AutomatonRunResult(status='fail', error=str(e))
            finally:
                self._update_history(project, result)

            if self.config.stop_on_fail:
                break

    def _get_target_projects(self) -> list[Project]:
        """TODO"""
        raise NotImplementedError

    def _execute_for_project(self, project: Project, ctx: RunContext) -> AutomatonRunResult:
        """TODO: CURRENT"""
        # TODO: Think about how to handle abort instruction nicely.
        # TODO: Think about on_task_fail='revert | pause' functionality.
        for preprocess_task in self.flow.preprocess_tasks:
            ctx.save_task_result(wrap_task_result(preprocess_task(ctx)))

        for file in project.explorer.explore():
            for process_file_task in self.flow.tasks:
                ctx.save_task_result(wrap_task_result(process_file_task(ctx, file)))

        for post_task in self.flow.postprocess_tasks:
            ctx.save_task_result(wrap_task_result(post_task(ctx)))

        return AutomatonRunResult(status='success')

    def _update_history(self, project: Project, result: AutomatonRunResult):
        """TODO"""
        return


def wrap_task_result(value: t.Any) -> TaskReturn:
    if isinstance(value, TaskReturn):
        return value
    else:
        return TaskReturn(instruction='continue', value=value)












import os
from pathlib import Path

class OSFile(File):
    def __init__(self, fullname: str):
        self._initial_location = fullname
        self._location = fullname

        self._inital_contents: str | None = None
        self._contents: str | None = None

        self._marked_for_delete: bool = False

    @property
    def folder(self) -> str:
        return str(Path(self._location).parent)

    @property
    def name(self) -> str:
        return str(Path(self._location).name)

    def read(self) -> t.Self:
        with open(self._location, 'r') as physical_file:
            self._inital_contents = physical_file.read()
            self._contents = self._inital_contents

        return self

    def flush(self) -> None:
        with open(self._location, 'w') as physical_file:
            physical_file.write(self._contents or '')

    def contains(self, text: str) -> bool:
        return text in (self._contents or '')

    def move(self, to: str | None = None, new_name: str | None = None) -> File:
        self._location = str(Path(to or self.folder) / (new_name or self.name))
        return self

    def get_contents(self) -> str:
        if self._contents is None:
            self.read()

        return self._contents or ''

    def edit(self, text: str) -> File:
        self._contents = text
        return self

    def delete(self) -> File:
        self._marked_for_delete = True
        return self


class ContainsFilter(Filter):
    def __init__(self, text: str | list[str]) -> None:
        self.text = text if isinstance(text, list) else [text]
        # TODO: Handle regexp case.

    def filter(self, file: File) -> File | None:
        if any(file.contains(occurance) for occurance in self.text):
            return file


class LocalFilesExplorer(ProjectExplorer):
    def __init__(self, rootdir: str, filter_by: Filter):
        self.rootdir = rootdir
        self.filter_by = filter_by

    def _all_files(self) -> t.Generator[File, None, None]:
        for root, dirs, files in os.walk(self.rootdir):
            for f in files:
                yield OSFile(fullname=str(Path(root)/f))

    def explore(self) -> t.Generator[File, None, None]:
        for file in self._all_files():
            if self.filter_by(file):
                yield file
