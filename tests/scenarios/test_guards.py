import typing as t

from automyte import (
    Automaton,
    Config,
    ContainsFilter,
    File,
    LocalFilesExplorer,
    Project,
    RunContext,
    TasksFlow,
    conditionals,
    guards,
)


def lol(ctx: RunContext, file: File | None):
    import re

    if file:
        file.edit(re.sub(r"world", "there", file.get_contents()))


def test_guards_simple(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!"}})

    Automaton(
        name="impl1",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow(
            [
                conditionals.RunOn(
                    lol,
                    lol,
                    lol,
                    on=guards.MODE.amend,
                ),
            ]
        ),
    ).run()

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello world!"
