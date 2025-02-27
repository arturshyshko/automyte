import os
import typing as t
from pathlib import Path

from .base import ProjectExplorer
from .file import File, OSFile
from .filters import Filter


class LocalFilesExplorer(ProjectExplorer):
    def __init__(self, rootdir: str, filter_by: Filter | None = None):
        self.rootdir = rootdir
        self.filter_by = filter_by
        self._changed_files: list[File] = []

    def _all_files(self) -> t.Generator[File, None, None]:
        for root, dirs, files in os.walk(self.rootdir):
            for f in files:
                yield OSFile(fullname=str(Path(root) / f)).read()

    def explore(self) -> t.Generator[File, None, None]:
        for file in self._all_files():
            if not self.filter_by or self.filter_by.filter(file):  # Don't filter at all if no filters supplied.
                yield file

                if file.is_tainted:
                    self._changed_files.append(file)

    def get_rootdir(self) -> str:
        return self.rootdir

    def set_rootdir(self, newdir: str) -> str:
        self.rootdir = newdir
        return newdir

    def flush(self):
        for file in self._changed_files:
            file.flush()
