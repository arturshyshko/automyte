from automyte.automaton.run_context import RunContext
from automyte.automaton.types import TaskReturn
from automyte.discovery.file.os_file import OSFile
from automyte.tasks import conditionals as cd


class TestRunIf:
    def test_skips_execution_if_condition_is_false(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        cd.RunIf(some_task, condition=False)(ctx, file)

        assert not has_been_called

    def test_runs_tasks_if_condition_is_true(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        cd.RunIf(some_task, condition=True)(ctx, file)

        assert has_been_called

    def test_properly_runs_for_multiple_tasks(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)

        cd.RunIf(some_task, some_task, condition=True)(ctx, file)

        assert len(has_been_called) == 2

    def test_stops_execution_if_one_of_the_tasks_fail(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        failure_of_a_task = lambda ctx, file: TaskReturn(instruction="skip")
        some_task = lambda ctx, file: has_been_called.append(1)

        cd.RunIf(failure_of_a_task, some_task, condition=True)(ctx, file)
        assert not has_been_called


class TestRunOn:
    def test_skips_execution_if_condition_is_false(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)
        checker = lambda ctx, file: False

        cd.RunOn(some_task, on=checker)(ctx, file)

        assert not has_been_called

    def test_runs_tasks_if_condition_is_true(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)
        checker = lambda ctx, file: True

        cd.RunOn(some_task, on=checker)(ctx, file)

        assert has_been_called

    def test_properly_runs_for_multiple_tasks(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)

        has_been_called = []  # Will just check for faulty.
        some_task = lambda ctx, file: has_been_called.append(1)
        checker = lambda ctx, file: True

        cd.RunOn(some_task, some_task, on=checker)(ctx, file)

        assert len(has_been_called) == 2
