import typing as t
from dataclasses import dataclass

from .vcs import SupportedVCS, VCSConfig

RUN_MODES = t.Literal["run", "amend"]

_ProjectID: t.TypeAlias = str
AutomatonTarget: t.TypeAlias = t.Literal["all", "new", "successful", "failed", "skipped"] | _ProjectID


@dataclass
class Config:
    mode: RUN_MODES
    vcs: VCSConfig
    stop_on_fail: bool = True
    target: AutomatonTarget = "all"

    @classmethod
    def get_default(cls, **kwargs):
        # TODO: Fix error when passing mode='run' in get_default kwargs and that gets multiple values for same arg.
        return cls(
            mode="run",
            stop_on_fail=True,
            vcs=VCSConfig.get_default(),
            **kwargs,
        )

    def set_vcs(self, **kwargs):
        self.vcs = VCSConfig.get_default(**kwargs)
        return self
