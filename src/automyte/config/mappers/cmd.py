import os
from argparse import ArgumentParser

from automyte.utils.bash import str_to_bool

AUTOMYTE_CLI_PARSER = ArgumentParser(description="Run automaton.")


class CMDArgsMapper:
    def __init__(self, parser: ArgumentParser = AUTOMYTE_CLI_PARSER) -> None:
        self.parser = parser
        self._args = None

    def setup_field(self, field):
        if field.kind is bool:
            # Allow passing --my-bool-opt, in case if default value is False or use --my-bool-opt=true/false otherwise.
            if field.default_value is False:
                self.parser.add_argument(
                    *field.argnames,
                    dest=field.name,
                    action="store_true",
                    default=field.default_value,
                    help=field.description,
                )
            else:
                self.parser.add_argument(
                    *field.argnames,
                    dest=field.name,
                    type=str_to_bool,
                    default=field.default_value,
                    help=field.description,
                )

        else:
            self.parser.add_argument(
                *field.argnames, dest=field.name, type=str, default=field.default_value, help=field.description
            )

    def get_value(self, field):
        if not str_to_bool(os.getenv("AUTOMYTE_CLI_MODE", "False")):
            return None

        self._args = self.parser.parse_args()

        return getattr(self._args, f"{field.name}", None)
