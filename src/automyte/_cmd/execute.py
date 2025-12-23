import runpy
import sys
from argparse import Namespace
from pathlib import Path


def execute_automaton(module_with_automaton: str):
    sys_argv_backup = sys.argv[:]
    sys.argv = [module_with_automaton, *sys_argv_backup]
    try:
        runpy.run_module(module_with_automaton, run_name="__main__")
    finally:
        sys.argv = sys_argv_backup


def find_automaton_module(args: Namespace) -> str:
    module_name = args.path
    if module_name is None:
        raise AttributeError("[CLI]: Automaton path was not provided")
    module_path = Path(module_name)

    return ".".join(module_path.with_suffix("").parts)
