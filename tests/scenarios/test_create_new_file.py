from automyte import Automaton
from automyte.config.config import Config
from automyte.tasks import fs, vcs
from automyte.utils import bash

file_contents = """
some_var = True
if some_var is True:
    do_stuff()
"""


def test_create_new_file(tmp_git_repo):
    directory = tmp_git_repo({"src": {"README.md": "Creating new file."}})

    Automaton(
        name="create_new_file",
        config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
        projects=[directory],
        tasks=[
            fs.create("src/some_python_file.py", file_contents),
            vcs.add("src"),
            vcs.commit("Created new file."),
        ],
    ).run()

    bash.execute(["git", "-C", directory, "checkout", "automate"])

    logs = bash.execute(["git", "-C", directory, "log", "--oneline"]).output
    assert "Created new file." in logs

    with open(f"{directory}/src/some_python_file.py", "r") as proj1_file:
        assert proj1_file.read() == file_contents


def test_create_new_file_in_worktree(tmp_git_repo):
    directory = tmp_git_repo({"src": {"README.md": "Creating new file."}})

    Automaton(
        name="create_new_file_in_worktree",
        projects=[directory],
        tasks=[
            fs.create("src/some_python_file.py", file_contents),
            vcs.add("src"),
            vcs.commit("Created new file."),
        ],
    ).run()

    bash.execute(["git", "-C", directory, "checkout", "automate"])

    logs = bash.execute(["git", "-C", directory, "log", "--oneline"]).output
    assert "Created new file." in logs

    with open(f"{directory}/src/some_python_file.py", "r") as proj1_file:
        assert proj1_file.read() == file_contents
