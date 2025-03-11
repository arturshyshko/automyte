from automyte.discovery import OSFile
from automyte.discovery.filters import PathFilter


class TestPathFilter:
    def test_correct_filename_match(self, tmp_os_file):
        file: OSFile = tmp_os_file("", filename="hello.txt")

        assert PathFilter(filename="hello.txt").filter(file=file)
        assert not PathFilter("hello.py").filter(file=file)

    def test_filename_is_searched_through_regexp(self, tmp_os_file):
        file: OSFile = tmp_os_file("", filename="hello.txt")

        assert PathFilter(filename=r".*llo.*").filter(file=file)

    def test_filename_allows_searching_by_extension(self, tmp_os_file):
        file: OSFile = tmp_os_file("", filename="hello.txt")

        assert PathFilter(filename=r".*.txt").filter(file=file)

    def test_correct_folder_match(self, tmp_os_file):
        file: OSFile = tmp_os_file("", filename="hello.txt")
        other_file: OSFile = tmp_os_file("")

        assert PathFilter(folder=file.folder).filter(file=file)
        assert not PathFilter(folder=other_file.folder).filter(file=file)

    def test_partial_folder_match(self, tmp_local_project):
        dir = tmp_local_project({"src": {"nested": {"subdir": {"hello.txt": ""}}}})
        file = OSFile(fullname=f"{dir}/nested/subdir/hello.txt")

        assert PathFilter(folder="nested/subdir").filter(file=file)

    def test_if_both_name_and_folder_provided_then_match_together(self, tmp_local_project):
        dir = tmp_local_project({"src": {"nested": {"subdir": {"hello.txt": "", "bye.py": ""}}}})
        file = OSFile(fullname=f"{dir}/nested/subdir/bye.py")
        wrong_file = OSFile(fullname=f"{dir}/nested/subdir/hello.txt")

        assert PathFilter(folder="subdir", filename=r"bye.py").filter(file=file)
        assert not PathFilter(folder="subdir", filename=r"bye.py").filter(file=wrong_file)
