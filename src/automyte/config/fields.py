from __future__ import annotations

import typing as t
from dataclasses import dataclass

if t.TYPE_CHECKING:
    from .config import Config
    from .vcs import VCSConfig

T = t.TypeVar("T")

RUN_MODES = t.Literal["run", "amend"]

ProjectID: t.TypeAlias = str
_AutomatonTarget: t.TypeAlias = t.Literal["all", "new", "successful", "failed", "skipped"]
AutomatonTarget: t.TypeAlias = _AutomatonTarget | ProjectID
SupportedVCS: t.TypeAlias = t.Literal["git"]


@dataclass
class ConfigField(t.Generic[T]):
    default_value: t.Any
    kind: t.Any
    description: str | None = None
    argnames: list[str] | None = None  # If not present - this field will not be configurable via cli.
    env_var: str | None = None  # If not present - this field will not be configurable via env vars.
    file_param: str | None = None  # If not present - this field will not be configurable via config file.

    def __set_name__(self, config: Config | VCSConfig, name: str):
        self.name = name
        self.private_name = f"_{name}"
        self.has_been_set_flag = f"__has_{name}_been_set"

        if self.argnames:
            config._cmd_getter.setup_field(self)

        if self.env_var:
            config._env_getter.setup_field(self)

        if self.file_param:
            config._file_getter.setup_field(self)

    def __get__(self, cfg_instance: Config | VCSConfig, objtype=None) -> T:
        if getattr(cfg_instance, self.has_been_set_flag, False):
            return getattr(cfg_instance, self.private_name)

        if self.argnames is not None and (value := cfg_instance._cmd_getter.get_value(self)) is not None:
            setattr(cfg_instance, self.private_name, value)
            setattr(cfg_instance, self.has_been_set_flag, True)
            return getattr(cfg_instance, self.private_name)

        if self.env_var is not None and (value := cfg_instance._env_getter.get_value(self)) is not None:
            setattr(cfg_instance, self.private_name, value)
            setattr(cfg_instance, self.has_been_set_flag, True)
            return getattr(cfg_instance, self.private_name)

        if self.file_param is not None and (value := cfg_instance._file_getter.get_value(self)) is not None:
            setattr(cfg_instance, self.private_name, value)
            setattr(cfg_instance, self.has_been_set_flag, True)
            return getattr(cfg_instance, self.private_name)

        if self.default_value is not ...:
            setattr(cfg_instance, self.private_name, self.default_value)
            setattr(cfg_instance, self.has_been_set_flag, True)
            return getattr(cfg_instance, self.private_name)

        raise ValueError(f"Config field {self.name} doesn't seem to have any value set.")

    def __set__(self, cfg_instance: Config | VCSConfig, value: T):
        setattr(cfg_instance, self.private_name, value)
        setattr(cfg_instance, self.has_been_set_flag, True)
