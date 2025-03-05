from pathlib import Path
from unittest.mock import patch

import pytest

from automyte import Config, Git
from automyte.utils import bash


class TestGitRun:
    def test_correctly_generates_prompt(self, tmp_local_project_factory):
        dir = tmp_local_project_factory({"src": {"hello.txt": "hello there"}})

        with patch("automyte.utils.bash.execute") as mock_execute:
            Git(rootdir=dir).run("commit", "--amend", "--no-edit")
            mock_execute.assert_called_once_with(["git", "-C", dir, "commit", "--amend", "--no-edit"])

    def test_actually_runs_command(self, tmp_git_repo):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello git"}}, unstaged_structure={"src": {"hello.txt": ""}}
        )

        Git(rootdir=dir).run("add", "src")

        staged_files_diff = bash.execute(["git", "-C", dir, "diff", "--name-only", "--cached"]).output
        assert "src/hello.txt" in staged_files_diff


class TestGitPreserveState:
    def test_doesnt_disrupt_user_state(self, tmp_git_repo):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello git"}},
            unstaged_structure={"src": {"hello.txt": "don't touch me"}},
        )

        with Git(rootdir=dir).preserve_state(Config.get_default().set_vcs(work_branch="verify").vcs) as new_workdir:
            # Running commands inside new workdir, not touching old state.

            bash.execute(["git", "-C", new_workdir, "add", "src"])
            bash.execute(["git", "-C", new_workdir, "commit", "-m", "commit in worktree"])

            staged_files = bash.execute(["git", "-C", dir, "diff", "--name-only", "--cached"]).output
            assert not staged_files
            commits_count = len(bash.execute(["git", "-C", dir, "log", "--oneline"]).output.splitlines())
            assert commits_count == 1

        # Also verifying after preserve_state has exited.
        staged_files = bash.execute(["git", "-C", dir, "diff", "--name-only", "--cached"]).output
        assert not staged_files
        commits_count = len(bash.execute(["git", "-C", dir, "log", "--oneline"]).output.splitlines())
        assert commits_count == 1

    def test_creates_new_worktree(self, tmp_git_repo):
        dir = tmp_git_repo(initial_structure={"src": {"hello.txt": "hello git"}})
        initial_worktrees_count = len(bash.execute(["git", "-C", dir, "worktree", "list"]).output.splitlines())

        with Git(rootdir=dir).preserve_state(Config.get_default().set_vcs(work_branch="verify").vcs):
            worktrees_list = bash.execute(["git", "-C", dir, "worktree", "list"]).output
            assert "[verify]" in worktrees_list
            assert len(worktrees_list.split("\n")) == initial_worktrees_count + 1

    def test_removes_worktree_after_exit(self, tmp_git_repo):
        dir = tmp_git_repo(initial_structure={"src": {"hello.txt": "hello git"}})
        initial_worktrees_count = len(bash.execute(["git", "-C", dir, "worktree", "list"]).output.split("\n"))

        with Git(rootdir=dir).preserve_state(Config.get_default().set_vcs(work_branch="verify").vcs):
            ...

        worktrees_list = bash.execute(["git", "-C", dir, "worktree", "list"]).output.splitlines()
        assert len(worktrees_list) == initial_worktrees_count

    def test_creates_worktree_in_a_child_dir(self, tmp_git_repo):
        dir = tmp_git_repo(initial_structure={"src": {"hello.txt": "hello git"}})

        with Git(rootdir=dir).preserve_state(Config.get_default().set_vcs(work_branch="verify").vcs) as new_workdir:
            worktree_desc = bash.execute(["git", "-C", dir, "worktree", "list"]).output.splitlines()[1]
            assert Path(new_workdir).resolve().is_relative_to(Path(dir).resolve())
            assert new_workdir in worktree_desc

    def test_updates_and_then_resets_own_workdir(self, tmp_git_repo):
        dir = tmp_git_repo(initial_structure={"src": {"hello.txt": "hello git"}})
        git = Git(rootdir=dir)
        original_workdir = git.workdir

        with git.preserve_state(Config.get_default().set_vcs(work_branch="verify").vcs) as new_workdir:
            assert git.workdir == new_workdir
        assert git.workdir == original_workdir

    def test_does_nothing_if_dont_disrupt_config_is_false(self, tmp_git_repo):
        dir = tmp_git_repo(initial_structure={"src": {"hello.txt": "hello git"}})
        git = Git(rootdir=dir)
        original_workdir = git.workdir

        with git.preserve_state(Config.get_default().set_vcs(dont_disrupt_prior_state=False).vcs) as new_workdir:
            assert len(bash.execute(["git", "-C", dir, "worktree", "list"]).output.splitlines()) == 1
            assert new_workdir == original_workdir
