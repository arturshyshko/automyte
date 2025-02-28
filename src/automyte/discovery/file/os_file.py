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

    @property
    def fullpath(self) -> Path:
        return Path(self._location)

    def read(self) -> "OSFile":
        # If the file was moved before initial read - we need to read from initial location.
        current_location = self._location if self.fullpath.exists() else self._initial_location

        with open(current_location, "r") as physical_file:
            self._inital_contents = physical_file.read()
            self._contents = self._inital_contents

        return self

    def flush(self) -> None:
        if not self.tainted:
            return

        if self._marked_for_delete:
            if self.fullpath.exists():
                self.fullpath.unlink()
            return

        # If file has been moved - self._location will have been changed, so we write to new location.
        with open(self._location, "w") as physical_file:
            physical_file.write(self.get_contents())

        # Cleanup old file after move() call.
        if self._initial_location != self._location:
            Path(self._initial_location).unlink()

    def contains(self, text: str) -> bool:
        return text in self.get_contents()

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
        return self._location
