from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from automyte.discovery import ProjectExplorer


class TestProjectExplorer:
    def test_all_files_returns_only_files(self):
        with TemporaryDirectory() as projectdir:
            with (
                TemporaryDirectory(dir=projectdir) as childdir,
                NamedTemporaryFile(dir=projectdir) as file1,
                NamedTemporaryFile(dir=projectdir) as file2,
            ):
                files = list(ProjectExplorer(rootdir=projectdir).all_files())

                assert next(f for f in files if str(f.path) == file1.name)
                assert next(f for f in files if str(f.path) == file2.name)
                assert next((f for f in files if str(f.path) == childdir), None) is None

    def test_all_files_does_recursive_search(self):
        with TemporaryDirectory() as projectdir:
            with TemporaryDirectory(dir=projectdir) as childdir:
                with NamedTemporaryFile(dir=childdir) as nested_file:
                    files = list(ProjectExplorer(rootdir=projectdir).all_files())

                    assert next(f for f in files if str(f.path) == nested_file.name)

    def test_all_files_filters_by_extension(self):
        with TemporaryDirectory() as projectdir:
            with NamedTemporaryFile(dir=projectdir, suffix='.pdf') as pdf_file:
                files = list(ProjectExplorer(rootdir=projectdir).all_files(extension='.pdf'))

                assert next(f for f in files if str(f.path) == pdf_file.name)

    def test_filter_contains_multiple_strings_are_treated_as_or(self):
        with TemporaryDirectory() as projectdir:
            with (
                NamedTemporaryFile(dir=projectdir) as tmp_contains1,
                NamedTemporaryFile(dir=projectdir) as tmp_contains2,
                NamedTemporaryFile(dir=projectdir) as tmp_dont_contain,
            ):
                with (
                    open(tmp_contains1.name, 'w') as contains_file1,
                    open(tmp_contains2.name, 'w') as contains_file2,
                    open(tmp_dont_contain.name, 'w') as dont_contain_file,
                ):
                    contains_file1.write("hello\nthere")
                    contains_file2.write("world")
                    dont_contain_file.write("aaaaaaa")

                files = list(ProjectExplorer(rootdir=projectdir).filter(contains=['hello', 'world']))

                assert next(f for f in files if str(f.path) == contains_file1.name)
                assert next(f for f in files if str(f.path) == contains_file2.name)
                assert len(files) == 2

    def test_filter_by_named(self):
        with TemporaryDirectory() as projectdir:
            with (
                open(str(Path(projectdir) / 'check_named.pdf'), 'x'),
                open(str(Path(projectdir) / 'incorrect.pdf'), 'x'),  # Checking just plain wrong name
                open(str(Path(projectdir) / 'check_nameddd.pdf'), 'x'),  # Checking exact match
            ):

                files = list(ProjectExplorer(rootdir=projectdir).filter(named=['check_named']))

                assert next(f for f in files if str(f.path) == str(Path(projectdir) / 'check_named.pdf'))
                assert len(files) == 1

    def test_filter_by_extension(self):
        with TemporaryDirectory() as projectdir:
            with (
                NamedTemporaryFile(dir=projectdir, suffix='.pdf') as correct,
                NamedTemporaryFile(dir=projectdir, suffix='.csv'),  # Checking just plain wrong extension
                NamedTemporaryFile(dir=projectdir, suffix='.pdff'),  # Checking exact match
            ):

                files = list(ProjectExplorer(rootdir=projectdir).filter(extension='.pdf'))

                assert next(f for f in files if str(f.path) == correct.name)
                assert len(files) == 1

    def test_filter_combination_is_treated_as_and(self):
        with TemporaryDirectory() as projectdir:
            with (
                open(str(Path(projectdir) / 'check_named.pdf'), 'w') as correct,
                open(str(Path(projectdir) / 'check_named.csv'), 'w'),  # Mismatch by extension
                open(str(Path(projectdir) / 'check_named.pdf'), 'w'),  # Mismatch by contents
            ):
                correct.write('hello\nthere')

            files = list(ProjectExplorer(rootdir=projectdir).filter(
                contains=['hello\nthere'], named=['check_named'], extension='.pdf'
            ))

            assert next(f for f in files if str(f.path) == correct.name)
            assert len(files) == 1
