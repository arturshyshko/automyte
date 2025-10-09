from __future__ import annotations

import configparser
import logging
from pathlib import Path

from automyte.config.fields import ConfigField

logger = logging.getLogger(__name__)


class FileConfigMapper:
    def __init__(self, filepath: Path = Path("./automyte.cfg")):
        self.filepath = filepath
        if not self.filepath.exists():
            logger.debug("[Setup]: Configuration file not found: %s.", self.filepath)
            self.cfg = None
            return

        self.cfg = configparser.ConfigParser()
        self.cfg.read(str(filepath))

    def setup_field(self, field: ConfigField):
        pass

    def get_value(self, field: ConfigField):
        if self.cfg is None:
            return None
        if field.file_param is None:
            return None
        section, param_name = field.file_param.split(".")

        try:
            if field.kind is bool:
                value = self.cfg.getboolean(section, param_name)
            elif field.kind is int:
                value = self.cfg.getint(section, param_name)
            else:
                value = self.cfg.get(section, param_name)
        except configparser.NoOptionError:
            return None

        return value
