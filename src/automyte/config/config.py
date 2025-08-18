import os
import typing as t
from dataclasses import Field, dataclass, field
from pathlib import Path

import typing_extensions as te

from automyte.utils.config import get_fields_to_process, get_typed_value

from . import fields as f
from .builders import FileConfigMixin
from .fields import RUN_MODES, AutomatonTarget, ConfigParams
from .vcs import VCSConfig


@dataclass
class Config(FileConfigMixin):
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
    def _load_from_config_file(
        cls, config_file_path: str | Path = "./automyte.cfg"
    ) -> ConfigParams:
        return cls.parse_config_file(Path(config_file_path).resolve())

    @classmethod
    def _load_from_env(cls) -> ConfigParams:
        env_config = ConfigParams()
        # get fields configurable via env_var including nested fields for vcs
        fields_to_process: t.Sequence[Field] = get_fields_to_process(cls, "env_var")

        for f in fields_to_process:
            param = f.metadata.get("env_var", None)
            kind = f.metadata.get("kind", str)
            field_of = f.metadata.get("field_of", "config")
            field_name = f.metadata.get("name", f.name)

            value = get_typed_value(kind, os.getenv(param)) if param else None

            # explicit checking for None as value can be False
            if param and value is not None:
                if field_of == "config":
                    env_config[field_name] = value
                else:
                    if field_of not in env_config:
                        env_config[field_of] = {}
                    env_config[field_of][field_name] = value

        return env_config

    @classmethod
    def _load_from_args(cls, config_overrides: ConfigParams | None = None):
        if not config_overrides:
            return {}

        return config_overrides
