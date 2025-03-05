import typing as t
from dataclasses import dataclass

SupportedVCS: t.TypeAlias = t.Literal["git"]


@dataclass
class VCSConfig:
    default_vcs: SupportedVCS
    main_branch: str = "master"
    work_branch: str = "automate"
    dont_disrupt_prior_state: bool = True

    @classmethod
    def get_default(cls, **kwargs):
        kwargs.setdefault("default_vcs", "git")
        kwargs.setdefault("main_branch", "master")
        kwargs.setdefault("work_branch", "automate")
        kwargs.setdefault("dont_disrupt_prior_state", True)

        return cls(**kwargs)
