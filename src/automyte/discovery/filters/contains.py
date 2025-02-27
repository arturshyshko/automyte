from .base import File, Filter


class ContainsFilter(Filter):
    def __init__(self, contains: str | list[str]) -> None:
        self.text = contains if isinstance(contains, list) else [contains]
        # TODO: Handle regexp case.

    def filter(self, file: File) -> File | None:
        if any(file.contains(occurance) for occurance in self.text):
            return file
