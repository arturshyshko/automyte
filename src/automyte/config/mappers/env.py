import os

from automyte.utils.bash import str_to_bool


class EnvVarsMapper:
    def setup_field(self, field):
        pass

    def get_value(self, field):
        value = os.getenv(field.env_var)
        if value is None:
            return None

        if field.kind is bool:
            return str_to_bool(value)
        elif field.kind is int:
            return int(value)
        else:
            return value
