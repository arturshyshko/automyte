from pathlib import Path

import pytest

from automyte.automaton.run_context import RunContext
from automyte.config.base import Config
from automyte.history.types import AutomatonRunResult
from automyte.project import Project
from automyte.utils.random import random_hash
from automyte.vcs.base import VCS


@pytest.fixture
def run_ctx():
    def _ctx_factory(
        dir: str | Path, vcs: VCS | None = None, project: Project | None = None, automaton_name: str = "auto"
    ):
        if project is None:
            project = Project(project_id=random_hash(), rootdir=str(dir))
        if vcs is None:
            vcs = project.vcs

        return RunContext(
            automaton_name=automaton_name,
            config=Config.get_default().set_vcs(dont_disrupt_prior_state=False),
            vcs=vcs,
            project=project,
            current_status=AutomatonRunResult("running"),
            previous_status=AutomatonRunResult("new"),
            global_tasks_returns=[],
            file_tasks_returns=[],
        )

    return _ctx_factory
