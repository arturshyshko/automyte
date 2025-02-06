import os

from .filesystem import OSFile


class ProjectExplorer:
    def __init__(self, rootdir) -> None:
        self.rootdir = rootdir

    def all_files(self, extension: str = ''):
        for root, dirs, files in os.walk(self.rootdir):
            for f in files:
                if f.endswith(extension):
                    yield OSFile(folder=root, filename=f)

    def filter(
            self,
            contains: list[str] | None = None,
            named: list[str] | None = None,
            extension: str | None = None,
    ):
        assert contains is not None or named is not None or extension is not None, \
            'Should provide text, name or extension filter.'

        checks_list = []
        if contains:
            contains_at_least_one_occurance = lambda f: any(f.contains(occurance) for occurance in contains)
            checks_list.append(contains_at_least_one_occurance)

        if named:
            file_without_extension_is_named = lambda f: f.path.stem in named
            checks_list.append(file_without_extension_is_named)

        if extension is not None:
            file_extension_is = lambda f: f.path.suffix == extension
            checks_list.append(file_extension_is)

        for file in self.all_files(extension=(extension or '')):
            if all(check(file) for check in checks_list):
                yield file
