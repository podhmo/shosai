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

    def search(
        self,
        *,
        q: t.Optional[str] = None,
        page: t.Optional[int] = None,
        per_page: t.Optional[int] = None,
    ) -> t.Dict:
        url = f"{self.url}/posts"
        params = {}
        params["q"] = q or f"author:{self.profile.username}"
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        logger.debug("request: %s, params=%s", url, params)
        response = self.session.get(url, params=params)
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
