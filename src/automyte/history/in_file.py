import csv
import logging
import os
import typing as t
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .base import History
from .types import AutomatonRunResult, ProjectID, RunStatus

logger = logging.getLogger(__name__)


class InFileHistory(History):
    """Store automatons runs for projects in a csv file.

    If history filename is reused between automatons - data will just be appended and separated for automatons,
        not overriden or lost.
    File extension doesn't matter, internally, file structure is csv.
    Users are free to manipulate that file manually, for manual overrides.
    """

    def __init__(self, filename: str | Path | None = None) -> None:
        """Setup new instance of in-file history.

        If filename is a directory - will create a new "automyte_history.csv" file there;
        If filename is a full path to a file - will either override/read contents or create new file with that name,
            as long as the parent folder of that file exists.

        Can set filename to either None, "./", "current", "local" to create history file in the script launch dir.
        """
        self.filepath = self._set_storage_path(filename)
        self.file_io = _HistoryFileIO(filepath=self.filepath)

    def get_status(self, automaton_name: str, project_id: str) -> AutomatonRunResult:
        return self.file_io.get_automaton_history(automaton_name=automaton_name).get(
            project_id, AutomatonRunResult("new", error=None)
        )

    def set_status(self, automaton_name: str, project_id: str, status: AutomatonRunResult):
        self.file_io.save_project_run(automaton_name=automaton_name, project_id=project_id, run_result=status)

    def read(self, automaton_name: str):
        if not self.filepath.parent.exists():
            logger.error("[History %s]: Folder %s doesn't exist.", automaton_name, self.filepath)
            raise ValueError(f"Path {self.filepath} does not exist")

        return self.file_io.get_automaton_history(automaton_name=automaton_name)

    def _set_storage_path(self, filepath: str | Path | None):
        result = Path(os.getcwd())

        if isinstance(filepath, str):
            if filepath == "." or filepath == "./" or filepath == "current" or filepath == "local":
                pass
            else:
                result = Path(filepath)

        elif isinstance(filepath, Path):
            result = filepath

        if result.is_dir():
            result = result / "automyte_history.csv"
        return result


@dataclass
class _AutomatonHistoryInstance:
    automaton_name: str
    projects: dict[ProjectID, AutomatonRunResult]


class _HistoryFileIO:
    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.separator = "|"

    def save_project_run(self, automaton_name: str, project_id: ProjectID, run_result: AutomatonRunResult):
        history_instances = {
            automaton: _AutomatonHistoryInstance(automaton_name=automaton, projects=projects)
            for automaton, projects in self._parse_file().items()
        }

        if not history_instances.get(automaton_name):
            history_instances[automaton_name] = _AutomatonHistoryInstance(
                automaton_name=automaton_name, projects={project_id: run_result}
            )
        else:
            history_instances[automaton_name].projects[project_id] = run_result

        self._update_history_file(all_automatons_histories=list(history_instances.values()))

    def get_automaton_history(self, automaton_name: str) -> dict[ProjectID, AutomatonRunResult]:
        data = self._parse_file()
        return data.get(automaton_name, {})

    def _parse_file(self) -> dict[str, dict[ProjectID, AutomatonRunResult]]:
        history_instances: t.DefaultDict[str, dict[ProjectID, AutomatonRunResult]] = defaultdict(dict)

        if not self.filepath.exists():
            self.filepath.touch()
            return {}

        with open(self.filepath, "r") as csv_file:
            reader = csv.reader(csv_file, delimiter=self.separator)
            # Skipping header, as we don't care.
            next(reader)

            for automaton_name, project_id, status, error in reader:
                if status not in ("fail", "success", "skipped", "running", "new"):
                    logger.error(
                        "[History %s]: Failed to parse history file - wrong project status: %s.",
                        automaton_name,
                        status,
                    )
                    raise ValueError(f"Incorrect project status in history file: {status}")
                history_instances[automaton_name][project_id] = AutomatonRunResult(status=status, error=error or None)

        return history_instances

    def _update_history_file(self, all_automatons_histories: list[_AutomatonHistoryInstance]):
        with open(self.filepath, "w") as csv_file:
            writer = csv.DictWriter(
                csv_file, delimiter=self.separator, fieldnames=["automaton", "project", "status", "error"]
            )
            writer.writeheader()

            for automaton_history in all_automatons_histories:
                writer.writerows(
                    [
                        {
                            "automaton": automaton_history.automaton_name,
                            "project": project_id,
                            "status": run_result.status,
                            "error": run_result.error,
                        }
                        for project_id, run_result in automaton_history.projects.items()
                    ]
                )
