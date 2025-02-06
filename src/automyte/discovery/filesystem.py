import mmap
import os
from pathlib import Path


class OSFile:
    def __init__(self, folder: str, filename: str) -> None:
        self.folder = folder
        self.filename = filename

    @property
    def path(self):
        return Path(self.folder) / self.filename

    def read_content(self):
        with open(self.path, 'r') as f:
            return f.read()

    def create(self, code: str | None = None):
        with open(self.path, 'w') as f:
            if code is not None:
                f.write(code)

            return self

    def rewrite(self, code: str):
        return self.create(code=code)

    def move(self, to: str | None = None, new_name: str | None = None):
        new_folder_path = Path(to or self.folder)
        new_filename = new_name or self.filename
        assert not all(arg is None for arg in (to, new_name)), "Must provide either new folder or new filename."

        os.rename(src=self.path, dst=new_folder_path/new_filename)

        self.folder = new_folder_path
        self.filename = new_filename
        return self

    def delete(self):
        os.remove(self.path)

    def contains(self, text: str):
        with open(self.path, 'rb') as file:
            try:
                with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                    if s.find(text.encode()) != -1:
                        return True
            except ValueError:  # ValueError: cannot mmap an empty file - if file is empty - don't mmap it.
                return False

        return False

    def __str__(self) -> str:
        return str(self.path)
