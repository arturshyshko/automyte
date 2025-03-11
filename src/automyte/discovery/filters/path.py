import re
from pathlib import Path

from .base import File, Filter


class PathFilter(Filter):
    """Filter files by their filename or folder.

    `filename` is treated as regexp so it is possible to provide smth like `filename=".*.py"`
        to search for file extension for example.
    `folder` search is performed by just checking if given folder is present in file path

    If both params are passed - they are treated as "and" filter.
    """

    def __init__(
        self,
        filename: str | None = None,
        folder: str | Path | None = None,
    ) -> None:
        self.name = filename

        if isinstance(folder, Path):
            self.folder = folder
        elif isinstance(folder, str):
            self.folder = Path(folder)
        else:
            self.folder = None

    def filter(self, file: File) -> bool:
        if self.name:
            if not re.search(self.name, file.name):
                return False

        if self.folder:
            if str(self.folder) not in file.folder:
                return False

        return True
