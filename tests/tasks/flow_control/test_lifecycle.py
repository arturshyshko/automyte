import pytest

from automyte.automaton.run_context import RunContext
from automyte.automaton.types import TaskReturn
from automyte.discovery.file.os_file import OSFile
from automyte.tasks import flow


class TestIgnoreReturn:
    @pytest.mark.parametrize(
        "ignore_instruction, output, should_next_be_called",
        [
            ("any", "skip", True),
            ("any", "abort", True),
            ("skipped", "skip", True),
            ("skipped", "abort", False),
            ("fail", "skip", False),
            ("fail", "abort", True),
        ],
    )
    def test_ignore_matrix(self, tmp_os_file, run_ctx, ignore_instruction, output, should_next_be_called):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        failure_of_a_task = lambda ctx, file: TaskReturn(instruction=output)
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.IgnoreResult(failure_of_a_task, some_task, ignore=ignore_instruction)(ctx, file)

        assert bool(has_been_called) is should_next_be_called
