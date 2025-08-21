import os

from automyte.config.config import Config
from automyte.config.fields import ConfigParams


class TestConfigEnvVar:
    def test_should_read_config_from_env_var_for_single_value(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_MODE", "run")
        expected_result = ConfigParams(mode="run")

        result = Config._load_from_env()

        assert result == expected_result

    def test_should_read_config_for_env_var_for_multiple_values(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_MODE", "run")
        monkeypatch.setenv("AUTOMYTE_STOP_ON_FAIL", "false")
        monkeypatch.setenv("AUTOMYTE_TARGET", "new")
        expected_result = ConfigParams(mode="run", stop_on_fail=False, target="new")

        result = Config._load_from_env()

        assert result == expected_result

    def test_should_read_config_from_env_var_for_vcs_fields(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_DEFAULT_VCS", "git")
        monkeypatch.setenv("AUTOMYTE_BASE_BRANCH", "main")
        monkeypatch.setenv("AUTOMYTE_WORK_BRANCH", "automation")
        expected_result = ConfigParams(
            vcs={
                "default_vcs": "git",
                "base_branch": "main",
                "work_branch": "automation",
            }
        )

        result = Config._load_from_env()

        assert result == expected_result

    def test_should_read_config_from_env_for_config_and_vcs_fields(self, monkeypatch):
        monkeypatch.setenv("AUTOMYTE_STOP_ON_FAIL", "false")
        monkeypatch.setenv("AUTOMYTE_BASE_BRANCH", "main")
        expected_result = ConfigParams(stop_on_fail=False, vcs={"base_branch": "main"})

        result = Config._load_from_env()

        assert result == expected_result
