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
    TasksFlow,
    guards,
)


def test_updates_history_to_success(tmp_local_project_factory):
    rootdir1 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})
    rootdir2 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})

    history = InMemoryHistory()
    filters = ContainsFilter(contains="hello")
    automaton = Automaton(
        name="hello",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        projects=[
            Project(explorer=LocalFilesExplorer(rootdir=rootdir1, filter_by=filters), project_id="proj1"),
            Project(explorer=LocalFilesExplorer(rootdir=rootdir2, filter_by=filters), project_id="proj2"),
        ],
        tasks=TasksFlow([lambda ctx, file: None]),
        history=history,
    )

    automaton.run()

    assert history.get_status("hello", "proj1") == AutomatonRunResult(status="success")
    assert history.get_status("hello", "proj2") == AutomatonRunResult(status="success")


def test_updates_to_fail(tmp_local_project_factory):
    rootdir1 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})
    rootdir2 = tmp_local_project_factory(structure={"src": {"hello.txt": "hello there"}})

    history = InMemoryHistory()
    filters = ContainsFilter(contains="hello")
    automaton = Automaton(
        name="hello",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        projects=[
            Project(explorer=LocalFilesExplorer(rootdir=rootdir1, filter_by=filters), project_id="proj1"),
            Project(explorer=LocalFilesExplorer(rootdir=rootdir2, filter_by=filters), project_id="proj2"),
        ],
        tasks=TasksFlow([lambda ctx, file: exec('raise ValueError("forced")')]),
        history=history,
    )

    automaton.run()

    assert history.get_status("hello", "proj1") == AutomatonRunResult(status="fail", error="forced")
    # Config.stop_on_fail = True by default, so we should never reach proj2, so it should be in "not_run" status.
    assert history.get_status("hello", "proj2") == AutomatonRunResult(status="new")
