from unittest.mock import patch

from automyte.config import Config
from automyte.config.mappers import FileConfigMapper
from automyte.discovery import OSFile


class TestConfigSetup:
    cfg_file_contents = """
    [config]
    mode = amend
    stop_on_fail = false

    [vcs]
    allow_publishing = true
    """

    def test_apply_config_from_file(self, tmp_os_file):
        file: OSFile = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")

        config = Config()
        config._file_getter = FileConfigMapper(filepath=file.fullpath)
        config.vcs._file_getter = FileConfigMapper(filepath=file.fullpath)

        assert config.mode == "amend"
        assert config.stop_on_fail is False
        assert config.vcs.allow_publishing

    def test_apply_config_from_env_vars(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_MODE", "amend")
        monkeypatch.setenv("AUTOMYTE_STOP_ON_FAIL", "false")
        monkeypatch.setenv("AUTOMYTE_BASE_BRANCH", "main")
        monkeypatch.setenv("AUTOMYTE_ALLOW_PUBLISHING", "true")

        config = Config()

        assert config.mode == "amend"
        assert config.stop_on_fail is False
        assert config.vcs.allow_publishing
        assert config.vcs.base_branch == "main"

    @patch("sys.argv", ["automyte", "--mode", "amend", "-dd", "false"])
    def test_apply_config_from_args(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_CLI_MODE", "true")

        config = Config()

        assert config.mode == "amend"
        assert config.vcs.dont_disrupt_prior_state is False

    def test_apply_config_from_direct_init(self):
        config = Config(target="skipped")
        assert config.target == "skipped"

    @patch("sys.argv", ["automyte", "--target", "skipped"])
    def test_override_ordering(self, tmp_os_file, monkeypatch):
        config = Config()
        assert config.target == "all"  # Checking default value fallback.

        config = Config()
        file: OSFile = tmp_os_file("[config]\ntarget = new", filename="automyte.cfg")
        config._file_getter = FileConfigMapper(filepath=file.fullpath)
        assert config.target == "new"  # File overrides default value.

        monkeypatch.setenv("AUTOMYTE_TARGET", "failed")
        config = Config()
        config._file_getter = FileConfigMapper(filepath=file.fullpath)
        assert config.target == "failed"  # Env vars override file.

        monkeypatch.setenv("AUTOMYTE_CLI_MODE", "true")
        config = Config()
        config._file_getter = FileConfigMapper(filepath=file.fullpath)
        assert config.target == "skipped"  # Cli args override env vars.

        config = Config(target="successful")
        config._file_getter = FileConfigMapper(filepath=file.fullpath)
        assert config.target == "successful"  # Direct assignment by user overrides everything.
