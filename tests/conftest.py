import os
import typing as t
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from automyte.automaton.run_context import RunContext
from automyte.config.base import Config
from automyte.discovery import OSFile
from automyte.history.types import AutomatonRunResult
from automyte.project import Project
from automyte.utils import bash
from automyte.utils.random import random_hash
from automyte.vcs.base import VCS

_DirName: t.TypeAlias = str
_FileName: t.TypeAlias = str
_FileContents: t.TypeAlias = str
_ProjectStructure: t.TypeAlias = dict[_DirName | _FileName, t.Union[_FileContents, "_ProjectStructure"]]


@pytest.fixture
def tmp_local_project_factory():
    """Setup a tmp project structure with folders, files and their contents for testing.

    Returns a factory function which accepts dictionary structure where we specify project structure.
    All projects are created in tmp folders which are cleaned up automatically after each run.

    Don't pass "dir" argument, as it is only used for recursive call for internal implementation.

    Example:
        tmp_local_project_factory(structure={
            'src': {
                'subdir1': {
                    'hello.txt': 'this will be the text for src/subdir1/hello.txt file',
                    'bye.py': 'print("good bye")',
                },
                'subdir2': {...},
            ...
            }
        })
    """
    rootdirs = []
    try:

        def _create_tmp_project(structure: _ProjectStructure, dir: str | None = None):
            if dir:  # Recursive call, just need to create child dirs.
                if not Path(dir).exists():
                    os.mkdir(dir)
                current_dir = dir
            else:  # First call, need to create TMP dir as parent and add it to array for removal.
                new_tmp_dir = TemporaryDirectory()
                rootdirs.append(new_tmp_dir)
                current_dir = new_tmp_dir.name

            for name, content in structure.items():
                if isinstance(content, str):  # Encountered a file.
                    with open(Path(current_dir) / name, "w") as f:
                        f.write(content)
                else:  # Encoruntered a folder, so need to generate the whole structure again, recursively.
                    _create_tmp_project(structure=content, dir=f"{current_dir}/{name}")

            return current_dir

        yield _create_tmp_project

    finally:
        for dir in rootdirs:
            dir.cleanup()


@pytest.fixture
def tmp_git_repo(tmp_local_project_factory):
    def _tmp_git_repo_factory(initial_structure, unstaged_structure=None):
        dir = tmp_local_project_factory(initial_structure)
        bash.execute(["git", "-C", dir, "init"])
        bash.execute(["git", "-C", dir, "add", "--all"])
        bash.execute(["git", "-C", dir, "commit", "-m", "Initial commit"])

        if unstaged_structure:
            tmp_local_project_factory(unstaged_structure, dir=dir)

        return dir

    return _tmp_git_repo_factory


@pytest.fixture
def run_ctx():
    def _ctx_factory(
        dir: str | Path, vcs: VCS | None = None, project: Project | None = None, automaton_name: str = "auto"
    ):
        if project is None:
            project = Project(project_id=random_hash(), rootdir=str(dir))
        if vcs is None:
            vcs = project.vcs

        return RunContext(
            automaton_name=automaton_name,
            config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
            vcs=vcs,
            project=project,
            current_status=AutomatonRunResult("running"),
            previous_status=AutomatonRunResult("new"),
            global_tasks_returns=[],
            file_tasks_returns=[],
        )

    return _ctx_factory


@pytest.fixture
def tmp_os_file(tmp_local_project_factory):
    def _tmp_file_factory(contents: str, filename: str | None = None) -> OSFile:
        filename = filename or random_hash()
        dir = tmp_local_project_factory(structure={filename: contents})

        filepath = Path(dir) / filename
        with open(filepath, "w") as f:
            f.write(contents)

        return OSFile(fullname=str(filepath))

    return _tmp_file_factory
