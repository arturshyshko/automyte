import abc

from .types import AutomatonRunResult, ProjectID


class History(abc.ABC):
    def set_status(self, automaton_name: str, project_id: str, status: AutomatonRunResult):
        raise NotImplementedError

    def get_status(self, automaton_name: str, project_id: str) -> AutomatonRunResult:
        raise NotImplementedError

    def read(self, automaton_name: str) -> dict[ProjectID, AutomatonRunResult]:
        """Return all project's history status"""
        raise NotImplementedError
