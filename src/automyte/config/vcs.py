import typing as t
from dataclasses import dataclass, field

import typing_extensions as te

from . import fields as f
from .fields import SupportedVCS, VCSConfigParams


@dataclass
class VCSConfig:
    default_vcs: SupportedVCS = field(default="git", metadata=f.DEFAULT_VCS.to_dict())
    base_branch: str = field(default="master", metadata=f.BASE_BRANCH.to_dict())
    work_branch: str = field(default="automate", metadata=f.WORK_BRANCH.to_dict())
    dont_disrupt_prior_state: bool = field(default=True, metadata=f.DONT_DISRUPT_PRIOR_STATE.to_dict())
    allow_publishing: bool = field(default=False, metadata=f.ALLOW_PUBLISHING.to_dict())

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
