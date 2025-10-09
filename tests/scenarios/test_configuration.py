from automyte import Automaton, Config, ContainsFilter, File, LocalFilesExplorer, Project, RunContext, TasksFlow

cfg_file_contents = """
    [config]
    mode = amend

    [vcs]
    dont_disrupt_prior_state=false
    """


def replace_text(ctx: RunContext, file: File):
    import re

    if ctx.config.mode == "run":
        return

    file.edit(re.sub(r"world", "there", file.get_contents()))


def test_user_input_overrides_rest_of_the_settings(tmp_local_project, monkeypatch):
    dir = tmp_local_project(
        structure={
            "src": {
                "hello.txt": "hello world!",
            },
        }
    )
    monkeypatch.setenv("AUTOMYTE_MODE", "amend")

    automaton = Automaton(
        name="config_test",
        config=Config(mode="run"),
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow([replace_text]),
    )
    automaton.run()

    assert automaton.config.mode == "run"

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello world!"  # Make sure task got proper config value and didn' run.
