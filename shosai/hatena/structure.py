import typing as t
import mypy_extensions as mx
from shosai.base import structure as base


class ProfileDict(mx.TypedDict):
    blog_id: str
    client_id: str
    client_secret: str
    consumer_key: str
    consumer_secret: str
    hatena_id: str


PostDict = t.Dict
AttachmentDict = base.AttachmentDict


class AttachmentResultDict(base.AttachmentResultDict):
    issued = str
    hatena_syntax = str


# attachment response doc
"""
  {
    "entry": {
      "@xmlns": "http://purl.org/atom/ns#",
      "@xmlns:hatena": "http://www.hatena.ne.jp/info/xmlns#",
      "title": "<filename>",
      "link": [
        {
          "@rel": "alternate",
          "@type": "text/html",
          "@href": "http://f.hatena.ne.jp/<username>/20180917010536"
        },
        {
          "@rel": "service.edit",
          "@type": "application/x.atom+xml",
          "@href": "http://f.hatena.ne.jp/atom/edit/20180917010536",
          "@title": "<filename>"
        }
      ],
      "issued": "2018-09-17T01:05:36+09:00",
      "author": {
        "name": "<username>"
      },
      "generator": {
        "@url": "http://f.hatena.ne.jp/",
        "@version": "1.0",
        "#text": "Hatena::Fotolife"
      },
      "dc:subject": {
        "@xmlns:dc": "http://purl.org/dc/elements/1.1/",
        "#text": "shosai"
      },
      "id": "tag:hatena.ne.jp,2005:fotolife-<username>-20180917010536",
      "hatena:imageurl": "https://cdn-ak.f.st-hatena.com/images/fotolife/p/<username>/20180917/20180917010536.png",
      "hatena:imageurlmedium": "https://cdn-ak.f.st-hatena.com/images/fotolife/p/<username>/20180917/20180917010536_120.jpg",
      "hatena:imageurlsmall": "https://cdn-ak.f.st-hatena.com/images/fotolife/p/<username>/20180917/20180917010536_m.jpg",
      "hatena:syntax": "f:id:<username>:20180917010536p:image"
    }
  }
"""
