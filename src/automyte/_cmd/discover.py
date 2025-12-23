import ast
import typing as t
from collections import defaultdict
from pathlib import Path

AutomatonName: t.TypeAlias = str


def find_all_automatons_in_dir(lookup_dir: Path):
    automatons_map: dict[Path, list[AutomatonName]] = defaultdict(list)

    for python_filepath in Path(lookup_dir).expanduser().resolve().rglob("*.py"):
        automatons_in_file = detect_automatons_in_a_file(python_filepath)

        if automatons_in_file:
            automatons_map[python_filepath].extend(automatons_in_file)


def detect_automatons_in_a_file(filepath: Path) -> list[AutomatonName]:
    automatons: list[AutomatonName] = []

    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            if not (
                isinstance(node.func, ast.Name)
                and node.func.id == "Automaton"
                or isinstance(node.func, ast.Attribute)
                and node.func.attr == "Automaton"
            ):
                continue

            name = next((ast.unparse(kw.value) for kw in node.keywords if kw == "name"), None)
            if name is not None:
                automatons.append(name)

    return automatons
