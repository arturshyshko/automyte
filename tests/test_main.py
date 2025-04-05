from automyte import main


def test_main_returns_0_status_on_proper_exit():
    expect = 0
    result = main.main()
    assert result == expect
