import typing as t
import shosai.base.structure as base
from shosai.langhelpers import normalize_linesep_text
from . import structure
from .resources import SearchResponseDict


def post_from_post(post: structure.PostDict) -> base.PostDict:
    # immutable is beter?
    post["tags"] = [t["name"] for t in post["tags"]]
    post["content"] = normalize_linesep_text(post.pop("body"))
    return post


def mapping_from_post(post: structure.PostDict) -> structure.MappingDict:
    data = post.copy()
    for k in ["tags", "body", "user", "comments"]:
        data.pop(k, None)
    return data


def from_search_response(data: SearchResponseDict) -> t.Sequence[base.PostDict]:
    return [(post_from_post(post), mapping_from_post) for post in data["posts"]]