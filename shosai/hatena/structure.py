import typing as t
import mypy_extensions as mx


class ProfileDict(mx.TypedDict):
    blog_id: str
    client_id: str
    client_secret: str
    consumer_key: str
    consumer_secret: str
    hatena_id: str


PostDict = t.Dict

