import re

from automyte import Automaton, File, Project, RunContext
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


# def test_simplest_setup(tmp_local_project):
#     directory = tmp_local_project({"src": {"some_python_file.py": file_contents}})

#     Automaton(
#         name="direct",
#         projects=[directory],
#         tasks=[
#             remove_redundant_is_true_comparisons,
#         ],
#     ).run()

#     bash.execute(["git", "-C", directory, "checkout", "automate"])
#     with open(f"{directory}/src/some_python_file.py", "r") as proj1_file:
#         assert proj1_file.read() == expected_new_contents
