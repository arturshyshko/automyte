from pathlib import Path
from tempfile import TemporaryDirectory

from automyte import LocalFilesExplorer
from automyte.discovery.file.os_file import File, OSFile
from automyte.discovery.filters.base import Filter


class TestLocalFilesExplorerExplore:
    def test_returns_all_files_in_the_rootdir_if_no_filters_provided(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(
            {"src": {"hello.txt": "hello explorer"}, "upper": {"inner": {"nested.py": "print(123)"}}}
        )

        all_files = list(LocalFilesExplorer(rootdir=dir).explore())

        assert next((f for f in all_files if f.fullpath == Path(dir) / "src" / "hello.txt"), None)
        assert next((f for f in all_files if f.fullpath == Path(dir) / "upper" / "inner" / "nested.py"), None)

    def test_returns_only_files(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(
            {"src": {"hello.txt": "hello explorer"}, "upper": {"inner": {"nested.py": "print(123)"}}}
        )

        all_files = list(LocalFilesExplorer(rootdir=dir).explore())
        assert len(all_files) == 2

    def test_filters_files_accordingly_to_provided_filter(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(
            {"src": {"hello.txt": "hello explorer"}, "upper": {"inner": {"nested.py": "print(123)"}}}
        )

        class TMPFilter(Filter):
            def filter(self, file: File) -> bool:
                self.has_been_called = True
                return file.name == "hello.txt"

        filter = TMPFilter()
        all_files = list(LocalFilesExplorer(rootdir=dir, filter_by=filter).explore())

        assert all_files[0].name == "hello.txt"
        assert len(all_files) == 1
        assert filter.has_been_called


class TestLocalFilesExplorerRootdir:
    def test_get_rootdir_returns_proper_field(self):
        with TemporaryDirectory() as dir:
            assert LocalFilesExplorer(rootdir=dir).get_rootdir() == dir

    def test_set_rootdir_updates_it(self):
        with TemporaryDirectory() as dir:
            explorer = LocalFilesExplorer(rootdir=dir)
            explorer.set_rootdir(newdir=f"{dir}/new")
            assert explorer.get_rootdir() == f"{dir}/new"


class TestLocalFilesExplorerFlush:
    def test_flushes_tainted_files(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(
            {"src": {"hello.txt": "hello explorer"}, "upper": {"inner": {"nested.py": "print(123)"}}}
        )
        explorer = LocalFilesExplorer(rootdir=dir)
        for file in explorer.explore():
            if file.name == "hello.txt":
                file = file.edit("good bye explorer")

        explorer.flush()

        with open(f"{dir}/src/hello.txt", "r") as flushed_file:
            assert flushed_file.read() == "good bye explorer"

    def test_doesnt_change_untainted_files(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(
            {"src": {"hello.txt": "hello explorer"}, "upper": {"inner": {"nested.py": "print(123)"}}}
        )
        explorer = LocalFilesExplorer(rootdir=dir)
        for file in explorer.explore():
            if file.name == "hello.txt":
                file = file.edit("good bye explorer")

        explorer.flush()

        with open(f"{dir}/upper/inner/nested.py", "r") as nested_file:
            assert nested_file.read() == "print(123)"
