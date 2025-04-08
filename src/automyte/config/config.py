import typing as t
from dataclasses import dataclass
from pathlib import Path

import typing_extensions as te

from .vcs import SupportedVCS, VCSConfig, VCSConfigParams

RUN_MODES = t.Literal["run", "amend"]

_ProjectID: t.TypeAlias = str
_AutomatonTarget: t.TypeAlias = t.Literal["all", "new", "successful", "failed", "skipped"]
AutomatonTarget: t.TypeAlias = _AutomatonTarget | _ProjectID


class ConfigParams(t.TypedDict, total=False):
    stop_on_fail: bool
    target: AutomatonTarget
    mode: RUN_MODES
    vcs: VCSConfigParams


@dataclass
class Config:
    mode: RUN_MODES
    vcs: VCSConfig
    stop_on_fail: bool = True
    target: AutomatonTarget = "all"

    @classmethod
    def setup(
        cls,
        config_file_path: str | Path = "./automyte.json",
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

    # TODO: Implement
    @classmethod
    def _load_from_config_file(cls, config_file_path: str | Path = "./automyte.json"):
        return {}

    # TODO: Implement (read from metadata)
    @classmethod
    def _load_from_env(cls):
        return {}

    @classmethod
    def _load_from_args(cls, config_overrides: ConfigParams | None = None):
        if not config_overrides:
            return {}

        return config_overrides
