from automyte.utils import bash


def test_plain_execution():
    result = bash.execute(["echo", "stdout test"])
    assert result.status == "success"
    assert result.output == "stdout test"


def test_failure_execution():
    result = bash.execute(["ls", "/kladjslkajdslkjasd"])
    assert result.status == "fail"
    assert result.output == "ls: /kladjslkajdslkjasd: No such file or directory"
