import typing_extensions as te

from . import fields as f
from .fields import ConfigField, SupportedVCS
from .mappers import CMDArgsMapper, EnvVarsMapper, FileConfigMapper


class VCSConfig:
    _cmd_getter = CMDArgsMapper()
    _env_getter = EnvVarsMapper()
    _file_getter = FileConfigMapper()

    default_vcs: ConfigField[SupportedVCS] = ConfigField(
        default_value="git",
        kind=SupportedVCS,
        argnames=["--vcs"],
        env_var="AUTOMYTE_DEFAULT_VCS",
        file_param="vcs.default_vcs",
    )
    base_branch: ConfigField[str] = ConfigField(
        default_value="master",
        kind=str,
        argnames=None,
        env_var="AUTOMYTE_BASE_BRANCH",
        file_param="vcs.base_branch",
    )
    work_branch: ConfigField[str] = ConfigField(
        default_value="automate",
        kind=str,
        argnames=None,
        env_var="AUTOMYTE_WORK_BRANCH",
        file_param="vcs.work_branch",
    )
    dont_disrupt_prior_state: ConfigField[bool] = ConfigField(
        default_value=True,
        kind=bool,
        argnames=["-dd", "--dont-disrupt"],
        env_var="AUTOMYTE_DONT_DISRUPT_PRIOR_STATE",
        file_param="vcs.dont_disrupt_prior_state",
    )
    allow_publishing: ConfigField[bool] = ConfigField(
        default_value=False,
        kind=bool,
        argnames=["-p", "--publish"],
        env_var="AUTOMYTE_ALLOW_PUBLISHING",
        file_param="vcs.allow_publishing",
    )

    def __init__(
        self,
        default_vcs: SupportedVCS | None = None,
        base_branch: str | None = None,
        work_branch: str | None = None,
        dont_disrupt_prior_state: bool | None = None,
        allow_publishing: bool | None = None,
    ) -> None:
        if default_vcs is not None:
            self.default_vcs = default_vcs

        if base_branch is not None:
            self.base_branch = base_branch

        if work_branch is not None:
            self.work_branch = work_branch

        if dont_disrupt_prior_state is not None:
            self.dont_disrupt_prior_state = dont_disrupt_prior_state

        if allow_publishing is not None:
            self.allow_publishing = allow_publishing
