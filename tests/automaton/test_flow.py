from unittest.mock import ANY, patch

import pytest

from automyte import Project, TasksFlow
from automyte.automaton.run_context import RunContext
from automyte.automaton.types import TaskReturn
from automyte.discovery.file.base import File
from automyte.discovery.file.os_file import OSFile
from automyte.history.types import AutomatonRunResult


def dummy_task(ctx: RunContext, file: File | None):
    return


def dummy_task2(ctx: RunContext, file: File | None):
    return


class TestFlowInit:
    def test_correctly_sets_tasks(self):
        flow = TasksFlow(
            dummy_task,
            dummy_task,
            [dummy_task, dummy_task],
            preprocess=[dummy_task, dummy_task],
            postprocess=[dummy_task, dummy_task],
        )

        assert len(flow.tasks) == 4
        assert len(flow.preprocess_tasks) == 2
        assert len(flow.postprocess_tasks) == 2

    def test_tasks_are_ordered_correctly(self):
        tasks = iter(TasksFlow(dummy_task, dummy_task2, [dummy_task2, dummy_task], dummy_task2).tasks)

        assert next(tasks) is dummy_task
        assert next(tasks) is dummy_task2
        assert next(tasks) is dummy_task2
        assert next(tasks) is dummy_task
        assert next(tasks) is dummy_task2


class TestFlowExecute:
    def test_tasks_calls_ordering(self, tmp_local_project_factory, run_ctx):
        outputs = []
        preprocess = lambda ctx, file: outputs.append("preprocess")
        postprocess = lambda ctx, file: outputs.append("postprocess")
        normal_task = lambda ctx, file: outputs.append("normal task")
        ctx = run_ctx(dir=tmp_local_project_factory({"hello.txt": "hello flow"}))

        TasksFlow([normal_task], preprocess=[preprocess], postprocess=[postprocess]).execute(ctx.project, ctx)

        assert outputs[0] == "preprocess"
        assert outputs[1] == "normal task"
        assert outputs[2] == "postprocess"

    def test_saves_task_returns_to_ctx(self, tmp_local_project_factory, run_ctx):
        expected_return = TaskReturn(instruction="continue", status="processed", value="smth")
        task = lambda ctx, file: expected_return
        ctx = run_ctx(dir=tmp_local_project_factory({"hello.txt": "hello flow"}))
        with patch("automyte.automaton.run_context.RunContext.save_task_result") as save_mock:
            TasksFlow(task).execute(ctx.project, ctx)

        save_mock.assert_called_once_with(result=expected_return, file=ANY)

    def test_plain_return_is_wrapped_as_task_return_with_correct_defaults(self, tmp_local_project_factory, run_ctx):
        task = lambda ctx, file: "smth"
        ctx = run_ctx(dir=tmp_local_project_factory({"hello.txt": "hello flow"}))

        with patch("automyte.automaton.run_context.RunContext.save_task_result") as save_mock:
            TasksFlow(task).execute(ctx.project, ctx)

        save_mock.assert_called_once_with(
            result=TaskReturn(value="smth", instruction="continue", status="processed"), file=ANY
        )

    def test_tasks_are_called_once_per_file(self, tmp_local_project_factory, run_ctx):
        files_called_for = []
        track_calls = lambda ctx, file: files_called_for.append(file.name)
        ctx = run_ctx(dir=tmp_local_project_factory({"src": {"hello.txt": "hello flow", "bye.txt": "bye flow"}}))

        TasksFlow(track_calls).execute(ctx.project, ctx)

        assert len(files_called_for) == 2
        assert next(f for f in files_called_for if f == "hello.txt")
        assert next(f for f in files_called_for if f == "bye.txt")

    def test_changes_are_applied_before_postprocess_tasks(self, tmp_local_project_factory, run_ctx):
        ctx = run_ctx(dir=tmp_local_project_factory({"src": {"hello.txt": "hello flow"}}))
        update_file = lambda ctx, file: file.edit("changed")
        read_file = lambda ctx, file: OSFile(fullname=f"{ctx.project.rootdir}/src/hello.txt").get_contents()

        TasksFlow(update_file, postprocess=[read_file]).execute(ctx.project, ctx)

        assert ctx.previous_return.value == "changed"

    def test_abort_task_instructions_return_immediately(self, tmp_local_project_factory, run_ctx):
        ctx = run_ctx(dir=tmp_local_project_factory({"src": {"hello.txt": "hello flow"}}))
        has_next_task_been_called = []
        check_if_called = lambda ctx, file: has_next_task_been_called.append("whatever, will just check falsy list")
        instruct = lambda ctx, file: TaskReturn(instruction="abort", value="oops")

        output = TasksFlow(instruct, check_if_called).execute(ctx.project, ctx)

        assert not has_next_task_been_called
        assert output == AutomatonRunResult(status="fail", error="oops")

    def test_skip_task_instructions_return_immediately(self, tmp_local_project_factory, run_ctx):
        ctx = run_ctx(dir=tmp_local_project_factory({"src": {"hello.txt": "hello flow"}}))
        has_next_task_been_called = []
        check_if_called = lambda ctx, file: has_next_task_been_called.append("whatever, will just check falsy list")
        instruct = lambda ctx, file: TaskReturn(instruction="skip")

        output = TasksFlow(instruct, check_if_called).execute(ctx.project, ctx)

        assert not has_next_task_been_called
        assert output == AutomatonRunResult(status="skipped")

    def test_exception_raised_inside_task_results_in_abort(self, tmp_local_project_factory, run_ctx):
        ctx = run_ctx(dir=tmp_local_project_factory({"src": {"hello.txt": "hello flow"}}))
        has_next_task_been_called = []
        check_if_called = lambda ctx, file: has_next_task_been_called.append("whatever, will just check falsy list")

        def failure_of_a_task(ctx, file):
            raise Exception("oops")

        output = TasksFlow(failure_of_a_task, check_if_called).execute(ctx.project, ctx)

        assert not has_next_task_been_called
        assert output == AutomatonRunResult(status="fail", error="oops")
