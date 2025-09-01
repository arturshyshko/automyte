from unittest.mock import patch

from dataclasses import is_dataclass
from automyte.config.builders.metadata_parser import ConfigMetadataParser
from automyte.config.config import Config
from automyte.config.fields import CONFIG_FIELDS, VCS_FIELDS
from automyte.discovery.file.os_file import OSFile


class TestConfigSetup:
    cfg_file_contents = """
    [config]
    mode = amend
    stop_on_fail = false

    [vcs]
    allow_publishing = true
    """

    def assert_defaults_preserved(self, config, overriden_fields):
        default_value_fields = [f for f in CONFIG_FIELDS if f.name not in overriden_fields]
        for field in default_value_fields:
            assert getattr(config, field.name) == field.default_value

        default_value_fields = [f for f in VCS_FIELDS if f.name not in overriden_fields]
        for field in default_value_fields:
            assert getattr(config.vcs, field.name) == field.default_value

    def test_apply_config_from_file(self, tmp_os_file):
        file: OSFile = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")

        result = Config.setup(config_file_path=file.fullpath)

        assert result.mode == "amend"
        assert result.stop_on_fail is False
        assert result.vcs.allow_publishing

        self.assert_defaults_preserved(config=result, overriden_fields=("mode", "stop_on_fail", "allow_publishing"))

    def test_apply_config_from_env_vars(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_MODE", "amend")
        monkeypatch.setenv("AUTOMYTE_STOP_ON_FAIL", "false")
        monkeypatch.setenv("AUTOMYTE_BASE_BRANCH", "main")
        monkeypatch.setenv("AUTOMYTE_ALLOW_PUBLISHING", "true")

        result = Config.setup()

        assert result.mode == "amend"
        assert result.stop_on_fail is False
        assert result.vcs.allow_publishing
        assert result.vcs.base_branch == "main"

        self.assert_defaults_preserved(
            config=result, overriden_fields=("mode", "stop_on_fail", "allow_publishing", "base_branch")
        )

    @patch("sys.argv", ["automyte", "--mode", "amend"])
    def test_apply_config_from_args(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_READ_CMD_ARGS", "true")

        result = Config.setup()

        assert result.mode == "amend"
        self.assert_defaults_preserved(config=result, overriden_fields=("mode"))

    def test_env_var_overrides_file_config(self, monkeypatch, tmp_os_file):
        file: OSFile = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")
        monkeypatch.setenv("AUTOMYTE_MODE", "run")
        monkeypatch.setenv("AUTOMYTE_ALLOW_PUBLISHING", "false")
        monkeypatch.setenv("AUTOMYTE_BASE_BRANCH", "main")

        result = Config.setup(config_file_path=file.fullpath)

        assert result.mode == "run"
        assert result.stop_on_fail is False
        assert result.vcs.allow_publishing is False
        assert result.vcs.base_branch == "main"

        self.assert_defaults_preserved(
            config=result, overriden_fields=("mode", "stop_on_fail", "allow_publishing", "base_branch")
        )

    @patch("sys.argv", ["automyte", "-m", "run", "-t", "skipped"])
    def test_args_overrides_all_config_inputs(self, monkeypatch, tmp_os_file):
        file: OSFile = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")
        monkeypatch.setenv("AUTOMYTE_TARGET", "new")
        monkeypatch.setenv("AUTOMYTE_ALLOW_PUBLISHING", "false")

        monkeypatch.setenv("AUTOMYTE_READ_CMD_ARGS", "true")

        result = Config.setup(config_file_path=file.fullpath, config_overrides={})

        assert result.mode == "run"
        assert result.target == "skipped"
        assert result.vcs.allow_publishing is False

        self.assert_defaults_preserved(
            config=result, overriden_fields=("mode", "stop_on_fail", "allow_publishing", "target")
        )
