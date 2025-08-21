from pathlib import Path
from automyte.automaton import RunContext
from automyte.discovery import OSFile
from automyte.tasks import vcs
from automyte.tasks.utils import fs
from automyte.utils import bash


class TestFileSystemFlush:
    def test_calls_file_flush_when_provided(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("whatever").edit("test flushing")
        ctx: RunContext = run_ctx(file.folder)

        fs.flush()(ctx, file)

        with open(file.fullpath, "r") as disk_file:
            assert disk_file.read() == "test flushing"


class TestFileSystemCreate:
    def test_should_create_new_file_when_path_is_sent_as_string(self, run_ctx, tmp_local_project):
        dir = tmp_local_project(structure={})
        ctx: RunContext = run_ctx(dir)

        result = fs.create(f"{dir}/test/file.txt", "File Content")(ctx, None)

        assert result.status == "processed"
        assert (Path(dir) / "test/file.txt").exists()

        file: OSFile = result.value
        with open(file.fullpath, "r") as f:
            assert f.read() == "File Content"

    def test_should_create_new_file_when_path_is_sent(self, run_ctx, tmp_local_project):
        dir = tmp_local_project(structure={})
        ctx: RunContext = run_ctx(dir)

        result = fs.create(Path(f"{dir}/test/file.txt"), "File Content")(ctx, None)

        assert result.status == "processed"
        assert (Path(dir) / "test/file.txt").exists()

        file: OSFile = result.value
        with open(file.fullpath, "r") as f:
            assert f.read() == "File Content"

    def test_should_create_new_file_and_stage_it(self, run_ctx, tmp_git_repo):
        dir = tmp_git_repo({})
        ctx: RunContext = run_ctx(dir)

        result = fs.create(f"{dir}/test/file.txt", "File Content")(ctx, None)

        assert result.status == "processed"
        vcs.add("test")(ctx, result.value)
        staged_files_diff = bash.execute(["git", "-C", dir, "diff", "--name-only", "--cached"]).output
        assert "test/file.txt" in staged_files_diff
