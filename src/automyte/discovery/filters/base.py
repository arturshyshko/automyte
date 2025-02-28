from __future__ import annotations

from ..file import File


class Filter:
    def filter(self, file: File) -> bool:
        raise NotImplementedError

    def __call__(self, file: File) -> bool:
        return self.filter(file=file)

    def __and__(self, other: "Filter") -> "Filter":
        """Returns a filter that represents logical AND."""

        class AndFilter(Filter):
            def __init__(self, filter1: Filter, filter2: Filter):
                self.filter1 = filter1
                self.filter2 = filter2

            def filter(self, file: File) -> bool:
                return self.filter1.filter(file) and self.filter2.filter(file)

        return AndFilter(self, other)

    def __or__(self, other: "Filter") -> "Filter":
        """Returns a filter that represents logical OR."""

        class OrFilter(Filter):
            def __init__(self, filter1: Filter, filter2: Filter):
                self.filter1 = filter1
                self.filter2 = filter2

            def filter(self, file: File) -> bool:
                return self.filter1.filter(file) or self.filter2.filter(file)

        return OrFilter(self, other)

    def __invert__(self) -> "Filter":
        class NotFilter(Filter):
            def __init__(self, filter: Filter) -> None:
                self.inverted_filter = filter

            def filter(self, file: File) -> bool:
                return not self.inverted_filter.filter(file)

        return NotFilter(self)
