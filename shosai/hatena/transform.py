import typing as t
import shosai.base.structure as base
from . import structure


def post_from_post(entry: structure.PostDict, *, baseurl: str) -> base.PostDict:
    id = ""
    for link in entry["link"]:
        if link.get("@rel") == "alternate":
            id = link["@href"].replace(baseurl, "").lstrip("/")

    return {
        "id": id,
        "title": entry["title"],
        "tags": [c["@term"] for c in entry["category"]],
        "content": entry["content"]["#text"]
    }
    return entry


def mapping_from_post(entry: structure.PostDict, *, baseurl: str) -> base.PostDict:
    url = ""
    id = ""
    for link in entry["link"]:
        if link.get("@rel") == "edit":
            url = link["@href"]
        if link.get("@rel") == "alternate":
            id = link["@href"].replace(baseurl, "").lstrip("/")
    return {
        "id": id,
        "title": entry["title"],
        "created_at": entry["published"],
        "draft": False,
        "url": url,
        "file": "",  # updated on loading.py
        "tags": [c["@term"] for c in entry["category"]],
    }
    return entry


# todo: typing
def from_search_response(data: t.Dict) -> t.Sequence[base.PostDict]:
    baseurl = ""
    for link in data["feed"]["link"]:
        if link["@rel"] == "alternate":
            baseurl = link["@href"]
    return [
        (post_from_post(entry, baseurl=baseurl), mapping_from_post(entry, baseurl=baseurl))
        for entry in data["feed"]["entry"]
    ]
