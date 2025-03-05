import logging
import os
import typing as t
from pathlib import Path

from ..file import File, OSFile
from ..filters import Filter
from .base import ProjectExplorer

logger = logging.getLogger(__name__)


class LocalFilesExplorer(ProjectExplorer):
    def __init__(self, rootdir: str, filter_by: Filter | None = None):
        self.rootdir = rootdir
        self.filter_by = filter_by
        self._changed_files: list[OSFile] = []

    def _all_files(self) -> t.Generator[OSFile, None, None]:
        for root, dirs, files in os.walk(self.rootdir):
            for f in files:
                yield OSFile(fullname=str(Path(root) / f)).read()

    def explore(self) -> t.Generator[OSFile, None, None]:
        for file in self._all_files():
            # Don't filter at all if no filters supplied or actually apply them
            if not self.filter_by or self.filter_by.filter(file):
                yield file

                if file.is_tainted:
                    self._changed_files.append(file)

    def get_rootdir(self) -> str:
        return self.rootdir

    def set_rootdir(self, newdir: str) -> str:
        self.rootdir = newdir
        return newdir

    def flush(self):
        logger.debug("[Explorer %s]: Flushing following files: %s", self.rootdir, self._changed_files)
        for file in self._changed_files:
            file.flush()
