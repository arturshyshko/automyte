from unittest.mock import patch

from automyte import OSFile, RunContext
from automyte.tasks.utils import Breakpoint


class TestBreakpoint:
    def test_continues_by_default_input(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("whatever")
        ctx: RunContext = run_ctx(file.folder)

        with patch("automyte.tasks.utils.breakpoint.Breakpoint._get_input", return_value=""):
            result = Breakpoint()(ctx, file)

        assert result is None

    def test_option_d_prints_project_dir_and_waits_in_loop(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("whatever")
        ctx: RunContext = run_ctx(file.folder)

        with (
            patch("automyte.tasks.utils.breakpoint.Breakpoint._get_input", side_effect=["p", "c"]) as mock_input,
            patch("builtins.print") as mock_print,
        ):
            Breakpoint()(ctx, file)

        assert mock_input.call_count == 2
        mock_print.assert_called_once_with(file.folder)

    def test_option_a_flushes_files_and_waits_in_loop(self, run_ctx, tmp_os_file):
        file: OSFile = tmp_os_file("whatever")
        ctx: RunContext = run_ctx(file.folder)

        with (
            patch("automyte.tasks.utils.breakpoint.Breakpoint._get_input", side_effect=["a", "c"]) as mock_input,
            patch("automyte.project.project.Project.apply_changes") as apply_mock,
        ):
            Breakpoint()(ctx, file)

        assert mock_input.call_count == 2
        apply_mock.assert_called_once()
