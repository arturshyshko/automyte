from argparse import ArgumentParser

CLI_DESCRIPTION = """
Automyte cli.

Commands:
    run  Run an automaton with given configuration.
"""


CMD_DESCRIPTION_RUN = """
Run an automaton.
"""

AutomyteArgParser = ArgumentParser(description=CLI_DESCRIPTION)
cmd = AutomyteArgParser.add_subparsers(dest="command", required=True)
AutomyteArgParser.add_argument("path", help="Python file path with automaton definition.")

RunArgParser = cmd.add_parser("run", description=CMD_DESCRIPTION_RUN)
