import typing as t
from dataclasses import dataclass

from automyte.discovery import File

if t.TYPE_CHECKING:
    from .run_context import RunContext

InstructionForAutomaton: t.TypeAlias = t.Literal["abort", "skip", "continue"]


@dataclass
class TaskReturn:
    value: t.Any = None
    instruction: "InstructionForAutomaton" = "continue"
    status: t.Literal["processed", "skipped", "errored"] = "processed"


BaseTask: t.TypeAlias = t.Callable[["RunContext", File | None], TaskReturn | t.Any]
FileTask: t.TypeAlias = t.Callable[["RunContext", File], TaskReturn | t.Any]
