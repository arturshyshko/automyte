from automyte.automaton import RunContext
from automyte.discovery import File


# TODO: Think of a better implementation?
class Breakpoint:
    def __call__(self, ctx: RunContext, file: File | None):
        import pdb

        pdb.set_trace()
