import os
from pathlib import Path

from automyte import OSFile


class TestOSFileGetContents:
    def test_returns_file_contents_from_the_disk(self, tmp_os_file):
        file: OSFile = tmp_os_file("osfile")
        assert file.get_contents() == "osfile"

    def test_second_call_doesnt_reread_from_the_dist(self, tmp_os_file):
        file: OSFile = tmp_os_file("osfile")
        file.get_contents()

        new_data = "new_data_shouldnt_equal_in_second_get_contents_call"
        with open(file.fullpath, "w") as disk_file:
            disk_file.write(new_data)

        assert file.get_contents() != new_data


class TestOSFileContains:
    def test_returns_true_if_text_is_in_file(self, tmp_os_file):
        file: OSFile = tmp_os_file("osfile")
        assert file.contains("os")

    def test_returns_false_if_text_is_not_in_file(self, tmp_os_file):
        file: OSFile = tmp_os_file("osfile")
        assert not file.contains("not here")


class TestOSFileEdit:
    def test_overrides_contents(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.edit(text="rev2")
        assert file.get_contents() == "rev2"

    def test_doesnt_override_disk_contents_immediately(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.edit(text="rev2")

        with open(Path(file.folder) / file.name, "r") as file_on_disk:
            assert file_on_disk.read() == "revision 1"

    def test_marks_file_as_tainted(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.edit(text="rev2")

        assert file.is_tainted


class TestOSFileDelete:
    def test_doesnt_delete_disk_file_immediately(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.delete()

        assert os.path.exists(file.fullpath)

    def test_marks_file_as_tainted(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.delete()

        assert file.is_tainted

    def test_doesnt_modify_file_contents(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.delete()

        assert file.get_contents() == "revision 1"


class TestOSFileMove:
    def test_doesnt_move_disk_file_immediately(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        old_path = file.fullpath
        file.move(new_name="newname")

        assert not os.path.exists(file.fullpath)
        assert os.path.exists(old_path)

    def test_marks_file_as_tainted(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.move(new_name="newname")

        assert file.is_tainted

    def test_doesnt_modify_file_contents(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.move(new_name="newname")

        assert file.get_contents() == "revision 1"

    def test_both_arguments_update_fullpath(self, tmp_local_project_factory):
        dir = tmp_local_project_factory({"src": {"subdir1": {"oldname.txt": "revision 1"}, "subdir2": {}}})
        file = OSFile(fullname=f"{dir}/subdir1/oldname.txt")

        file.move(to=f"{dir}/subdir2", new_name="newname.txt")

        assert file.fullpath == Path(dir) / "subdir2" / "newname.txt"


class TestOSFileFlush:
    def test_flush_overrides_disk_contents_after_edit(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.edit(text="rev2").flush()

        with open(Path(file.folder) / file.name, "r") as file_on_disk:
            assert file_on_disk.read() == "rev2"

    def test_flush_deletes_file_after_delete(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.delete().flush()

        assert not os.path.exists(file.fullpath)

    def test_flush_moves_file_to_new_location_after_move(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        file.move(new_name="newname").flush()

        assert os.path.exists(file.fullpath)

    def test_flush_removes_old_file_after_move(self, tmp_os_file):
        file: OSFile = tmp_os_file("revision 1")
        old_path = file.fullpath
        file.move(new_name="newname").flush()

        assert not os.path.exists(old_path)
