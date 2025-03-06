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


def instruct_to_skip(ctx: RunContext, file: File):
    return TaskReturn(instruction="skip")


def instruct_to_abort(ctx: RunContext, file: File):
    return TaskReturn(instruction="abort", value="smth is wrong")


def error_out(ctx: RunContext, file: File):
    raise Exception("oops")


def second_task(ctx: RunContext, file: File):
    file.edit(re.sub(r"world", "there", file.get_contents()))


def test_skip_works_immediately_and_updates_history(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!"}})

    history = InMemoryHistory()
    Automaton(
        name="impl1",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        history=history,
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            )
        ],
        tasks=TasksFlow([instruct_to_skip, second_task]),
    ).run()

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello world!"  # Make sure it's unchanged.

    assert history.get_status("impl1", "test_project") == AutomatonRunResult(status="skipped")


def test_abort_works_immediately_and_updates_history(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!"}})

    history = InMemoryHistory()
    Automaton(
        name="impl1",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        history=history,
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            )
        ],
        tasks=TasksFlow([instruct_to_abort, second_task]),
    ).run()

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello world!"  # Make sure it's unchanged.

    assert history.get_status("impl1", "test_project") == AutomatonRunResult(status="fail", error="smth is wrong")


def test_task_exception_abort_run(tmp_local_project_factory):
    dir = tmp_local_project_factory(structure={"src": {"hello.txt": "hello world!"}})

    history = InMemoryHistory()
    Automaton(
        name="impl1",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        history=history,
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            )
        ],
        tasks=TasksFlow([error_out, second_task]),
    ).run()

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello world!"  # Make sure it's unchanged.

    assert history.get_status("impl1", "test_project") == AutomatonRunResult(status="fail", error="oops")
