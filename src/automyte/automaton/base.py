from __future__ import annotations

import abc
from ast import arguments
import contextlib
import typing as t
from dataclasses import dataclass


import subprocess
from pathlib import Path


# TODO: Need to handle errors in the script call.
# TODO: move to bash utils.
def bash_execute(
        command: str | list[str],
        path: str | Path | None = None,
):
    if isinstance(command, str):
        command = command.split()

    output = subprocess.run(
        command, cwd=path, shell=False, text=True, capture_output=True,
    )

    return output.stdout.strip()

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

    @property
    def is_tainted(self) -> bool:
        raise NotImplementedError


_ProjectID: t.TypeAlias = str
AutomatonTarget: t.TypeAlias = t.Literal['all', 'new', 'successful', 'failed', 'skipped'] | _ProjectID

@dataclass
class Config:
    mode: RUN_MODES
    vcs: VCSConfig
    stop_on_fail: bool = True
    target: AutomatonTarget = 'all'

    @classmethod
    def get_default(cls, **kwargs):
        # TODO: Fix error when passing mode='run' in get_default kwargs and that gets multiple values for same arg.
        return cls(
            mode='run',
            stop_on_fail=True,
            vcs=VCSConfig(
                default_vcs='git',
                dont_disrupt_prior_state=True,
            ),
            **kwargs,
        )

    def set_vcs(self, **kwargs):
        self.vcs = VCSConfig.get_default(**kwargs)
        return self


SupportedVCS: t.TypeAlias = t.Literal['git']

@dataclass
class VCSConfig:
    default_vcs: SupportedVCS
    main_branch: str = 'master'
    work_branch: str | None = 'automate'
    dont_disrupt_prior_state: bool = True

    @classmethod
    def get_default(cls, **kwargs):
        kwargs.setdefault("default_vcs", 'git')
        kwargs.setdefault("main_branch", 'master')
        kwargs.setdefault("work_branch", 'automate')
        kwargs.setdefault("dont_disrupt_prior_state", True)

        return cls(**kwargs)


@dataclass
class RunContext:
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

        return TaskReturn(instruction='continue', value=None)

    def save_task_result(self, result: TaskReturn, file: File | None):
        if file is None:
            self.global_tasks_returns.append(result)
        else:
            self.file_tasks_returns.append(result)
        return result

    def cleanup_file_returns(self):
        self.file_tasks_returns.clear()


# TODO: Need to implement __and__ __or__ stuff, to be able to combine filters
class Filter:
    def filter(self, file: File) -> File | None:
        raise NotImplementedError

    def __call__(self, file: File) -> File | None:
        return self.filter(file=file)


# NOTE: Maybe split it into FilesBackend + ProjectExplorer class, so then ProjectExplorer is responsible for filters, backend is for getting/saving files
class ProjectExplorer(abc.ABC):
    def get_rootdir(self) -> str:
        """To be overriden by child classes to provide project/vcs with access to explorer's rootdir."""
        raise NotImplementedError

    def set_rootdir(self, newdir: str) -> str:
        """To be overriden by child classes to allow project to adjust explorer dir during setup() phase."""
        raise NotImplementedError

    def explore(self) -> t.Generator[File, None, None]:
        """To be inherited from and override accessing/saving project's files logic"""
        raise NotImplementedError

    def flush(self):
        """Centralised hook to actually apply all necessary changes for all files that require it."""
        raise NotImplementedError


class Project:
    def __init__(
            self,
            project_id: str,
            rootdir: str | None = None,
            explorer: ProjectExplorer | None = None,
            vcs: VCS | None = None
    ):
        assert rootdir or explorer, "Need to supply at least one of: rootdir | explorer."
        self.project_id = project_id
        self.explorer = explorer or LocalFilesExplorer(rootdir=rootdir)  # TODO: Fix linter??
        self.rootdir = rootdir or self.explorer.get_rootdir()
        self.vcs = vcs or Git(rootdir=self.rootdir)

    @contextlib.contextmanager
    def in_working_state(self, config: Config):
        """Hook for doing any initial project setup and cleanup after the work is done.

        Real use case for now - adjusting rootdir to point to worktree one if dont_disrupt_prior_state = True for Git.
        """
        # Setup phase:
        original_rootdir = self.rootdir
        with self.vcs.preserve_state(config=config.vcs) as current_project_dir:
            self.rootdir = str(current_project_dir)
            self.explorer.set_rootdir(newdir=str(current_project_dir))

            yield

        self.rootdir = original_rootdir
        self.explorer.set_rootdir(newdir=self.rootdir)

    def apply_changes(self):
        self.explorer.flush()


InstructionForAutomaton: t.TypeAlias = t.Literal['abort', 'skip', 'continue']

@dataclass
class TaskReturn:
    value: t.Any = None
    instruction: InstructionForAutomaton = 'continue'
    status: t.Literal['processed', 'skipped', 'errored'] = 'processed'


BaseTask: t.TypeAlias = t.Callable[[RunContext, File | None], TaskReturn | t.Any]
FileTask: t.TypeAlias = t.Callable[[RunContext, File], TaskReturn | t.Any]


class TasksFlow:
    def __init__(
            self,
            *args: list[FileTask],
            preprocess: list[BaseTask] | None = None,
            postprocess: list[BaseTask] | None = None
        ):
        self.preprocess_tasks = preprocess or []
        self.postprocess_tasks = postprocess or []
        self.tasks = list(*args)

    def execute(self, project: Project, ctx: RunContext):
        for preprocess_task in self.preprocess_tasks:
            instruction = self._handle_task_call(ctx=ctx, task=preprocess_task, file=None)

            if instruction == 'skip':
                return AutomatonRunResult(status='skipped')
            elif instruction == 'abort':
                return AutomatonRunResult(status='fail', error=str(ctx.previous_return.value))

        for file in project.explorer.explore():
            for process_file_task in self.tasks:
                instruction = self._handle_task_call(ctx=ctx, task=process_file_task, file=file)

                if instruction == 'skip':
                    return AutomatonRunResult(status='skipped')
                elif instruction == 'abort':
                    return AutomatonRunResult(status='fail', error=str(ctx.previous_return.value))

            ctx.cleanup_file_returns()

        # Has to be called prior to postprocess tasks, otherwise files changes are not reflected on disk before vcs calls.
        project.apply_changes()

        for post_task in self.postprocess_tasks:
            instruction = self._handle_task_call(ctx=ctx, task=post_task, file=None)

            if instruction == 'skip':
                return AutomatonRunResult(status='skipped')
            elif instruction == 'abort':
                return AutomatonRunResult(status='fail', error=str(ctx.previous_return.value))

        return AutomatonRunResult(status='success')

    def _handle_task_call(self, ctx: RunContext, task: BaseTask, file: File | None) -> InstructionForAutomaton:
        """ Convenience wrapper for calling and handling all tasks.

        Wraps plain python values into TaskReturns,
            so that user doesn't have to do it unless they want to specify behaviour;
        Save task return into ctx;
        Return instruction for automaton on what to do next (like skip the project, continue or abort right away).

        If the task raised an Exception - save it's value into task return with "errored" status and instruct to abort.
        """
        try:

            task_result = wrap_task_result(task(ctx, file))

        except Exception as e:
            ctx.save_task_result(result=TaskReturn(instruction='abort', value=str(e), status='errored'), file=file)
            return 'abort'

        else:
            ctx.save_task_result(result=task_result, file=file)
            return task_result.instruction

RunStatus: t.TypeAlias = t.Literal['fail', 'success', 'skipped', 'running', 'new']

@dataclass
class AutomatonRunResult:
    status: RunStatus
    error: str | None = None


class VCS(abc.ABC):
    """NOTE: VCS operations are to rely on RunContext to get access to project rootdir and stuff."""
    def switch(self, to: str) -> t.Self:
        raise NotImplementedError

    def add(self, path: str | Path | File | Filter) -> t.Self:
        raise NotImplementedError

    def commit(self, msg: str) -> t.Self:
        raise NotImplementedError

    def pull(self, branch: str) -> t.Self:
        # TODO: Mode to be configured in init of the specific implementation.
        raise NotImplementedError

    def assure_remote(self) -> t.Self:
        """Function to make sure remote is present - either create one or check if it exists, throw error otherwise."""
        raise NotImplementedError

    def push(self, to: str) -> t.Self:
        raise NotImplementedError

    # TODO: Think on how this should be implemented.
    def pr(self, create: bool) -> None:
        raise NotImplementedError

    # Will be using worktrees for git. Think if need to return smth?
    @contextlib.contextmanager
    def preserve_state(self, config: VCSConfig):
        raise NotImplementedError

    def run(self, subcommand):
        raise NotImplementedError

import hashlib, uuid
# TODO: Figure out authentication.
# TODO: Setup proper implementations when splitting into files. (probably use builder pattern for commands, like lazygit)
class Git(VCS):
    def __init__(
        self,
        rootdir: str,
        preferred_workflow: t.Literal['rebase', 'merge'] = 'rebase',
        remote: str | None = 'origin',  # TODO: Figure out how to work properly with remote, like validation, origin/custom_name, check if it's been setup and stuff.
    ) -> None:
            self.preferred_workflow = preferred_workflow
            self.remote = remote
            self.original_rootdir = rootdir
            self.workdir = rootdir

    def switch(self, to: str) -> t.Self:
        bash_execute(f"git -C {self.workdir} switch -c {to} 2>/dev/null || git switch {to}")
        return self

    def add(self, path: str | Path | File | Filter) -> t.Self:
        output = bash_execute(f"git -C {self.workdir} add {path}")
        return self

    def commit(self, msg: str) -> t.Self:
        command = f'git -C {self.workdir} commit -m "{msg}"'
        output = bash_execute(['git', '-C', f'{self.workdir}', 'commit', '-m', f'"{msg}"'])
        return self

    def pull(self, branch: str) -> t.Self:
        if self.preferred_workflow == 'rebase':
            bash_execute(f'git -C {self.workdir} pull --rebase {self.remote} {branch}')
        else:
            bash_execute(f'git -C {self.workdir} pull {self.remote} {branch}')

        return self

    def assure_remote(self) -> t.Self:
        """Function to make sure remote is present - either create one or check if it exists, throw error otherwise."""
        # TODO: Implement
        return self

    def push(self, to: str) -> t.Self:
        bash_execute(f"git -C {self.workdir} push --force-with-lease origin {to}")
        return self

    # TODO: Think on how this should be implemented.
    def pr(self, create: bool) -> None:
        raise NotImplementedError

    def run(self, subcommand: str):
        output = bash_execute(f'git -C {self.workdir} {subcommand}')
        return output

    @contextlib.contextmanager
    def preserve_state(self, config: VCSConfig):
        if config.dont_disrupt_prior_state:
            # TODO: Maybe add a check if a work_branch already exists in run mode, then have to process this somehow, as worktree will not be created?
            random_hash = f'auto_{hashlib.md5(uuid.uuid4().bytes).hexdigest()}'
            relative_worktree_path = f"./{random_hash}"
            output = bash_execute(f'git -C {self.original_rootdir} worktree add -b {config.work_branch} {relative_worktree_path}')

            self.workdir = Path(self.original_rootdir) / relative_worktree_path
            yield str(self.workdir)

            bash_execute(f'git -C {self.original_rootdir} worktree remove -f {relative_worktree_path}')

        else:
            yield self.original_rootdir






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
            result = AutomatonRunResult(status='running')
            previous_result = self.history.get_status(project.project_id)

            try:
                ctx = RunContext(
                    config=self.config, vcs=project.vcs, project=project,
                    current_status=result, previous_status=previous_result,
                    global_tasks_returns=[], file_tasks_returns=[]
                )
                result = self._execute_for_project(project, ctx)

            except Exception as e:
                result = AutomatonRunResult(status='fail', error=str(e))

            finally:
                self._update_history(project, result)

            if self.config.stop_on_fail and result.status == 'fail':
                break

    def _get_target_projects(self) -> t.Generator[Project, None, None]:
        targets = {p.project_id: p for p in self.projects}
        filter_by_status = lambda status: {  # Get projects from targets based on their status in history.
            proj_id: targets[proj_id]
            for proj_id, run in self.history.read().items()
            if run.status == status
        }

        match self.config.target:
            case 'all': pass
            case 'new': targets = filter_by_status('new')
            case 'failed': targets = filter_by_status('fail')
            case 'successful': targets = filter_by_status('success')
            case 'skipped': targets = filter_by_status('skipped')
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


# NOTE: This should probably be top-level function in TasksFlow module?
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
        self.tainted: bool = False

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
            physical_file.write(self.get_contents())

    def contains(self, text: str) -> bool:
        return text in (self._contents or '')

    def move(self, to: str | None = None, new_name: str | None = None) -> File:
        self._location = str(Path(to or self.folder) / (new_name or self.name))
        self.tainted = True
        return self

    def get_contents(self) -> str:
        if self._contents is None:
            self.read()

        return self._contents or ''

    def edit(self, text: str) -> File:
        self._contents = text
        self.tainted = True
        return self

    def delete(self) -> File:
        self._marked_for_delete = True
        self.tainted = True
        return self

    @property
    def is_tainted(self) -> bool:
        return self.tainted

    def __str__(self):
        return self._initial_location


class ContainsFilter(Filter):
    def __init__(self, contains: str | list[str]) -> None:
        self.text = contains if isinstance(contains, list) else [contains]
        # TODO: Handle regexp case.

    def filter(self, file: File) -> File | None:
        if any(file.contains(occurance) for occurance in self.text):
            return file


class LocalFilesExplorer(ProjectExplorer):
    def __init__(self, rootdir: str, filter_by: Filter | None = None):
        self.rootdir = rootdir
        self.filter_by = filter_by
        self._changed_files: list[File] = []

    def _all_files(self) -> t.Generator[File, None, None]:
        for root, dirs, files in os.walk(self.rootdir):
            for f in files:
                yield OSFile(fullname=str(Path(root)/f)).read()

    def explore(self) -> t.Generator[File, None, None]:
        for file in self._all_files():
            if not self.filter_by or self.filter_by.filter(file):  # Don't filter at all if no filters supplied.
                yield file

                if file.is_tainted:
                    self._changed_files.append(file)

    def get_rootdir(self) -> str:
        return self.rootdir

    def set_rootdir(self, newdir: str) -> str:
        self.rootdir = newdir
        return newdir

    def flush(self):
        for file in self._changed_files:
            file.flush()

class History(abc.ABC):
    def set_status(self, project_id: str, status: AutomatonRunResult):
        raise NotImplementedError

    def get_status(self, project_id: str) -> AutomatonRunResult:
        raise NotImplementedError

    def read(self) -> dict[_ProjectID, AutomatonRunResult]:
        """Return all project's history status"""
        raise NotImplementedError


from collections import defaultdict


class InMemoryHistory(History):
    def __init__(self) -> None:
        self.data: dict[str, AutomatonRunResult] = defaultdict(lambda: AutomatonRunResult(status='new'))

    def get_status(self, project_id: str) -> AutomatonRunResult:
        return self.data[project_id]

    def set_status(self, project_id: str, status: AutomatonRunResult):
        self.data[project_id] = status

    def read(self):
        return self.data


class ModeGuards:
    run = lambda ctx: ctx.config.mode == 'run'
    amend = lambda ctx: ctx.config.mode == 'amend'

class HistoryGuards:
    failed = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == 'fail'
    skipped = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == 'skipped'
    succeeded = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == 'success'
    new = lambda ctx: ctx.history.get_status(ctx.project.project_id).status == 'new'

class PreviousTaskGuards:
    is_success = lambda ctx: ctx.previous_return is None or ctx.previous_return.status == 'processed'
    was_skipped = lambda ctx: ctx.previous_return is None or not ctx.previous_return.status == 'skipped'

# TODO: Figure out a typing for passing any of the attrs of these classes.
# TODO: This will just be in a module called "guards", so I don't actually need Guards class.
GuardsCollection: t.TypeAlias = ModeGuards | HistoryGuards | PreviousTaskGuards

class Guards:
    MODE = ModeGuards
    HISTORY = HistoryGuards
    PREVIOUS_TASK = PreviousTaskGuards


class TaskGuard:
    def __init__(self, *args: FileTask) -> None:
        self.tasks = list(args)

    def __call__(self, ctx: RunContext, file: File):
        if self.guard(ctx):
            for task in self.tasks:
                result = task(ctx, file)
            else:
                # TODO: Need to actually properly handle cases when tasks fail.
                return locals().get('result', None)  # Just preventing linter from complaining
        else:
            # TODO: What should be done here? Supposedle, RunResult('skip')
            ...

    def guard(self, ctx: RunContext) -> bool:
        raise NotImplementedError


class Conditional(TaskGuard):
    def __init__(self, *args: FileTask, on: t.Callable[[RunContext], bool]) -> None:
        super().__init__(*args)
        self.validator = on

    def guard(self, ctx: RunContext) -> bool:
        return self.validator(ctx)


# TODO: Think of a better implementation?
class Breakpoint:
    def __call__(self, ctx: RunContext, file: File | None):
        import pdb; pdb.set_trace()
