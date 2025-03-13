import pytest

from automyte.automaton.run_context import RunContext
from automyte.automaton.types import TaskReturn
from automyte.discovery import Filter, OSFile
from automyte.tasks import flow


class TestIf:
    def test_skips_execution_if_condition_is_false(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.If(some_task, condition=False)(ctx, file)

        assert not has_been_called

    def test_runs_tasks_if_condition_is_true(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.If(some_task, condition=True)(ctx, file)

        assert has_been_called

    def test_skips_execution_if_check_is_false(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.If(some_task, check=lambda ctx, file: False)(ctx, file)

        assert not has_been_called

    def test_runs_tasks_if_check_is_true(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.If(some_task, check=lambda ctx, file: True)(ctx, file)

        assert has_been_called

    @pytest.mark.parametrize(
        "filter_result, other",
        [
            (True, "check"),
            (False, "check"),
            (True, "condition"),
            (False, "condition"),
        ],
    )
    def test_execution_according_to_filter_regardless_of_other_checks(self, run_ctx, tmp_os_file, other, filter_result):
        class DummyFilter(Filter):
            def filter(self, file):
                return filter_result

        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        wrapper = flow.If(some_task, filter=DummyFilter())
        if other == "check":
            wrapper.check = lambda ctx, file: True
        elif other == "condition":
            wrapper.condition = True
        wrapper(ctx, file)

        assert bool(has_been_called) is filter_result

    def test_properly_runs_for_multiple_tasks(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.If(some_task, some_task, condition=True)(ctx, file)

        assert len(has_been_called) == 2

    def test_stops_execution_if_one_of_the_tasks_fail(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        failure_of_a_task = lambda ctx, file: TaskReturn(instruction="skip")
        some_task = lambda ctx, file: has_been_called.append(1)

        flow.If(failure_of_a_task, some_task, condition=True)(ctx, file)
        assert not has_been_called
