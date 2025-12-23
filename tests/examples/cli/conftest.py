import os
import sys
from pathlib import Path

import pytest

cli_tests_dir = Path(__file__).parent
data_dir = Path(__file__).parent / "data"


@pytest.fixture(autouse=True)
def reset_data():
    snapshots = {p: p.read_bytes() for p in data_dir.rglob("*.py")}

    try:
        yield

    finally:
        for path, content in snapshots.items():
            path.write_bytes(content)


@pytest.fixture(autouse=True)
def add_automatons_to_syspath():
    env = os.environ.copy()
    sys.path.append(str(cli_tests_dir))
    print(123, env)
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    yield env
