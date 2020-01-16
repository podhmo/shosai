import typing as t
import typing_extensions as tx
from shosai.base import structure as base


class ProfileDict(tx.TypedDict):
    blog_id: str
    client_id: str
    client_secret: str
    consumer_key: str
    consumer_secret: str
    hatena_id: str


class MetadataDict(tx.TypedDict):
    id: str
    name: str  # flename
    title: str
    created_at: str
    draft: bool
    file: str
    tags: t.Sequence[str]


PostDict = t.Dict
AttachmentDict = base.AttachmentDict


class AttachmentResultDict(base.AttachmentResultDict):
    issued = str
    hatena_syntax = str
