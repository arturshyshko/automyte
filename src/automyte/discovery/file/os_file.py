from __future__ import annotations

import os
import typing as t
from pathlib import Path

from .base import File


class OSFile(File):
    def __init__(self, fullname: str):
        self._initial_location = fullname
        self._location = fullname

        self._inital_contents: str | None = None
        self._contents: str | None = None

        self._marked_for_delete: bool = False
        self.tainted: bool = False

    @property
    def folder(self) -> str:
        return str(Path(self._location).parent)

    @property
    def name(self) -> str:
        return str(Path(self._location).name)

    def read(self) -> "OSFile":
        with open(self._location, "r") as physical_file:
            self._inital_contents = physical_file.read()
            self._contents = self._inital_contents

        return self

    def flush(self) -> None:
        with open(self._location, "w") as physical_file:
            physical_file.write(self.get_contents())

    def contains(self, text: str) -> bool:
        return text in (self._contents or "")

    def move(self, to: str | None = None, new_name: str | None = None) -> File:
        self._location = str(Path(to or self.folder) / (new_name or self.name))
        self.tainted = True
        return self

    def get_contents(self) -> str:
        if self._contents is None:
            self.read()

        return self._contents or ""

    def edit(self, text: str) -> File:
        self._contents = text
        self.tainted = True
        return self

    def delete(self) -> File:
        self._marked_for_delete = True
        self.tainted = True
        return self

    @property
    def is_tainted(self) -> bool:
        return self.tainted

    def __str__(self):
        return self._initial_location
