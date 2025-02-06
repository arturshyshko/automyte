from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from automyte.discovery import OSFile


class TestOSFile:
    @pytest.fixture(autouse=True)
    def parent_dir(self):
        with TemporaryDirectory() as tmp_dir:
            yield tmp_dir

    def test_create_saves_file(self, parent_dir):
        OSFile(folder=parent_dir, filename='check_create.py').create(code="hello")

        with open(Path(parent_dir) / 'check_create.py', 'r') as target:
            assert target.read() == "hello"

    def test_create_without_code_creates_empty_file(self, parent_dir):
        OSFile(folder=parent_dir, filename='check_create.py').create()

        with open(Path(parent_dir) / 'check_create.py', 'r') as target:
            assert target.read() == ''

    def test_read_content_reads(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_read.py').create(code="hello")
        assert file.read_content() == "hello"

    def test_move_changes_filename_and_folder(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_move.py').create()
        with TemporaryDirectory() as new_dir:
            file.move(to=new_dir, new_name='checked_move.py')

            assert (Path(new_dir) / 'checked_move.py').is_file()

    def test_move_updates_osfile_internal_path_state(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_move.py').create()
        with TemporaryDirectory() as new_dir:
            file.move(to=new_dir, new_name='checked_move.py')

        assert file.path == Path(new_dir) / 'checked_move.py'

    def test_move_doesnt_update_contents(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_move.py').create(code='dont change')
        with TemporaryDirectory() as new_dir:
            file.move(to=new_dir, new_name='checked_move.py')

            assert file.read_content() == 'dont change'

    def test_contains_positive(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_contains.py').create('hello\nthere')
        assert file.contains('here')

    def test_contains_negative(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_contains.py').create('hello\nthere')
        assert file.contains('aa') is False

    def test_contains_works_for_an_empty_file(self, parent_dir):
        file = OSFile(folder=parent_dir, filename='check_contains.py').create()
        assert file.contains('a') is False
