import typing as t
import logging
import os.path
from importlib import import_module
from . import loading
from .langhelpers import reify

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "~/.config/shosai/config.json"
DEFAULT_MAPPING_PATH = "./mapping.json"


class App:
    def __init__(
        self,
        config_path: t.Optional[str] = None,
        *,
        service: str,  # ("hatena", "docbase")
        mapping_path: t.Optional[str] = None,
    ) -> None:
        self.config_path = config_path or os.path.expanduser(config_path or DEFAULT_CONFIG_PATH)
        self.mapping_path = mapping_path or DEFAULT_MAPPING_PATH
        self.service = service

    @reify
    def configuration(self):
        return import_module(f"shosai.{self.service}.configuration")

    @reify
    def resources(self):
        return import_module(f"shosai.{self.service}.resources")

    @reify
    def profile(self) -> t.Dict[str, str]:
        return self.configuration.Profile(self.config_path)

    @reify
    def loader(self):
        return loading.Loader(self.mapping_path)

    @reify
    def saver(self):
        return loading.Saver(self.mapping_path, self.loader.data)

    @reify
    def resource(self) -> "Resource":
        return self.resources.Resource(self.profile)

    @reify
    def transform(self):
        return import_module(f"shosai.{self.service}.transform")
