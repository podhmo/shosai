import typing as t
import logging
import os.path
from . import loading
from .docbase import configuration  # xxx
from .docbase import resources  # xxx
from .langhelpers import reify

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "~/.config/shosai/config.json"
DEFAULT_MAPPING_PATH = "./mapping.json"


class App:
    def __init__(
        self, config_path: t.Optional[str] = None, *, mapping_path: t.Optional[str] = None
    ) -> None:
        self.config_path = config_path or os.path.expanduser(config_path or DEFAULT_CONFIG_PATH)
        self.mapping_path = mapping_path or DEFAULT_MAPPING_PATH

    @reify
    def profile(self) -> t.Dict[str, str]:
        return configuration.Profile(self.config_path)

    @reify
    def loader(self):
        return loading.Loader(self.mapping_path)

    @reify
    def saver(self):
        return loading.Saver(self.mapping_path, self.loader.data)

    @reify
    def resource(self) -> "Resource":
        return resources.Resource(self.profile)