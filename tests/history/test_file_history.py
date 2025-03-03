from pathlib import Path

import pytest

from automyte import AutomatonRunResult, InFileHistory


class TestInFileHistoryRead:
    def test_read_properly_parses_history_file(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
            ["auto1", "proj1", "success", ""],
            ["auto1", "proj2", "skipped", ""],
            ["auto2", "proj1", "fail", "oops"],
        ]

        history = InFileHistory(filename=tmp_csv_file(data))
        result1 = history.read(automaton_name="auto1")
        result2 = history.read(automaton_name="auto2")

        assert result1["proj1"] == AutomatonRunResult(status="success")
        assert result1["proj2"] == AutomatonRunResult(status="skipped")
        assert result2["proj1"] == AutomatonRunResult(status="fail", error="oops")

    def test_read_from_empty_file(self, tmp_csv_file):
        data = [[]]
        result = InFileHistory(filename=tmp_csv_file(data)).read("whatever")

        assert result == {}

    def test_read_from_file_without_necessary_automaton(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
            ["auto9", "proj1", "success", ""],
        ]
        result = InFileHistory(filename=tmp_csv_file(data)).read("auto1")

        assert result == {}

    def test_read_will_raise_if_dir_doesnt_exist(self):
        with pytest.raises(ValueError, match=".*does not exist*"):
            InFileHistory(filename="some/nonexistant/like/definitely/path/").read("whatever")

    def test_read_will_create_empty_default_file_in_existing_dir(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(structure={"src": {}})

        result = InFileHistory(filename=f"{dir}/src/").read("whatever")

        assert result == {}
        assert (Path(dir) / "src" / "automyte_history.csv").exists()

    def test_read_will_raise_if_file_parent_dir_doesnt_exist(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(structure={"src": {}})

        with pytest.raises(ValueError, match=".*does not exist*"):
            InFileHistory(filename=Path(dir) / "src" / "nonexistant_folder" / "history.csv").read("whatever")

    @pytest.mark.parametrize("filepath", [None, "./", "current", "local"])
    def test_read_will_use_local_call_dir_if_no_filepath_is_given(self, filepath):
        exptected_path = Path.cwd() / "automyte_history.csv"
        try:
            InFileHistory(filename=filepath).read("whatever")
            assert exptected_path.exists()

        finally:
            exptected_path.unlink()


class TestInFileHistoryGetStatus:
    def test_correct_retrieval(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
            ["auto", "proj1", "success", ""],
            ["auto", "proj2", "skipped", ""],
            ["auto", "proj3", "fail", "oops"],
        ]
        result1 = InFileHistory(filename=tmp_csv_file(data)).get_status(automaton_name="auto", project_id="proj1")
        result2 = InFileHistory(filename=tmp_csv_file(data)).get_status(automaton_name="auto", project_id="proj2")
        result3 = InFileHistory(filename=tmp_csv_file(data)).get_status(automaton_name="auto", project_id="proj3")

        assert result1 == AutomatonRunResult("success")
        assert result2 == AutomatonRunResult("skipped")
        assert result3 == AutomatonRunResult("fail", error="oops")

    def test_retrieval_for_new_project(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
        ]
        result = InFileHistory(filename=tmp_csv_file(data)).get_status(automaton_name="auto", project_id="proj1")

        assert result == AutomatonRunResult("new")

    def test_retrieval_for_the_first_run(self, tmp_local_project_factory):
        dir = tmp_local_project_factory(structure={"src": {}})

        # In the first run, file might not exist, making sure we just get new run.
        result = InFileHistory(filename=f"{dir}/src").get_status(automaton_name="auto", project_id="proj1")

        assert result == AutomatonRunResult("new")


class TestInFileHistorySetStatus:
    def test_plain_set_in_existing_new_file(self, tmp_csv_file):
        history = InFileHistory(filename=tmp_csv_file([[]]))

        history.set_status(automaton_name="auto", project_id="proj1", status=AutomatonRunResult(status="success"))

        assert history.get_status("auto", "proj1") == AutomatonRunResult("success")

    def test_override_of_previous_status(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
            ["auto", "proj1", "skipped", ""],
        ]
        history = InFileHistory(filename=tmp_csv_file(data))

        history.set_status(
            automaton_name="auto", project_id="proj1", status=AutomatonRunResult(status="fail", error="whoops")
        )

        assert history.get_status("auto", "proj1") == AutomatonRunResult("fail", error="whoops")

    def test_override_doesnt_touch_other_projects(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
            ["auto", "proj2", "skipped", ""],
            ["auto", "proj3", "success", ""],
            ["auto", "proj4", "fail", "oops"],
            ["auto2", "proj1", "fail", "oops"],
        ]
        history = InFileHistory(filename=tmp_csv_file(data))

        history.set_status(automaton_name="auto", project_id="proj1", status=AutomatonRunResult("success"))

        assert history.get_status("auto", "proj2") == AutomatonRunResult("skipped")
        assert history.get_status("auto", "proj3") == AutomatonRunResult("success")
        assert history.get_status("auto", "proj4") == AutomatonRunResult("fail", "oops")
        assert history.get_status("auto2", "proj1") == AutomatonRunResult("fail", "oops")

    def test_overrides_file_contents(self, tmp_csv_file):
        data = [
            ["automaton", "project", "status", "error"],
            ["auto", "proj1", "skipped", ""],
        ]
        filename = tmp_csv_file(data)
        InFileHistory(filename).set_status(
            automaton_name="auto", project_id="proj1", status=AutomatonRunResult("success")
        )

        separate_history_instance = InFileHistory(filename=filename)
        assert separate_history_instance.get_status("auto", "proj1") == AutomatonRunResult("success")
