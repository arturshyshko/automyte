import typing as t
from dataclasses import dataclass, field

import typing_extensions as te

SupportedVCS: t.TypeAlias = t.Literal["git"]


class VCSConfigParams(t.TypedDict, total=False):
    default_vcs: SupportedVCS
    base_branch: str
    work_branch: str
    dont_disrupt_prior_state: bool
    allow_publishing: bool


@dataclass
class VCSConfig:
    default_vcs: SupportedVCS
    main_branch: str = "master"
    work_branch: str = "automate"
    dont_disrupt_prior_state: bool = True

    @classmethod
    def get_default(cls, **kwargs: te.Unpack[VCSConfigParams]):
        defaults = VCSConfigParams(
            default_vcs="git",
            base_branch="master",
            work_branch="automate",
            dont_disrupt_prior_state=True,
        )
        defaults.update(**kwargs)

        return cls(**defaults)
