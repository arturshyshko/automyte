from dataclasses import dataclass, field

from automyte.config import Config
from automyte.config.builders import FileConfigMixin
from automyte.config.fields import ConfigField, ConfigParams, VCSConfigParams


class TestFileConfigMixin:
    cfg_file_contents = """
    [config]
    mode = run

    [vcs]
    default_vcs = git
    """

    def test_works_for_single_field(self, tmp_os_file):
        @dataclass
        class DummyConfig(FileConfigMixin):
            some_field: str = field(metadata=dict(name="mode", file_param="config.mode"))

        file = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")
        overrides = DummyConfig.parse_config_file(filepath=file.fullpath)

        assert overrides == ConfigParams(mode="run")

    def test_works_for_nested_field(self, tmp_os_file):
        @dataclass
        class NestedField(FileConfigMixin):
            some_field: str = field(metadata=dict(name="default_vcs", field_of="vcs", file_param="vcs.default_vcs"))

        @dataclass
        class DummyConfig(FileConfigMixin):
            vcs: NestedField

        file = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")
        overrides = DummyConfig.parse_config_file(filepath=file.fullpath)

        assert overrides == dict(vcs=dict(default_vcs="git"))

    def test_skips_field_without_file_param(self, tmp_os_file):
        @dataclass
        class DummyConfig(FileConfigMixin):
            mode: str = field(metadata=dict(name="mode"))

        file = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")
        overrides = DummyConfig.parse_config_file(filepath=file.fullpath)

        assert overrides == {}


class TestConfigClassParsesFile:
    cfg_file_contents = """
    [config]
    mode = run
    target = failed
    stop_on_fail = false

    [vcs]
    default_vcs = git
    base_branch = main
    work_branch = current
    dont_disrupt_prior_state = false
    allow_publishing = true
    """

    def test_cfg_file_parsing(self, tmp_os_file):
        file = tmp_os_file(self.cfg_file_contents, filename="automyte.cfg")
        overrides = Config._load_from_config_file(config_file_path=file.fullpath)

        assert overrides == ConfigParams(
            mode="run",
            target="failed",
            stop_on_fail=False,
            vcs=VCSConfigParams(
                default_vcs="git",
                base_branch="main",
                work_branch="current",
                dont_disrupt_prior_state=False,
                allow_publishing=True,
            ),
        )
