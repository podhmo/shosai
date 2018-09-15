import sys
import json
import logging
import os.path
from ..langhelpers import reify
from . import structure
logger = logging.getLogger(__name__)


def init(path: str) -> None:
    d: structure.ProfileDict = {
        "consumer_key": "",
        "consumer_secret": "",
        "client_id": "",
        "client_secret": "",
        "hatena_id": "",
        "blog_id": ""
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger.info("write: %s", path)
    with open(path, "w") as wf:
        json.dump({"hatena": d}, wf, indent=2)


def load(config_path: str, *, init=init):
    if not os.path.exists(config_path):
        print(f"{config_path} is not found, generated. please setting this file.", file=sys.stderr)
        init(config_path)
        sys.exit(1)

    logger.info("read: %s", config_path)
    with open(config_path) as rf:
        config = json.load(rf)
    return config["hatena"]


class Profile:
    data: structure.ProfileDict

    def __init__(self, config_path: str) -> None:
        self.data = load(config_path)

    # todo: remove?
    @reify
    def blog_id(self) -> str:
        return self.data["blog_id"]

    @reify
    def client_id(self) -> str:
        return self.data["client_id"]

    @reify
    def client_secret(self) -> str:
        return self.data["client_secret"]

    @reify
    def consumer_key(self) -> str:
        return self.data["consumer_key"]

    @reify
    def consumer_secret(self) -> str:
        return self.data["consumer_secret"]

    @reify
    def hatena_id(self) -> str:
        return self.data["hatena_id"]
