import xmltodict


def loads(xml):
    return xmltodict.parse(xml, process_namespaces=False)


def dumps(doc):
    return xmltodict.unparse(doc, full_document=False)


def dumps_as_bytes(doc, *, encoding="utf-8"):
    return xmltodict.unparse(doc, full_document=False).encode(encoding=encoding)
