import csv
from pathlib import Path

import pytest

from automyte.utils.random import random_hash


@pytest.fixture
def tmp_csv_file(tmp_local_project_factory):
    def _tmp_csv_file_factory(contents: list[list], filename: str | None = None, delimiter: str = "|") -> Path:
        filename = filename or random_hash()
        dir = tmp_local_project_factory(structure={filename: ""})
        filepath = Path(dir) / filename

        with open(filepath, "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=delimiter)
            writer.writerows(contents)

        return filepath

    return _tmp_csv_file_factory
