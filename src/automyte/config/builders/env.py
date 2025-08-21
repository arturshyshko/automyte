from dataclasses import Field, dataclass
import os
from automyte.config.fields import ConfigParams
import typing as t

from automyte.utils.config import get_fields_to_process, get_typed_value


@dataclass
class EnvVarsConfigMixin:
    @classmethod
    def parse_env_vars(cls) -> ConfigParams:
        env_config = ConfigParams()
        # get fields configurable via env_var including nested fields for vcs
        fields_to_process: t.Sequence[Field] = get_fields_to_process(cls, "env_var")

        for item in fields_to_process:
            param = item.metadata.get("env_var", None)
            kind = item.metadata.get("kind", str)
            field_of = item.metadata.get("field_of", "config")
            field_name = item.metadata.get("name", item.name)

            value = get_typed_value(kind, os.getenv(param)) if param else None

            # explicit checking for None as value can be False
            if param and value is not None:
                if field_of == "config":
                    env_config[field_name] = value
                else:
                    if field_of not in env_config:
                        env_config[field_of] = {}
                    env_config[field_of][field_name] = value

        return env_config
