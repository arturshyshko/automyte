from ..file import File


# TODO: Need to implement __and__ __or__ stuff, to be able to combine filters
class Filter:
    def filter(self, file: File) -> File | None:
        raise NotImplementedError

    def __call__(self, file: File) -> File | None:
        return self.filter(file=file)
