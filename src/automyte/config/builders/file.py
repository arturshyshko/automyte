from __future__ import annotations

import configparser
import logging
import typing as t
from dataclasses import Field, dataclass, fields, is_dataclass
from pathlib import Path

from typing_extensions import override

from ..fields import ConfigParams

logger = logging.getLogger(__name__)


@dataclass
class FileConfigMixin:
    @classmethod
    def parse_config_file(cls, filepath: Path) -> "ConfigParams":
        if not filepath.exists():
            logger.debug("[Setup]: Configuration file not found: %s.", filepath)
            return {}

        if filepath.suffix == ".cfg":
            return cls._parse_cfg_file(filepath)

        else:
            raise ValueError(f"Received invalid file format for config file: {filepath}")
        return {}

    @classmethod
    def _parse_cfg_file(cls, filepath: Path) -> "ConfigParams":
        overrides = ConfigParams(vcs={})
        cfg = configparser.ConfigParser()
        cfg.read(str(filepath))

        # Once get fields with "file_param" present in metadata, from nested child classes as well.
        # Only works for 1 level of nesting.
        fields_to_process: t.Sequence[Field] = []
        for f in fields(cls):
            if is_dataclass(f.type):
                fields_to_process.extend(fields(f.type))
            else:
                fields_to_process.append(f)
        fields_to_process = [f for f in fields_to_process if f.metadata.get("file_param", None)]

        # Take location of the field in config file and in Config class and generate overrides.
        for field in fields_to_process:
            section, param_name = field.metadata["file_param"].split(".")
            field_of = field.metadata.get("field_of", "config")
            field_name = field.metadata.get("name", field.name)
            kind = field.metadata.get("kind", str)

            try:
                if kind is bool:
                    value = cfg.getboolean(section, param_name)
                elif kind is int:
                    value = cfg.getint(section, param_name)
                else:
                    value = cfg.get(section, param_name)
            except configparser.NoOptionError:
                continue

            if field_of == "config":
                overrides[field_name] = value
            else:
                overrides[field_of][field_name] = value

        overrides = {k: v for k, v in overrides.items() if v not in ({},)}

        return overrides
