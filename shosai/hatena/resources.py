import sys
import typing as t
import logging
import os.path
import re
from requests_oauthlib import OAuth1Session
from ..langhelpers import reify
from ..base.resources import LoggedRequestMixin
from . import structure
from . import xmllib
logger = logging.getLogger(__name__)

# see:
# http://developer.hatena.ne.jp/ja/documents/blog/apis/atom
# http://developer.hatena.ne.jp/ja/documents/fotolife/apis/atom


class Session(LoggedRequestMixin, OAuth1Session):
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
        url: t.Optional[str] = None,
    ) -> t.Sequence[t.Any]:
        params = {}
        if q is not None:
            params["page"] = q
        app = self.app
        url = url or f"{app.url}/atom/entry"
        response = app.session.get(url, params=params)
        return xmllib.loads(response.text)


class Attachment:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def build_content_from_file(
        self,
        path: str,
        *,
        name=None,
    ) -> structure.AttachmentDict:
        with open(path, "rb") as rf:
            data = rf.read()
        return self.build_content(path, data, name=name)

    def build_content(
        self,
        path: str,
        data: bytes,
        *,
        name: t.Optional[str] = None,
    ) -> structure.AttachmentDict:
        import base64
        return {
            "name": name or os.path.basename(path),
            "content": base64.b64encode(data).decode("ascii"),
        }

    def __call__(self, contents: t.Sequence[structure.AttachmentDict]
                 ) -> t.Sequence[structure.AttachmentResultDict]:
        import mimetypes
        app = self.app
        url = "http://f.hatena.ne.jp/atom/post/"

        results = []
        for content in contents:
            typ, _ = mimetypes.guess_type(content["name"])
            doc = {
                "entry": {
                    "@xmlns": "http://purl.org/atom/ns#",
                    "generator": "shosai",
                    "title": content["name"],
                    "content": {
                        "@mode": "base64",
                        "@type": typ,
                        "#text": content["content"]
                    },
                },
            }
            xml = xmllib.dumps(doc)
            response = app.session.post(url, data=xml)
            try:
                # ./structure.py attachment response doc
                response_doc = xmllib.loads(response.text)
                result: structure.AttachmentResultDict = {
                    "id": response_doc["entry"]["id"],
                    "name": response_doc["entry"]["title"],
                    "url": response_doc["entry"]["hatena:imageurl"],
                    "hatena_syntax": response_doc["entry"]["hatena:syntax"],
                    "issued": response_doc["entry"]["issued"],
                }
                results.append(result)
            except Exception as e:
                print(str(e), file=sys.stderr)
                print(response.text, file=sys.stderr)
        return results


class Fetch:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def __call__(self, id: str) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/atom/entry/{id}"
        response = app.session.get(url)
        return xmllib.loads(response.text)

    def from_url(self, url: str, *, pagination_life=10) -> structure.PostDict:
        rx = re.compile(r"https://.+/entry/([\d/]+)")

        m = rx.search(url)
        assert m is not None
        part = m.group(1)

        # search from recently uploaded articles
        guessed_id = self._guess_id(part, pagination_life=pagination_life)
        if guessed_id is None:
            raise ValueError(f"sorry, not found {url!r}")
        return self.__call__(guessed_id)

    def _guess_id(self, part: str, *, pagination_life: int) -> str:
        app = self.app
        next_url = None
        for _ in range(pagination_life):
            response_dict = app.search(url=next_url)
            for link in response_dict["feed"]["link"]:
                if link["@rel"] == "next":
                    next_url = link["@href"]
                    break
            for entry in response_dict["feed"]["entry"]:
                matched = False
                for link in entry["link"]:
                    if link.get("@rel") == "alternate":
                        matched = link["@href"].rsplit("/entry/", 1)[-1] == part
                if not matched:
                    continue
                for link in entry["link"]:
                    if link.get("@rel") == "edit":
                        guessed_id = link["@href"].rsplit("/", 1)[-1]
                        return guessed_id
        return None


class Post:
    def __init__(self, app: Resource) -> None:
        self.app = app

    @property
    def author_name(self) -> str:
        return self.app.profile.name

    def __call__(
        self,
        title: str,
        body: str,
        *,
        draft: t.Optional[bool] = None,
        notice: bool = False,
        tags: t.Optional[t.Sequence[str]] = None,
        id: t.Optional[str] = None,
        meta: t.Optional[structure.MetadataDict] = None,
    ) -> structure.PostDict:
        created_at = None
        if meta is not None:
            created_at = meta["created_at"]
            if draft is None:
                draft = meta["draft"]

        doc = {
            "entry": {
                "@xmlns": "http://www.w3.org/2005/Atom",
                "@xmlns:app": "http://www.w3.org/2007/app",
                "title": title,
                "author": {
                    "name": self.author_name,
                },
                "content": {
                    "@type": "text/plain",
                    "#text": body,
                },
                "app:control": {
                    "app:draft": ("yes" if (draft is None or draft) else "no"),
                },
            },
        }

        if tags:
            doc["entry"]["category"] = [{"@term": t} for t in tags or []]

        if created_at is not None:
            doc["entry"]["updated"] = created_at

        if id is None:
            return self._create_post(doc)
        else:
            return self._update_post(doc, id=id)

    def _update_post(self, params: t.Dict, *, id: str) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/atom/entry/{id}"
        xml = xmllib.dumps_as_bytes(params)
        response = app.session.put(url, data=xml)
        return xmllib.loads(response.text)

    def _create_post(self, params: t.Dict) -> structure.PostDict:
        app = self.app
        url = f"{app.url}/atom/entry"
        xml = xmllib.dumps_as_bytes(params)
        response = app.session.post(url, data=xml)
        return xmllib.loads(response.text)
