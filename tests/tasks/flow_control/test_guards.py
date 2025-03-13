from automyte import Automaton, AutomatonRunResult, InMemoryHistory, OSFile, Project, RunContext, guards
from automyte.automaton.types import TaskReturn


class TestModeGuards:
    def test_run(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)
        ctx.config.mode = "run"

        assert guards.MODE.run(ctx, file)
        assert not guards.MODE.amend(ctx, file)

    def test_amend(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("hello conditional")
        ctx: RunContext = run_ctx(dir=file.folder)
        ctx.config.mode = "amend"

        assert not guards.MODE.run(ctx, file)
        assert guards.MODE.amend(ctx, file)


class TestHistoryGuards:
    def test_failed(self, run_ctx, tmp_os_file):
        ctx: RunContext = run_ctx("smth")
        ctx.previous_status = AutomatonRunResult("fail")
        file: OSFile = tmp_os_file("smth")

        assert guards.HISTORY.failed(ctx, file)

    def test_new(self, run_ctx, tmp_os_file):
        ctx: RunContext = run_ctx("smth")
        ctx.previous_status = AutomatonRunResult("new")
        file: OSFile = tmp_os_file("smth")

        assert guards.HISTORY.new(ctx, file)

    def test_skipped(self, run_ctx, tmp_os_file):
        ctx: RunContext = run_ctx("smth")
        ctx.previous_status = AutomatonRunResult("skipped")
        file: OSFile = tmp_os_file("smth")

        assert guards.HISTORY.skipped(ctx, file)

    def test_succeeded(self, run_ctx, tmp_os_file):
        ctx: RunContext = run_ctx("smth")
        ctx.previous_status = AutomatonRunResult("success")
        file: OSFile = tmp_os_file("smth")

        assert guards.HISTORY.succeeded(ctx, file)


class TestPreviousTaskGuards:
    def test_is_success(self, run_ctx, tmp_os_file):
        ctx: RunContext = run_ctx("smth")
        file: OSFile = tmp_os_file("smth")
        ctx.save_task_result(result=TaskReturn(status="processed"), file=file)

        assert guards.PREVIOUS_TASK.is_success(ctx, file)

    def test_was_skipped(self, run_ctx, tmp_os_file):
        ctx: RunContext = run_ctx("smth")
        file: OSFile = tmp_os_file("smth")
        ctx.save_task_result(result=TaskReturn(status="skipped"), file=file)

        assert guards.PREVIOUS_TASK.was_skipped(ctx, file)
