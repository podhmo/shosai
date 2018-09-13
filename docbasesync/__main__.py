import sys
import typing as t
import json
import logging
logger = logging.getLogger(__name__)


def search(
    *,
    config: str,
    query: t.Optional[str] = None,
    page: t.Optional[int] = None,
    per_page: t.Optional[int] = None,
    out: t.Optional[t.IO] = None,
) -> None:
    from docbasesync import App
    out = out or sys.stdout
    app = App(config)
    with app:
        data = app.search(q=query, page=page, per_page=per_page)
    json.dump(data, out, indent=2, ensure_ascii=False)


def post(
    *,
    config: str,
    path: str,
    draft: bool = False,
    notice: bool = False,
    tags: t.Optional[t.Sequence[str]] = None,
    id: t.Optional[str],
    out: t.Optional[t.IO] = None,
) -> None:
    from docbasesync import App
    from docbasesync import parsing
    out = out or sys.stdout
    app = App(config)
    with app:
        with open(path) as rf:
            parsed = parsing.parse_article(rf)
        data = app.post(
            parsed.title,
            parsed.content,
            tags=[*parsed.tags, *(tags or [])],
            id=id,
            draft=draft,
            notice=notice,
        )
    json.dump(data, out, indent=2, ensure_ascii=False)


def main(argv: t.Optional[t.Sequence[str]] = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument('--config', required=False)
    parser.add_argument('--log', default="INFO", choices=list(logging._nameToLevel.keys()))

    subparsers = parser.add_subparsers(required=True, dest="subcommand")

    # search
    fn = search
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("-q", "--query", default=None)
    sparser.add_argument("--page", default=None, type=int)
    sparser.add_argument("--per_page", default=None, type=int)

    # post
    fn = post
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument("path", )
    sparser.add_argument("--draft", action="store_true")
    sparser.add_argument("--notice", action="store_true")
    sparser.add_argument("--tag", dest="tags", action="append")
    sparser.add_argument("--id")

    args = parser.parse_args(argv)
    params = vars(args).copy()

    logging.basicConfig(level=getattr(logging, params.pop('log')), stream=sys.stderr)
    params.pop("subcommand")(**params)


if __name__ == '__main__':
    main()
