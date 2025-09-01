import argparse
from dataclasses import dataclass
import os
import typing as t
from argparse import ArgumentParser
from collections import defaultdict

from automyte.config.builders.metadata_parser import ConfigMetadataParser
from automyte.config.fields import ConfigField, ConfigParams
from .. import fields as f


def str_to_bool(value: str) -> bool:
    """Convert string values to boolean"""
    if value.lower() in ("true", "1", "yes"):
        return True
    elif value.lower() in ("false", "0", "no"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def cli_args_parser(fields: t.Sequence[ConfigField]) -> ArgumentParser:
    parser = ArgumentParser(description="Run automaton.")

    for field in fields:
        if field.argnames is None:
            continue

        # Adding prefix, to later indicate that field has to go to a nested ConfigParam.
        save_to = f"{field.field_of + '-' if field.field_of != 'config' else ''}{field.name}"

        if field.kind is bool:
            # Allow passing --my-bool-opt, in case if default value is False or use --my-bool-opt=true/false otherwise.
            if field.default_value is False:
                parser.add_argument(
                    *field.argnames,
                    dest=save_to,
                    action="store_true",
                    default=field.default_value,
                    help=field.description,
                )
            else:
                parser.add_argument(
                    *field.argnames, dest=save_to, type=str_to_bool, default=field.default_value, help=field.description
                )

        else:
            parser.add_argument(
                *field.argnames, dest=save_to, type=str, default=field.default_value, help=field.description
            )

    return parser


def get_config_params_from_argv(supported_fields: t.Sequence[ConfigField]) -> ConfigParams:
    args = cli_args_parser(fields=supported_fields).parse_args()

    result = defaultdict(dict)
    for k, v in vars(args).items():
        # If arg has a name of 'smth-some_field' - "smth" is considered as sub-config object.
        if "-" in k:
            parent, key = k.split("-", 1)
            result[parent][key] = v
        else:
            result[k] = v

    return result  # pyright: ignore


@dataclass
class CmdArgsMixin:
    @classmethod
    def get_config_from_args(cls, config_overrides: ConfigParams | None = None) -> ConfigParams:
        is_cli = os.getenv("AUTOMYTE_READ_CMD_ARGS")
        if is_cli != "true":
            return config_overrides or {}

        fields_to_process = ConfigMetadataParser.get_fields_to_process(cls, "argnames")
        result = get_config_params_from_argv(
            supported_fields=ConfigMetadataParser.get_config_fields_from_fields(fields_to_process)
        )
        if not config_overrides:
            return result

        return {**result, **config_overrides}
