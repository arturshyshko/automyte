import typing as t


from dataclasses import Field, fields, is_dataclass


def get_fields_to_process(dataclass, field_name: str) -> t.Sequence[Field]:
    fields_to_process: t.Sequence[Field] = []
    for f in fields(dataclass):
        if is_dataclass(f.type):
            fields_to_process.extend(fields(f.type))
        else:
            fields_to_process.append(f)
    fields_to_process = [
        f for f in fields_to_process if f.metadata.get(field_name, None)
    ]
    return fields_to_process


def get_typed_value(kind: t.Any, value: str | None) -> str | bool | int | None:
    if value is None:
        return None

    if kind is bool:
        return value.strip().lower() == "true"
    elif kind is int:
        return int(value)

    return value
