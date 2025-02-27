import subprocess
from pathlib import Path


# TODO: Need to handle errors in the script call.
# TODO: move to bash utils.
def execute(
    command: str | list[str],
    path: str | Path | None = None,
):
    if isinstance(command, str):
        command = command.split()

    output = subprocess.run(
        command,
        cwd=path,
        shell=False,
        text=True,
        capture_output=True,
    )

    return output.stdout.strip()
