# import subprocess
# import sys
# from pathlib import Path

# BASE_TESTS_DIR = Path(__file__).parent.parent.parent.parent
# BASE_CLI_TESTS_DIR = Path(__file__).parent
# DATA_DIR = BASE_CLI_TESTS_DIR / "data"
# AUTOMATONS_DIR = BASE_CLI_TESTS_DIR / "callee"

# expected_result = """
# some_var = True
# if some_var:
#     print(123)
# """


# def test_automyte_run(add_automatons_to_syspath):
#     env_with_syspath = add_automatons_to_syspath
#     result = subprocess.run(
#         ["automyte", "run", "--mode=run", str(AUTOMATONS_DIR.relative_to(BASE_CLI_TESTS_DIR) / "plain_regexp.py")],
#         capture_output=True,
#         text=True,
#         cwd=str(BASE_CLI_TESTS_DIR),
#         # env=env_with_syspath,
#     )
#     assert result.returncode == 0

#     with open(str(DATA_DIR / "replace_true.py"), "r") as f:
#         contents = f.read()

#         assert contents == expected_result
