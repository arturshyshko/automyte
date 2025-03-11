import re

from automyte import Automaton, File, LocalFilesExplorer, Project, RunContext
from automyte.discovery import ContainsFilter, PathFilter
from automyte.tasks import fs, vcs
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


def test_file_filtering(tmp_git_repo):
    directory = tmp_git_repo(
        {
            "src": {
                "some_python_file.py": file_contents,
                "models": {
                    "model.py": file_contents,
                },
                "README.md": "Trying to remove 'if smth is True:' from all python files.",
            },
        }
    )

    Automaton(
        name="filter_files",
        projects=[
            Project(
                explorer=LocalFilesExplorer(
                    rootdir=directory,
                    filter_by=(ContainsFilter("is True") & PathFilter(filename=".*.py") & ~PathFilter(folder="models")),
                )
            ),
        ],
        tasks=[
            remove_redundant_is_true_comparisons,
            fs.flush(),
            vcs.add("src"),
            vcs.commit("Remove unnecessary 'is True' comparisons, only in python files."),
        ],
    ).run()

    bash.execute(["git", "-C", directory, "checkout", "automate"])

    with open(f"{directory}/src/some_python_file.py", "r") as file_to_change:
        assert file_to_change.read() == expected_new_contents
    with open(f"{directory}/src/models/model.py", "r") as model_file:
        assert model_file.read() == file_contents
    with open(f"{directory}/src/README.md", "r") as readme_file:
        assert readme_file.read() == "Trying to remove 'if smth is True:' from all python files."
