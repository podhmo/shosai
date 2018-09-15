import typing as t
import logging
import os.path
import base64
from .langhelpers import reify
from requests import sessions
logger = logging.getLogger(__name__)


class Resource:
    def __init__(self, profile):
        self.profile = profile

    @reify
    def url(self):
        return f"https://api.docbase.io/teams/{self.profile.teamname}".rstrip("/")

    @reify
    def session(self) -> sessions.Session:
        s = sessions.Session()
        s.headers["X-DocBaseToken"] = self.profile.token
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
    ) -> t.Dict:
        app = self.app
        url = f"{app.url}/posts"

        params = {}
        params["q"] = q or f"author:{app.profile.username}"
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page

        logger.info("GET %s, params=%s", url, params)
        response = app.session.get(url, params=params)
        logger.info("status=%s, %s", response.status_code, url)
        response.raise_for_status()
        return response.json()


class Attachment:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def build_content_from_file(self, path, *, name=None) -> t.Dict:
        with open(path, "rb") as rf:
            data = rf.read()
        return self.build_content(path, data, name=name)

    def build_content(self, path, data, *, name=None) -> t.Dict:
        return {
            "name": name or os.path.basename(path),
            "content": base64.b64encode(data).decode("ascii"),
        }

    def __call__(self, contents):
        # [{"name": <str>, "content": <base64>}]
        app = self.app
        url = f"{app.url}/attachments"

        logger.info("POST %s, params=%s", url, [d["name"] for d in contents])
        response = app.session.post(url, json=contents)
        logger.info("status=%s, %s", response.status_code, url)
        response.raise_for_status()
        return response.json()


class Fetch:
    def __init__(self, app: Resource) -> None:
        self.app = app

    def __call__(self, id) -> t.Dict:
        app = self.app
        url = f"{app.url}/posts/{id}"
        logger.info("GET %s", url)
        response = app.session.get(url)
        logger.info("status=%s, %s", response.status_code, url)
        response.raise_for_status()
        return response.json()


class Post:
    def __init__(self, app: Resource) -> None:
        self.app = app

    # todo: group/scope
    def __call__(
        self,
        title: str,
        body: str,
        *,
        draft: bool = False,
        notice: bool = False,
        tags: t.Optional[t.Sequence[str]] = None,
        id: t.Optional[str] = None,
        scope: t.Optional[str] = None,
        groups: t.Optional[t.Sequence[int]] = None,
    ) -> t.Dict:
        params = {
            "title": title,
            "body": body,
            "draft": draft,
            "notice": notice,
        }
        if tags is not None:
            params["tags"] = tags
        if scope is not None:
            params["scope"] = scope
        if groups is not None:
            params["groups"] = groups

        if id is None:
            return self._create_post(params)
        else:
            return self._update_post(params, id=id)

    def _update_post(self, params: t.Dict, *, id: str) -> t.Dict:
        app = self.app
        url = f"{app.url}/posts/{id}"

        logger.info("PATCH %s", url)
        response = app.session.patch(url, json=params)
        logger.info("status=%s, %s", response.status_code, url)
        response.raise_for_status()
        return response.json()

    def _create_post(self, params: t.Dict) -> t.Dict:
        app = self.app
        url = f"{app.url}/posts"

        logger.info("POST %s", url)
        response = app.session.post(url, json=params)
        logger.info("status=%s, %s", response.status_code, url)
        response.raise_for_status()
        return response.json()
