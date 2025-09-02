from automyte import (
    Automaton,
    ContainsFilter,
    File,
    LocalFilesExplorer,
    Project,
    RunContext,
    TasksFlow,
)
from automyte.config.fields import ConfigParams, VCSConfigParams
from automyte.discovery.file.os_file import OSFile

cfg_file_contents = """
    [config]
    mode = amend

    [vcs]
    dont_disrupt_prior_state=false
    """


def replace_text(ctx: RunContext, file: File):
    import re

    file.edit(re.sub(r"world", "there", file.get_contents()))


def test_setting_config_through_file(tmp_local_project, tmp_os_file):
    dir = tmp_local_project(
        structure={
            "src": {
                "hello.txt": "hello world!",
            },
        }
    )
    file: OSFile = tmp_os_file(cfg_file_contents, filename="automyte.cfg")

    automaton = Automaton(
        name="config_test",
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow([replace_text]),
    )
    automaton.run(config_file_path=file.fullpath)

    assert automaton.config.mode == "amend"
    assert automaton.config.vcs.dont_disrupt_prior_state is False

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello there!"


def test_setting_config_through_env_vars(tmp_local_project, monkeypatch):
    dir = tmp_local_project(
        structure={
            "src": {
                "hello.txt": "hello world!",
            },
        }
    )
    monkeypatch.setenv("AUTOMYTE_MODE", "amend")
    monkeypatch.setenv("AUTOMYTE_DONT_DISRUPT_PRIOR_STATE", "false")

    automaton = Automaton(
        name="config_test",
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow([replace_text]),
    )
    automaton.run()

    assert automaton.config.mode == "amend"
    assert automaton.config.vcs.dont_disrupt_prior_state is False

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello there!"


def test_setting_config_through_overrides(tmp_local_project):
    dir = tmp_local_project(
        structure={
            "src": {
                "hello.txt": "hello world!",
            },
        }
    )
    config_overrides = ConfigParams(mode="amend", vcs=VCSConfigParams(dont_disrupt_prior_state=False))

    automaton = Automaton(
        name="config_test",
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow([replace_text]),
    )
    automaton.run(config_overrides=config_overrides)

    assert automaton.config.mode == "amend"
    assert automaton.config.vcs.dont_disrupt_prior_state is False

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello there!"
