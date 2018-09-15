import typing as t
import mypy_extensions as mx


class PostDict(mx.TypedDict):
    content: str
    tags: t.Sequence[str]
    title: str
    url: str
    id: t.Any


class MappingDict(mx.TypedDict):
    id: int
    title: str
    draft: bool
    url: str
    created_at: str
    file: str
    tags: t.Sequence[str]
