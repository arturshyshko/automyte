import logging
import os
import typing as t
from pathlib import Path

from automyte.utils.filesystem import parse_dir

from ..file import File, OSFile
from ..filters import Filter
from .base import ProjectExplorer

logger = logging.getLogger(__name__)

IGNORE_FILES_LIST_PATTERNS = [
    ".git",
    "node_modules/",
]


class LocalFilesExplorer(ProjectExplorer):
    def __init__(
        self,
        rootdir: str,
        filter_by: Filter | None = None,
        ignore_locations: list[str] = IGNORE_FILES_LIST_PATTERNS,
    ):
        rootdir = str(parse_dir(rootdir))
        self.rootdir = rootdir
        self.filter_by = filter_by
        self._changed_files: list[OSFile] = []
        self.ignore_locations = ignore_locations

    def _all_files(self) -> t.Generator[OSFile, None, None]:
        for root, dirs, files in os.walk(self.rootdir):
            for f in files:
                file = OSFile(fullname=str(Path(root) / f))
                if self.ignore_locations and self._should_ignore_file(file):
                    continue
                else:
                    yield file

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

    def _should_ignore_file(self, file: OSFile) -> bool:
        relative_to_rootdir_path = file.fullpath.resolve().relative_to(Path(self.rootdir).resolve())
        for pattern in self.ignore_locations:
            if pattern in str(relative_to_rootdir_path):
                return True

        return False
