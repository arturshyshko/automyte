from dataclasses import dataclass, field
from pathlib import Path

import typing_extensions as te

from . import fields as f
from .builders import FileConfigMixin, EnvVarsConfigMixin
from .fields import RUN_MODES, AutomatonTarget, ConfigParams
from .vcs import VCSConfig


@dataclass
class Config(FileConfigMixin, EnvVarsConfigMixin):
    mode: RUN_MODES = field(metadata=f.MODE.to_dict())
    vcs: VCSConfig
    stop_on_fail: bool = field(default=True, metadata=f.STOP_ON_FAIL.to_dict())
    target: AutomatonTarget = field(default="all", metadata=f.TARGET.to_dict())

    @classmethod
    def setup(
        cls,
        config_file_path: str | Path = "./automyte.cfg",
        config_overrides: ConfigParams | None = None,
    ):
        """
        Set up configuration with the following precedence order:
            1. Command line arguments (actually handled by cmd parser, we just get config_overrides)
            2. Environment variables
            3. Config file
            4. Default values in class definition
        """
        config_values: ConfigParams = {}
        config_values.update(cls._load_from_config_file(config_file_path))
        config_values.update(cls._load_from_env())
        config_values.update(cls._load_from_args(config_overrides=config_overrides))
        config = cls.get_default(**config_values)

        return config

    @classmethod
    def get_default(cls, **kwargs: te.Unpack[ConfigParams]):
        defaults = ConfigParams(
            mode="run",
            stop_on_fail=True,
        )
        defaults.update(**kwargs)
        vcs_defaults = defaults.pop("vcs", {})

        return cls(
            vcs=VCSConfig.get_default(**vcs_defaults),
            **defaults,  # pyright: ignore (vcs already assigned)
        )

    def set_vcs(self, **kwargs):
        self.vcs = VCSConfig.get_default(**kwargs)
        return self

    @classmethod
    def _load_from_config_file(cls, config_file_path: str | Path = "./automyte.cfg") -> ConfigParams:
        return cls.parse_config_file(Path(config_file_path).resolve())

    @classmethod
    def _load_from_env(cls) -> ConfigParams:
        return cls.parse_env_vars()

    @classmethod
    def _load_from_args(cls, config_overrides: ConfigParams | None = None):
        if not config_overrides:
            return {}

        return config_overrides
