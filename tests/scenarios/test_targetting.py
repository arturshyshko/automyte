import pytest

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


def test_targetting_by_target_id(tmp_local_project_factory):
    rootdir1 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})
    rootdir2 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})

    history = InMemoryHistory()
    history.set_status("hello", "proj1", AutomatonRunResult(status="fail"))
    history.set_status("hello", "proj2", AutomatonRunResult(status="new"))
    filters = ContainsFilter(contains="hello")

    config = Config.get_default(target="proj1").set_vcs(dont_disrupt_prior_state=False)

    automaton = Automaton(
        name="hello",
        config=config,
        projects=[
            Project(explorer=LocalFilesExplorer(rootdir=rootdir1, filter_by=filters), project_id="proj1"),
            Project(explorer=LocalFilesExplorer(rootdir=rootdir2, filter_by=filters), project_id="proj2"),
        ],
        tasks=TasksFlow([lambda ctx, file: None]),
        history=history,
    )

    automaton.run()

    # Ran for proj1 due to target_id
    assert history.get_status("hello", "proj1") == AutomatonRunResult(status="success")
    assert history.get_status("hello", "proj2") == AutomatonRunResult(status="new")  # Never ran for proj2


@pytest.mark.parametrize(
    "initial_status, target_status",
    [
        ("fail", "failed"),
        ("skipped", "skipped"),
    ],
)
def test_targetting_by_status(tmp_local_project_factory, initial_status, target_status):
    rootdir1 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})
    rootdir2 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})

    history = InMemoryHistory()
    history.set_status("hello", "proj1", AutomatonRunResult(status=initial_status))
    history.set_status("hello", "proj2", AutomatonRunResult(status="new"))
    filters = ContainsFilter(contains="hello")

    config = Config.get_default(target=target_status).set_vcs(dont_disrupt_prior_state=False)

    automaton = Automaton(
        name="hello",
        config=config,
        projects=[
            Project(explorer=LocalFilesExplorer(rootdir=rootdir1, filter_by=filters), project_id="proj1"),
            Project(explorer=LocalFilesExplorer(rootdir=rootdir2, filter_by=filters), project_id="proj2"),
        ],
        tasks=TasksFlow([lambda ctx, file: None]),
        history=history,
    )

    automaton.run()

    # Ran for proj1 due to target='failed'
    assert history.get_status("hello", "proj1") == AutomatonRunResult(status="success")
    assert history.get_status("hello", "proj2") == AutomatonRunResult(status="new")  # Never ran for proj2
