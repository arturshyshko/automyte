from pathlib import Path

from automyte import (
    Automaton,
    AutomatonRunResult,
    Config,
    ContainsFilter,
    File,
    InMemoryHistory,
    LocalFilesExplorer,
    Project,
    RunContext,
    TaskReturn,
    TasksFlow,
    guards,
)
from automyte.tasks import vcs
from automyte.utils import bash


def lol(ctx: RunContext, file: File):
    import re

    file.edit(re.sub(r"world", "there", file.get_contents()))


def test_worktree_setup(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!"}})

    # Worktrees require at least 1 commit
    bash.execute(["git", "-C", dir, "init"])
    bash.execute(["git", "-C", dir, "add", "."])
    bash.execute(["git", "-C", dir, "commit", "-m", "hello"])

    Automaton(
        name="impl1",
        config=Config.get_default(),
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow(
            [
                lol,
                # vcs.add()
            ],
            preprocess=[
                # vcs.run('init')
            ],
            postprocess=[
                vcs.add("."),
                vcs.commit("testing worktree"),
                # Breakpoint(),
            ],
        ),
    ).run()

    assert "src/hello.txt" in bash.execute(["git", "-C", dir, "diff", "master..automate"]).output
