import re

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


def replace(ctx: RunContext, file: File):
    file.edit(re.sub(r"world", "there", file.get_contents()))
    return file.contains("oo")


def second_task(ctx: RunContext, file: File):
    if ctx.previous_return.value is True:
        file.edit(re.sub(r"good", "bad", file.get_contents()))


def test_simple_return_with_one_file(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!"}})

    Automaton(
        name="impl1",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            )
        ],
        tasks=TasksFlow([replace, second_task]),
    ).run()

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello there!"


def test_simple_return_with_multiple_files(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!", "bye.txt": "good bye!"}})

    Automaton(
        name="impl1",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="o")),
            )
        ],
        tasks=TasksFlow([replace, second_task]),
    ).run()

    with open(f"{dir}/src/bye.txt", "r") as f:
        assert f.read() == "bad bye!"
