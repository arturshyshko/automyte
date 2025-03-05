import abc
import typing as t

from ..file import File


# NOTE: Maybe split it into FilesBackend + ProjectExplorer class, so then ProjectExplorer is responsible for filters, backend is for getting/saving files
class ProjectExplorer(abc.ABC):
    def get_rootdir(self) -> str:
        """To be overriden by child classes to provide project/vcs with access to explorer's rootdir."""
        raise NotImplementedError

    def set_rootdir(self, newdir: str) -> str:
        """To be overriden by child classes to allow project to adjust explorer dir during setup() phase."""
        raise NotImplementedError

    def explore(self) -> t.Generator[File, None, None]:
        """To be inherited from and override accessing/saving project's files logic"""
        raise NotImplementedError

    def flush(self):
        """Centralised hook to actually apply all necessary changes for all files that require it."""
        raise NotImplementedError
