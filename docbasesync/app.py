import typing as t
import logging
from requests import sessions
from . import configuration
from .langhelpers import reify
logger = logging.getLogger(__name__)


class App:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path

    @reify
    def profile(self) -> t.Dict[str, str]:
        return Profile(self.config_path)

    @reify
    def url(self):
        return f"https://api.docbase.io/teams/{self.profile.teamname}".rstrip("/")

    @reify
    def session(self) -> sessions.Session:
        s = sessions.Session()
        s.headers["X-DocBaseToken"] = self.profile.token
        return s

    def __enter__(self):
        return self.session.__enter__()

    def __exit__(self, typ, tb, value):
        return self.session.__exit__(typ, tb, value)

    @reify
    def search(self) -> "Search":
        return Search(self)

    @reify
    def post(self) -> "Post":
        return Post(self)


class Search:
    def __init__(self, app: App) -> None:
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
        logger.debug("request: %s, params=%s", url, params)
        response = app.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


class Post:
    def __init__(self, app: App) -> None:
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
    ) -> t.Dict:
        params = {
            "title": title,
            "body": body,
            "draft": draft,
            "notice": notice,
        }
        if tags is not None:
            params["tags"] = tags
        if id is None:
            return self._create_post(params)
        else:
            return self._update_post(params, id=id)

    def _update_post(self, params: t.Dict, *, id: str) -> t.Dict:
        app = self.app
        url = f"{app.url}/posts/{id}"
        response = app.session.patch(url, json=params)
        response.raise_for_status()
        return response.json()

    def _create_post(self, params: t.Dict) -> t.Dict:
        app = self.app
        url = f"{app.url}/posts"
        print(params)
        response = app.session.post(url, json=params)
        response.raise_for_status()
        return response.json()


class Profile:
    def __init__(self, config_path: str) -> None:
        data = configuration.load(config_path)
        assert "token" in data
        assert "teamname" in data
        assert "username" in data
        self.data = data

    @reify
    def token(self) -> str:
        return self.data["token"]

    @reify
    def username(self) -> str:
        return self.data["username"]

    @reify
    def teamname(self) -> str:
        return self.data["teamname"]


# class Loader:
#     def __init__(self, profile):
#         self.profile = profile
