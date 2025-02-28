import re

from .base import File, Filter


class ContainsFilter(Filter):
    def __init__(self, contains: str | list[str], regexp: bool = False) -> None:
        self.text = contains if isinstance(contains, list) else [contains]
        self.use_regexp = regexp

    def filter(self, file: File) -> bool:
        if not self.use_regexp:
            return any(file.contains(occurance) for occurance in self.text)

        file_contents = file.get_contents()
        return any(re.search(pattern, file_contents) for pattern in self.text)
