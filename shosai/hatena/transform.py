import typing as t
import shosai.base.structure as base
from . import structure


def post_from_post(entry: structure.PostDict) -> base.PostDict:
    categories = entry.get("category", [])
    if hasattr(categories, "keys"):
        categories = [categories]
    return {
        "title": entry["title"],
        "tags": [c["@term"] for c in categories],
        "content": entry["content"]["#text"],
    }
    return entry


def mapping_from_post(entry: structure.PostDict) -> base.PostDict:
    url = ""
    id = ""
    name = ""
    for link in entry["link"]:
        if link.get("@rel") == "edit":
            url = link["@href"]
            id = link["@href"].rsplit("/", 1)[-1]
        if link.get("@rel") == "alternate":
            name = link["@href"].rsplit("/entry/", 1)[-1]
    return {
        "id": id,
        "name": name,
        "title": entry["title"],
        "created_at": entry["published"],
        "draft": entry["app:control"]["app:draft"] == "yes",
        "url": url,
        "file": "",  # updated on loading.py
    }
    return entry


# todo: typing
def from_search_response(
    data: t.Dict,
) -> t.Sequence[t.Tuple[base.PostDict, base.MappingDict]]:
    return [
        (post_from_post(entry), mapping_from_post(entry))
        for entry in data["feed"]["entry"]
    ]


def from_fetch_response(data: t.Dict) -> t.Tuple[base.PostDict, base.MappingDict]:
    entry = data["entry"]
    return (post_from_post(entry), mapping_from_post(entry))
