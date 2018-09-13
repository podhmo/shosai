import sys
import json
import os.path


def init(path):
    api_token = "<from https://help.docbase.io/posts/45703#%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E3%83%88%E3%83%BC%E3%82%AF%E3%83%B3>"
    d = {
        "teamname": "<team>",
        "token": api_token,
        "username": "<user>",
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as wf:
        json.dump(d, wf, indent=2)


DEFAULT_CONFIG_PATH = "~/.config/docbasesync/config.json"


def load(config_path=None, *, init=init):
    config_path = os.path.expanduser(config_path or DEFAULT_CONFIG_PATH)

    if not os.path.exists(config_path):
        print(f"{config_path} is not found, generated. please setting this file.", file=sys.stderr)
        init(config_path)
        sys.exit(1)

    with open(config_path) as rf:
        config = json.load(rf)
    return config
