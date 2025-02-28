import typing as t
from pathlib import Path

import pytest

from automyte import OSFile
from automyte.utils.random import random_hash


@pytest.fixture
def tmp_os_file(tmp_local_project_factory):
    def _tmp_file_factory(contents: str, filename: str | None = None) -> OSFile:
        filename = filename or random_hash()
        dir = tmp_local_project_factory(structure={filename: contents})

        filepath = Path(dir) / filename
        with open(filepath, "w") as f:
            f.write(contents)

        return OSFile(fullname=str(filepath))

    return _tmp_file_factory
