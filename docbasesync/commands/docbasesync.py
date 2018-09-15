import sys
import typing as t
import os.path
import json
import logging
import re  # xxx
from docbasesync.langhelpers import (
    NameStore,
    normalize_linesep_text,
)
logger = logging.getLogger(__name__)


def search(
    *,
    config_path: str,
    mapping_path: str,
    save: bool = False,
    query: t.Optional[str] = None,
    page: t.Optional[int] = None,
    per_page: t.Optional[int] = None,
    out: t.Optional[t.IO] = None,
) -> None:
    from docbasesync import App
    out = out or sys.stdout
    app = App(config_path, mapping_path=mapping_path)
    with app.resource as r:
        data = r.search(q=query, page=page, per_page=per_page)
    json.dump(data, out, indent=2, ensure_ascii=False)
    if save:
        with app.saver as append:
            for post in data["posts"]:
                post["tags"] = [t["name"] for t in post["tags"]]
                append(post)


def pull(
    *,
    config_path: str,
    mapping_path: str,
    path: str,
    out: t.Optional[t.IO] = None,
) -> None:
    from docbasesync import App
    out = out or sys.stdout
    app = App(config_path, mapping_path=mapping_path)
    with app.resource as r:
        meta = app.loader.lookup(path)
        if meta is None:
            print(f"mapped file is not found {path}", file=sys.stderr)
            sys.exit(1)
        post = r.fetch(meta["id"])
        post["body"] = normalize_linesep_text(post["body"])
    with app.saver as append:
        post["tags"] = [t["name"] for t in post["tags"]]
        append(post, filepath=meta["file"])


def push(
    *,
    config_path: str,
    mapping_path: str,
    save: bool = True,
    path: str,
    draft: t.Optional[bool] = None,
    notice: bool = False,
    id: t.Optional[str] = None,
    scope: t.Optional[str] = None,
    groups: t.Optional[t.Sequence[str]] = None,
    out: t.Optional[t.IO] = None,
) -> None:
    from docbasesync import App
    from docbasesync import parsing
    out = out or sys.stdout
    app = App(config_path)
    with app.resource as r:
        with open(path) as rf:
            parsed = parsing.parse_article(rf.read())

        content = parsed.content

        # parse article and upload images as attachments.
        attachments = []
        namestore = NameStore()

        for image in parsed.images:
            if "://" in image.src:
                continue
            imagepath = os.path.join(os.path.dirname(path), image.src)
            if not os.path.exists(imagepath):
                logger.info("image: %s is not found (where %s)", imagepath, path)
                continue
            if image.src in namestore:
                continue
            namestore[image.src] = os.path.basename(imagepath)
            attachments.append(
                r.attachment.build_content_from_file(imagepath, name=namestore[image.src])
            )
        if attachments:
            logger.info("attachments is found, the length is %d", len(attachments))
            uploaded = r.attachment(attachments)

            logger.info("overwrite passed article %s", path)
            for uploaded_image in uploaded:
                image_src = namestore.reverse_lookup(uploaded_image["name"])
                rx = re.compile(f"\\( *{image_src}*\\)")
                content = rx.subn(f"({uploaded_image['url']})", content)[0]
            with open(path, "w") as wf:
                tagspart = "".join([f"[{t}]" for t in parsed.tags])
                wf.write(f"#{tagspart}{parsed.title}\n")
                wf.write("")
                wf.write(content)

        meta = app.loader.lookup(path)
        tags = parsed.tags
        if meta is not None:
            if draft is None:
                draft = meta.get("draft", True)
            id = id or meta["id"]
            scope = scope or meta["scope"]
            groups = groups or meta["groups"]
            tags = tags or meta["tags"]

        data = r.post(
            parsed.title or (meta and meta.get("title")) or "",
            content,
            tags=tags,
            id=id,
            scope=scope,
            groups=groups,
            draft=bool(draft),
            notice=notice,
        )
    json.dump(data, out, indent=2, ensure_ascii=False)
    if save:
        with app.saver as append:
            append(data, writefile=path)


def main(argv: t.Optional[t.Sequence[str]] = None) -> None:
    import argparse
    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument('--log', default="INFO", choices=list(logging._nameToLevel.keys()))
    subparsers = parser.add_subparsers(required=True, dest="subcommand")

    # search
    fn = search
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument('-c', '--config', required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("--save", action="store_true")
    sparser.add_argument("-q", "--query", default=None)
    sparser.add_argument("--page", default=None, type=int)
    sparser.add_argument("--per_page", default=None, type=int)

    # pull
    fn = pull
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument('-c', '--config', required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("path")

    # push
    fn = push
    sparser = subparsers.add_parser(fn.__name__, description=fn.__doc__)
    sparser.set_defaults(subcommand=fn)
    sparser.add_argument('-c', '--config', required=False, dest="config_path")
    sparser.add_argument("--mapping", default=None, type=int, dest="mapping_path")
    sparser.add_argument("--unsave", action="store_false", dest="save")
    sparser.add_argument("path")
    sparser.add_argument("--draft", action="store_true", default=None)
    sparser.add_argument("--notice", action="store_true")
    sparser.add_argument("--id")
    sparser.add_argument("--scope")
    sparser.add_argument("--group", dest="groups", action="append")

    args = parser.parse_args(argv)
    params = vars(args).copy()

    logging.basicConfig(level=getattr(logging, params.pop('log')), stream=sys.stderr)
    params.pop("subcommand")(**params)


if __name__ == '__main__':
    main()
