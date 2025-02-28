from automyte import ContainsFilter


class TestContainsFilter:
    def test_single_text_returns_correctly(self, tmp_os_file):
        file = tmp_os_file("substring")

        assert ContainsFilter(contains="sub").filter(file=file)
        assert not ContainsFilter(contains="text").filter(file=file)

    def test_array_value_in_contains_filters_by_at_least_one_match(self, tmp_os_file):
        file = tmp_os_file("substring")

        assert ContainsFilter(contains=["sub", "text"]).filter(file=file)
        assert not ContainsFilter(contains=["random", "text"]).filter(file=file)

    def test_regexp_returns_correctly_for_str_contains(self, tmp_os_file):
        file = tmp_os_file("substring")

        assert ContainsFilter(contains=r"su.string", regexp=True).filter(file=file)
        assert not ContainsFilter(contains=r"si.*", regexp=True).filter(file=file)

    def test_array_value_in_contains_with_regexp_filters_by_at_least_one_match(self, tmp_os_file):
        file = tmp_os_file("substring")

        assert ContainsFilter(contains=[r"su.string", r"text"], regexp=True).filter(file=file)
        assert not ContainsFilter(contains=[r"si.*", r"what.*"], regexp=True).filter(file=file)
