from unittest.mock import patch

import pytest

from automyte.config import fields as config_fields
from automyte.config.cmd import get_config_params_from_argv
from automyte.config.config import ConfigParams
from automyte.config.vcs import VCSConfig, VCSConfigParams


class TestConfigCmdGetConfigParamsFromArgv:
    @pytest.mark.parametrize(
        "argv",
        [
            ["automyte", "--mode", "run"],
            ["automyte", "-m", "amend"],
        ],
    )
    def test_properly_processes_mode_config_field(self, argv):
        with patch("sys.argv", argv):
            result = get_config_params_from_argv(supported_fields=[config_fields.MODE])

        assert result == ConfigParams(mode=argv[-1])

    @patch("sys.argv", ["automyte", "--vcs", "git"])
    def test_processes_nested_vcs_field(self):
        result = get_config_params_from_argv(supported_fields=[config_fields.DEFAULT_VCS])

        assert result == ConfigParams(vcs=VCSConfigParams(default_vcs="git"))

    @patch(
        "sys.argv",
        [
            "automyte",
            "--vcs",
            "git",
            "-m",
            "run",
            "-sf",
            "false",
            "-t",
            "skipped",
            "--dont-disrupt",
            "true",
            "--publish",
        ],
    )
    def test_works_for_all_supported_fields(self):
        result = get_config_params_from_argv(supported_fields=(config_fields.CONFIG_FIELDS + config_fields.VCS_FIELDS))

        assert result == ConfigParams(
            mode="run",
            stop_on_fail=False,
            target="skipped",
            vcs=VCSConfigParams(
                default_vcs="git",
                allow_publishing=True,
                dont_disrupt_prior_state=True,
            ),
        )
