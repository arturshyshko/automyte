from datetime import datetime, timedelta
from unittest.mock import patch

from automyte.automaton.run_context import RunContext
from automyte.discovery import OSFile
from automyte.tasks import vcs
from automyte.utils import bash


class TestVCSTaskAdd:
    def test_stages_files_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello add", "new_file.txt": "hello git"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")

        vcs.add("src")(ctx, file)

        staged_files_diff = bash.execute(["git", "-C", dir, "diff", "--name-only", "--cached"]).output
        assert "src/hello.txt" in staged_files_diff
        assert "src/new_file.txt" in staged_files_diff

    def test_properly_adds_command_flags_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello add"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")

        vcs.add("src").flags("--dry-run")(ctx, file)

        staged_files_diff = bash.execute(["git", "-C", dir, "diff", "--name-only", "--cached"]).output
        assert "src/hello.txt" not in staged_files_diff


class TestVCSTaskCommit:
    def test_creates_commit_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello new commit"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")
        vcs.add(".")(ctx, file)

        vcs.commit("commit #2")(ctx, file)

        commits_list = bash.execute(["git", "-C", dir, "log", "--oneline"]).output.split("\n")
        assert "commit #2" in commits_list[0]

    def test_doesnt_alter_any_other_commits_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello new commit"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")
        prev_commits = bash.execute(["git", "-C", dir, "log", "--oneline"]).output.split("\n")
        vcs.add(".")(ctx, file)

        vcs.commit("some message")(ctx, file)

        commits_list = bash.execute(["git", "-C", dir, "log", "--oneline"]).output.split("\n")
        assert len(commits_list) == len(prev_commits) + 1
        assert commits_list[1] == prev_commits[0]

    def test_properly_adds_command_flags_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello new commit"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")

        vcs.commit("commit #2").flags("--include", "src")(ctx, file)

        changed_files = bash.execute(["git", "-C", dir, "log", "-1", "--pretty=format:", "--name-only"]).output
        assert "hello.txt" in changed_files


class TestVCSTaskPush:
    def test_calls_correct_cmd_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello new commit"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")

        with patch("automyte.utils.bash.execute") as mock_execute:
            vcs.push(to="automyte123123123")(ctx, file)
            mock_execute.assert_called_once_with(["git", "-C", dir, "push", "origin", "automyte123123123"])

    def test_properly_adds_command_flags_for_git_vcs(self, tmp_git_repo, run_ctx):
        dir = tmp_git_repo(
            initial_structure={"src": {"hello.txt": "hello vcs task"}},
            unstaged_structure={"src": {"hello.txt": "hello new commit"}},
        )
        ctx = run_ctx(dir=dir)
        file = OSFile(fullname=f"{dir}/src/hello.txt")

        with patch("automyte.utils.bash.execute") as mock_execute:
            vcs.push(to="automyte123123123").flags("--force-with-lease")(ctx, file)
            mock_execute.assert_called_once_with(
                ["git", "-C", dir, "push", "--force-with-lease", "origin", "automyte123123123"]
            )
