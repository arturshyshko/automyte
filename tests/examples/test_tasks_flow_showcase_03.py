import re

from automyte import Automaton, File, Project, RunContext, TasksFlow
from automyte.tasks import flow, guards, vcs
from automyte.utils import bash

file_contents = """
some_var = True
if some_var is True:
    do_stuff()
"""

expected_new_contents = """
some_var = True
if some_var:
    do_stuff()
"""


def remove_redundant_is_true_comparisons(ctx: RunContext, file: File):
    file.edit(re.sub(r"if (\w+) is True:", r"if \1:", file.get_contents()))


def test_tasks_flow_showcase(tmp_git_repo):
    directory = tmp_git_repo({"src": {"some_python_file.py": file_contents}})

    Automaton(
        name="expanded_tasks_flow",
        projects=[directory],
        tasks=TasksFlow(
            remove_redundant_is_true_comparisons,
            preprocess=[
                flow.IgnoreResult(vcs.pull("master").flags("--rebase")),  # Ignoring fail, as I don't have remote repo
            ],
            postprocess=[
                vcs.add("src"),
                flow.If(
                    vcs.commit("Remove unnecessary 'is True' comparisons"),
                    check=guards.PREVIOUS_TASK.is_success,
                ),
            ],
        ),
    ).run()

    bash.execute(["git", "-C", directory, "checkout", "automate"])
    with open(f"{directory}/src/some_python_file.py", "r") as proj1_file:
        assert proj1_file.read() == expected_new_contents
