import pdb
import typing as t

from automyte.automaton import RunContext
from automyte.discovery import File

_user_prompt = """
Please select one of the following options:
(d) - Debug (spawn pdb.set_trace() with access to task context, like ctx and file)
(a) - Apply changes (immediately flushes all files to disk, useful to inspect currect project state)
(p) - Print current project working directory
(c) - Continue (exit breakpoint, continue automaton execution)

Any options besides (c) will keep breakpoint active.
Enter your choice (default: "c"):
"""
_allowed_options = ["d", "a", "p", "c"]
_possible_options = t.Literal["d", "a", "p", "c"]


class Breakpoint:
    def __call__(self, ctx: RunContext, file: File | None):
        while True:
            choice = self._get_input(_user_prompt)
            if not choice:
                return
            elif choice not in _allowed_options:
                print(f"Invalid option selected, please enter one of: {_allowed_options}")
            else:
                match t.cast(_possible_options, choice):
                    case "c":
                        return
                    case "d":
                        pdb.set_trace()
                        return
                    case "a":
                        ctx.project.apply_changes()
                        print("Changed applied, you can inspect project state and then continue...")
                    case "p":
                        print(ctx.project.rootdir)

    def _get_input(self, text: str):
        return input(text)
