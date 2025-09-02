from __future__ import annotations

import typing as t
from dataclasses import Field, dataclass

RUN_MODES = t.Literal["run", "amend"]

_ProjectID: t.TypeAlias = str
_AutomatonTarget: t.TypeAlias = t.Literal["all", "new", "successful", "failed", "skipped"]
AutomatonTarget: t.TypeAlias = _AutomatonTarget | _ProjectID
SupportedVCS: t.TypeAlias = t.Literal["git"]


class ConfigParams(t.TypedDict, total=False):
    stop_on_fail: bool
    target: AutomatonTarget
    mode: RUN_MODES
    vcs: VCSConfigParams


class VCSConfigParams(t.TypedDict, total=False):
    default_vcs: SupportedVCS
    base_branch: str
    work_branch: str
    dont_disrupt_prior_state: bool
    allow_publishing: bool


@dataclass
class ConfigField:
    name: str
    default_value: t.Any
    kind: t.Any
    description: str
    argnames: list[str] | None = None  # If not present - this field will not be configurable via cli.
    env_var: str | None = None  # If not present - this field will not be configurable via env vars.
    file_param: str | None = None  # If not present - this field will not be configurable via config file.
    field_of: t.Literal["config", "vcs"] = "config"

    def to_dict(self):
        return {
            "name": self.name,
            "default_value": self.default_value,
            "kind": self.kind,
            "description": self.description,
            "argnames": self.argnames,
            "env_var": self.env_var,
            "file_param": self.file_param,
            "field_of": self.field_of,
        }

    @classmethod
    def from_field(cls, field: Field) -> "ConfigField":
        return cls(
            name=field.name,
            default_value=field.metadata.get("default_value"),
            kind=field.metadata.get("kind"),
            description=field.metadata.get("description", ""),
            argnames=field.metadata.get("argnames", None),
            env_var=field.metadata.get("env_var", None),
            file_param=field.metadata.get("file_param", None),
            field_of=field.metadata.get("field_of", None),
        )


#################################################################
# Actual definitions for all config fields.
#################################################################

MODE = ConfigField(
    name="mode",
    argnames=["-m", "--mode"],
    default_value=...,
    kind=RUN_MODES,
    description="",
    file_param="config.mode",
    env_var="AUTOMYTE_MODE",
)
STOP_ON_FAIL = ConfigField(
    name="stop_on_fail",
    argnames=["-sf", "--stop-on-fail"],
    default_value=True,
    kind=bool,
    description="",
    file_param="config.stop_on_fail",
    env_var="AUTOMYTE_STOP_ON_FAIL",
)
TARGET = ConfigField(
    name="target",
    argnames=["-t", "--target"],
    default_value="all",
    kind=AutomatonTarget | _ProjectID,
    description="",
    file_param="config.target",
    env_var="AUTOMYTE_TARGET",
)

#################################################################
# VCS related fields.
#################################################################

DEFAULT_VCS = ConfigField(
    field_of="vcs",
    name="default_vcs",
    argnames=["--vcs"],
    default_value="git",
    kind=SupportedVCS,
    description="",
    file_param="vcs.default_vcs",
    env_var="AUTOMYTE_DEFAULT_VCS",
)
BASE_BRANCH = ConfigField(
    field_of="vcs",
    name="base_branch",
    argnames=None,
    default_value="master",
    kind=str,
    description="",
    file_param="vcs.base_branch",
    env_var="AUTOMYTE_BASE_BRANCH",
)
WORK_BRANCH = ConfigField(
    field_of="vcs",
    name="work_branch",
    argnames=None,
    default_value="automate",
    kind=str,
    description="",
    file_param="vcs.work_branch",
    env_var="AUTOMYTE_WORK_BRANCH",
)
DONT_DISRUPT_PRIOR_STATE = ConfigField(
    field_of="vcs",
    name="dont_disrupt_prior_state",
    argnames=["-dd", "--dont-disrupt"],
    default_value=True,
    kind=bool,
    description="",
    file_param="vcs.dont_disrupt_prior_state",
    env_var="AUTOMYTE_DONT_DISRUPT_PRIOR_STATE",
)
ALLOW_PUBLISHING = ConfigField(
    field_of="vcs",
    name="allow_publishing",
    argnames=["-p", "--publish"],
    default_value=False,
    kind=bool,
    description="",
    file_param="vcs.allow_publishing",
    env_var="AUTOMYTE_ALLOW_PUBLISHING",
)


CONFIG_FIELDS = (MODE, STOP_ON_FAIL, TARGET)
VCS_FIELDS = (DEFAULT_VCS, BASE_BRANCH, WORK_BRANCH, DONT_DISRUPT_PRIOR_STATE, ALLOW_PUBLISHING)
