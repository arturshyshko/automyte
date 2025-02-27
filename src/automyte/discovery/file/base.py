from __future__ import annotations

import abc
import typing as t


class File(abc.ABC):
    @property
    def folder(self) -> str:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    def get(self) -> t.Self:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError

    def contains(self, text: str) -> bool:
        raise NotImplementedError

    def move(self, to: str | None = None, new_name: str | None = None) -> File:
        raise NotImplementedError

    def get_contents(self) -> str:
        raise NotImplementedError

    def edit(self, text: str) -> File:
        raise NotImplementedError

    def delete(self) -> File:
        raise NotImplementedError

    @property
    def is_tainted(self) -> bool:
        raise NotImplementedError
