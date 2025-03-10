from automyte.automaton import RunContext
from automyte.discovery import OSFile
from automyte.tasks.utils import fs


class TestFileSystemFlush:
    def test_calls_file_flush_when_provided(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("whatever").edit("test flushing")
        ctx: RunContext = run_ctx(file.folder)

        fs.flush()(ctx, file)

        with open(file.fullpath, "r") as disk_file:
            assert disk_file.read() == "test flushing"
