import re
from pathlib import Path

from automyte import Automaton, Config, File, Project, RunContext, VCSConfig

files_location = Path(__file__).parent.parent / "data"


def remove_redundant_is_true_comparisons(ctx: RunContext, file: File):
    file.edit(re.sub(r"if (\w+) is True:", r"if \1:", file.get_contents()))


automaton = Automaton(
    name="plain",
    config=Config(vcs=VCSConfig(dont_disrupt_prior_state=False)),
    projects=[str(files_location)],
    tasks=[
        remove_redundant_is_true_comparisons,
    ],
)

if __name__ == "__main__":
    print(files_location)
    automaton.run()
