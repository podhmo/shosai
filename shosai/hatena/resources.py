import typing as t
import mypy_extensions as mx
import logging
import os.path
import base64
import xmltodict
from requests_oauthlib import OAuth1Session
from ..langhelpers import reify
from ..base.resources import LoggedRequestMixin
from . import structure
logger = logging.getLogger(__name__)


class Session(OAuth1Session, LoggedRequestMixin):
    logger = logger


class Resource:
    def __init__(self, profile):
        self.profile = profile

    @reify
    def url(self):
        url = f"https://blog.hatena.ne.jp/{self.profile.hatena_id}/{self.profile.blog_id}"
        return url.rstrip("/")

    @reify
    def session(self) -> Session:
        profile = self.profile
        s = Session(
            client_key=profile.consumer_key,
            client_secret=profile.consumer_secret,
            resource_owner_key=profile.client_id,
            resource_owner_secret=profile.client_secret
        )
        return s

    def __enter__(self):
        self.session.__enter__()
        return self

    def __exit__(self, *args):
        return self.session.__exit__(*args)

    @reify
    def search(self) -> "Search":
        return Search(self)

    @reify
    def attachment(self) -> "Attachment":
        return Attachment(self)

    @reify
    def fetch(self) -> "Fetch":
        return Fetch(self)

    @reify
    def post(self) -> "Post":
        return Post(self)


class Search:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def __call__(
        self,
        *,
        q: t.Optional[str] = None,
        page: t.Optional[int] = None,
        per_page: t.Optional[int] = None,
    ) -> t.Sequence[t.Any]:
        params = {}
        if q is not None:
            params["page"] = q
        app = self.app
        url = f"{app.url}/atom/entry"
        response = app.session.get(url, params=params)
        return xmltodict.parse(response.text, process_namespaces=False)


class Attachment:
    def __init__(self, app: Resource) -> None:
        self.app = app

    # def build_content_from_file(
    #     self,
    #     path: str,
    #     *,
    #     name=None,
    # ) -> structure.AttachmentDict:
    #     with open(path, "rb") as rf:
    #         data = rf.read()
    #     return self.build_content(path, data, name=name)

    # def build_content(
    #     self,
    #     path: str,
    #     data: bytes,
    #     *,
    #     name: t.Optional[str] = None,
    # ) -> structure.AttachmentDict:
    #     return {
    #         "name": name or os.path.basename(path),
    #         "content": base64.b64encode(data).decode("ascii"),
    #     }

    # def __call__(self, contents) -> t.Sequence[structure.AttachmentResultDict]:
    #     # [{"name": <str>, "content": <base64>}]
    #     app = self.app
    #     url = f"{app.url}/attachments"

    #     response = app.session.post(url, json=contents)
    #     return response.json()


class Fetch:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def __call__(self, id: str) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/atom/entry/{id}"
        response = app.session.get(url)
        return xmltodict.parse(response.text, process_namespaces=False)

    # def from_url(self, url: str) -> structure.PostDict:
    #     import re
    #     app = self.app
    #     rx = re.compile(r"https://([^.]+).docbase.io/posts/(\d+)")

    #     m = rx.search(url)
    #     assert m is not None
    #     team = m.group(1)
    #     assert team == app.profile.teamname
    #     id = m.group(2)
    #     return self.__call__(id)


class _PostParamsDictOptional(mx.TypedDict, total=False):
    draft: bool  # default false
    notice: bool  # default true
    tags: t.Sequence[str]
    scope: str  # default "everyone"
    groups: t.Sequence[str]


class PostParamsDict(_PostParamsDictOptional, mx.TypedDict, total=True):
    title: str
    body: str


class Post:
    def __init__(self, app: Resource) -> None:
        self.app = app

    # # todo: group/scope
    # def __call__(
    #     self,
    #     title: str,
    #     body: str,
    #     *,
    #     draft: bool = False,
    #     notice: bool = False,
    #     tags: t.Optional[t.Sequence[str]] = None,
    #     id: t.Optional[str] = None,
    #     scope: t.Optional[str] = None,
    #     groups: t.Optional[t.Sequence[int]] = None,
    # ) -> structure.PostDict:
    #     params: PostParamsDict = {
    #         "title": title,
    #         "body": body,
    #         "draft": draft,
    #         "notice": notice,
    #     }
    #     if tags is not None:
    #         params["tags"] = tags
    #     if scope is not None:
    #         params["scope"] = scope
    #     if groups is not None:
    #         params["groups"] = groups

    #     if id is None:
    #         return self._create_post(params)
    #     else:
    #         return self._update_post(params, id=id)

    # def _update_post(self, params: t.Dict, *, id: str) -> structure.PostDict:
    #     app = self.app
    #     url = f"{app.url}/posts/{id}"

    #     response = app.session.patch(url, json=params)
    #     return response.json()

    # def _create_post(self, params: t.Dict) -> structure.PostDict:
    #     app = self.app
    #     url = f"{app.url}/posts"

    #     response = app.session.post(url, json=params)
    #     return response.json()
