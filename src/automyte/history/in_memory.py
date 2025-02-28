from collections import defaultdict

from .base import History
from .types import AutomatonRunResult


class InMemoryHistory(History):
    def __init__(self) -> None:
        self.data: dict[str, AutomatonRunResult] = defaultdict(lambda: AutomatonRunResult(status="new"))

    def get_status(self, automaton_name: str, project_id: str) -> AutomatonRunResult:
        return self.data[project_id]

    def set_status(self, automaton_name: str, project_id: str, status: AutomatonRunResult):
        self.data[project_id] = status

    def read(self, automaton_name: str):
        return self.data
