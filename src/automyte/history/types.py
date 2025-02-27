import typing as t
from dataclasses import dataclass

RunStatus: t.TypeAlias = t.Literal["fail", "success", "skipped", "running", "new"]
ProjectID: t.TypeAlias = str


@dataclass
class AutomatonRunResult:
    status: RunStatus
    error: str | None = None
