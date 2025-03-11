from pathlib import Path


def parse_dir(directory: str | Path) -> Path:
    if isinstance(directory, str):
        path = Path(directory).expanduser()
    else:
        path = directory.expanduser()

    if not path.is_dir():
        raise ValueError(f"Received invalid directory: {directory}.")

    return path
