from __future__ import annotations

import typing as t
from dataclasses import dataclass

RUN_MODES = t.Literal["run", "amend"]
_ProjectID: t.TypeAlias = str
AutomatonTarget: t.TypeAlias = t.Literal["all", "new", "successful", "failed", "skipped"] | _ProjectID
SupportedVCS: t.TypeAlias = t.Literal["git"]


@dataclass
class ConfigField:
    name: str
    default_value: t.Any
    kind: t.Any
    description: str
    argnames: list[str] | None  # If argnames is not present - this field will not be configurable via cli.
    env_var: str | None = None
    field_of: t.Literal["config", "vcs"] = "config"


#################################################################
# Actual definitions for all config fields.
#################################################################

MODE = ConfigField(name="mode", argnames=["-m", "--mode"], default_value=..., kind=RUN_MODES, description="")
STOP_ON_FAIL = ConfigField(
    name="stop_on_fail", argnames=["-sf", "--stop-on-fail"], default_value=True, kind=bool, description=""
)
TARGET = ConfigField(
    name="target", argnames=["-t", "--target"], default_value="all", kind=AutomatonTarget | _ProjectID, description=""
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
)
BASE_BRANCH = ConfigField(
    field_of="vcs",
    name="base_branch",
    argnames=None,
    default_value="master",
    kind=str,
    description="",
)
WORK_BRANCH = ConfigField(
    field_of="vcs",
    name="work_branch",
    argnames=None,
    default_value="automate",
    kind=str,
    description="",
)
DONT_DISRUPT_PRIOR_STATE = ConfigField(
    field_of="vcs",
    name="dont_disrupt_prior_state",
    argnames=["-dd", "--dont-disrupt"],
    default_value=True,
    kind=bool,
    description="",
)
ALLOW_PUBLISHING = ConfigField(
    field_of="vcs",
    name="allow_publishing",
    argnames=["-p", "--publish"],
    default_value=False,
    kind=bool,
    description="",
)


CONFIG_FIELDS = (MODE, STOP_ON_FAIL, TARGET)
VCS_FIELDS = (DEFAULT_VCS, BASE_BRANCH, WORK_BRANCH, DONT_DISRUPT_PRIOR_STATE, ALLOW_PUBLISHING)
