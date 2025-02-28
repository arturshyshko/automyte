from automyte import File, Filter, OSFile


class ExampleFilter1(Filter):
    def filter(self, file: File):
        return file.contains("1")


class ExampleFilter2(Filter):
    def filter(self, file: File):
        return file.contains("2")


class ExampleFilter3(Filter):
    def filter(self, file: File):
        return file.contains("3")


class TestFilter:
    def test_logical_and_results_in_file_having_to_pass_both_filters_conditions(self, tmp_os_file):
        file1: OSFile = tmp_os_file("11111")
        file2: OSFile = tmp_os_file("22222")
        file3: OSFile = tmp_os_file("3333")
        correct_file: OSFile = tmp_os_file("111222")

        filter = ExampleFilter1() & ExampleFilter2()

        assert not filter.filter(file=file1)
        assert not filter.filter(file=file2)
        assert not filter.filter(file=file3)
        assert filter.filter(file=correct_file)

    def test_logical_or_results_in_file_having_to_pass_either_filters_conditions(self, tmp_os_file):
        file1: OSFile = tmp_os_file("11111")
        file2: OSFile = tmp_os_file("22222")
        file3: OSFile = tmp_os_file("111222")
        incorrect_file: OSFile = tmp_os_file("3333")

        filter = ExampleFilter1() | ExampleFilter2()

        assert filter.filter(file=file1)
        assert filter.filter(file=file2)
        assert filter.filter(file=file3)
        assert not filter.filter(file=incorrect_file)

    def test_logical_not_results_in_file_having_to_fail_filter_condition(self, tmp_os_file):
        file1: OSFile = tmp_os_file("11111")
        file2: OSFile = tmp_os_file("2")
        filter = ~ExampleFilter1()

        assert not filter.filter(file=file1)
        assert filter.filter(file=file2)

    def test_complex_scenario(self, tmp_os_file):
        file: OSFile = tmp_os_file("111222333")

        filter1 = ExampleFilter1() & ExampleFilter2()
        filter2 = (ExampleFilter1() & ExampleFilter2()) & ~ExampleFilter3()

        assert filter1.filter(file=file)
        assert not filter2.filter(file=file)
