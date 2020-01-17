import typing as t
import sys
import argparse
import json
from . import resources


def tags(
    service: str,
    *,
    config_path: str,
    mapping_path: str,
    out: t.Optional[t.IO] = None,
    verbose: bool = False,
):
    """https://help.docbase.io/posts/92979"""
    from shosai import App

    out = out or sys.stdout
    app = App(config_path, service=service, mapping_path=mapping_path)
    assert isinstance(app.resource, resources.Resource)
    with app.resource as r:
        data = r.tags()
        json.dump(data, out, indent=2, ensure_ascii=False)


def groups(
    service: str,
    *,
    config_path: str,
    mapping_path: str,
    out: t.Optional[t.IO] = None,
    verbose: bool = False,
):
    """https://help.docbase.io/posts/92978"""
    from shosai import App

    out = out or sys.stdout
    app = App(config_path, service=service, mapping_path=mapping_path)
    assert isinstance(app.resource, resources.Resource)
    with app.resource as r:
        data = r.groups()
        json.dump(data, out, indent=2, ensure_ascii=False)


def setup(*, parser: argparse.ArgumentParser, subparsers: argparse._SubParsersAction):
    """install extra commands"""
    # tags
    fn = tags
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-c", "--config", required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")

    # groups
    fn = groups
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-c", "--config", required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
