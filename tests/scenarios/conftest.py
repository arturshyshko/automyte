import os
import typing as t
from tempfile import TemporaryDirectory
from pathlib import Path

import pytest

_DirName: t.TypeAlias = str
_FileName: t.TypeAlias = str
_FileContents: t.TypeAlias = str
_ProjectStructure: t.TypeAlias = dict[_DirName | _FileName, t.Union[_FileContents, "_ProjectStructure"]]

@pytest.fixture
def tmp_local_project_factory():
    rootdir = TemporaryDirectory()
    try:

        def _create_tmp_project(structure: _ProjectStructure, dir: str | None = None):
            if dir: os.mkdir(dir)
            current_dir = dir or rootdir.name

            for name, content in structure.items():
                if isinstance(content, str):  # Encountered a file.
                    with open(Path(current_dir)/name, 'w') as f:
                        f.write(content)
                else:  # Encoruntered a folder, so need to generate the whole structure again, recursively.
                    _create_tmp_project(structure=content, dir=f'{current_dir}/{name}')

            return rootdir.name  # Returning rootdir for the project.

        yield _create_tmp_project

    finally:
        rootdir.cleanup()
