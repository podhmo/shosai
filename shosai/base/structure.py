import typing as t
import typing_extensions as tx


class PostDict(tx.TypedDict):
    content: str
    tags: t.Sequence[str]
    title: str


class MappingDict(tx.TypedDict):
    id: t.Any
    name: str
    title: str
    draft: bool
    url: str
    created_at: str
    file: str
    tags: t.Sequence[str]


class AttachmentDict(tx.TypedDict):
    name: str
    content: str


class AttachmentResultDict(tx.TypedDict):
    id: t.Any
    name: str
    url: str
