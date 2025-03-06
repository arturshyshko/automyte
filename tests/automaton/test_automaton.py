import contextlib

import pytest

from automyte import Automaton
from automyte.automaton.flow import TasksFlow
from automyte.config import Config
from automyte.discovery import ProjectExplorer
from automyte.discovery.file.os_file import OSFile
from automyte.history.in_memory import InMemoryHistory
from automyte.history.types import AutomatonRunResult
from automyte.project.project import Project
from automyte.vcs import VCS


class DummyExplorer(ProjectExplorer):
    def get_rootdir(self) -> str:
        return "smth"

    def set_rootdir(self, newdir: str):
        return "smth"

    def flush(self):
        self.flushed = True

    def explore(self):
        yield OSFile(fullname="smth/hello.txt")


class DummyVCS(VCS):
    def run(self, *args):
        return

    @contextlib.contextmanager
    def preserve_state(self, config):
        self.preserve_state_called = True
        yield "newdir"


class TestAutomatonInit:
    def test_accepts_plain_list_of_tasks(self):
        dummy_task = lambda ctx, file: ...
        flow = Automaton(name="auto", projects=[], tasks=[dummy_task, dummy_task]).flow

        assert isinstance(flow, TasksFlow)
        assert len(flow.preprocess_tasks) == 0
        assert len(flow.postprocess_tasks) == 0

        assert flow.tasks[0] is dummy_task
        assert flow.tasks[1] is dummy_task


class TestAutomatonTargetting:
    @pytest.mark.parametrize(
        "target, expected_projects",
        [
            ("all", ["proj_new", "proj_fail", "proj_success", "proj_skipped", "proj_not_in_history", "custom_id"]),
            ("new", ["proj_new", "proj_not_in_history", "custom_id"]),
            ("failed", ["proj_fail"]),
            ("skipped", ["proj_skipped"]),
            ("successful", ["proj_success"]),
        ],
    )
    def test_appropriate_targetting_filtering(self, target, expected_projects):
        ran_for = []
        mark_project = lambda ctx, file: ran_for.append(ctx.project.project_id)

        history = InMemoryHistory()
        history.set_status("auto", "proj_new", AutomatonRunResult(status="new"))
        history.set_status("auto", "proj_fail", AutomatonRunResult(status="fail"))
        history.set_status("auto", "proj_success", AutomatonRunResult(status="success"))
        history.set_status("auto", "proj_skipped", AutomatonRunResult(status="skipped"))
        history.set_status("auto", "custom_id", AutomatonRunResult(status="new"))

        config = Config.get_default()
        config.target = target

        Automaton(
            "auto",
            history=history,
            config=config,
            projects=[
                Project("proj_new", explorer=DummyExplorer(), vcs=DummyVCS()),
                Project("proj_fail", explorer=DummyExplorer(), vcs=DummyVCS()),
                Project("proj_success", explorer=DummyExplorer(), vcs=DummyVCS()),
                Project("proj_skipped", explorer=DummyExplorer(), vcs=DummyVCS()),
                Project("proj_not_in_history", explorer=DummyExplorer(), vcs=DummyVCS()),
                Project("custom_id", explorer=DummyExplorer(), vcs=DummyVCS()),
            ],
            tasks=TasksFlow(postprocess=[mark_project]),
        ).run()

        assert sorted(ran_for) == sorted(expected_projects)

    def test_targetting_by_target_id(self):
        ran_for = []
        mark_project = lambda ctx, file: ran_for.append(ctx.project.project_id)

        config = Config.get_default()
        config.target = "somecustomid"

        Automaton(
            "auto",
            config=config,
            projects=[Project("somecustomid", explorer=DummyExplorer(), vcs=DummyVCS())],
            tasks=TasksFlow(postprocess=[mark_project]),
        ).run()

        assert ran_for == ["somecustomid"]


class TestAutomatonUpdatesHistory:
    def test_updates_history(self, tmp_local_project_factory):
        successful_task = lambda ctx, file: True
        history = InMemoryHistory()

        Automaton(
            "auto",
            history=history,
            projects=[Project("proj1", explorer=DummyExplorer(), vcs=DummyVCS())],
            tasks=[successful_task],
        ).run()

        assert history.get_status("auto", "proj1").status == "success"

    def test_updates_history_for_fail(self, tmp_local_project_factory):
        history = InMemoryHistory()

        def failed_task(ctx, file):
            raise Exception("oops")

        Automaton(
            "auto",
            history=history,
            projects=[Project("proj1", explorer=DummyExplorer(), vcs=DummyVCS())],
            tasks=[failed_task],
        ).run()

        assert history.get_status("auto", "proj1") == AutomatonRunResult(status="fail", error="oops")
