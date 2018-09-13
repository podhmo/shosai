import unittest
import textwrap


class Tests(unittest.TestCase):
    def _getTarget(self):
        from docbasesync.parsing import parse_article
        return parse_article

    def _callFUT(self, text):
        from io import StringIO
        return self._getTarget()(StringIO(text))

    def test_it(self):
        text = textwrap.dedent(
            """
# [aaa][bb] [memo]hello

this is first article

## subsection

- x
- y
- z
"""
        ).strip()
        parsed = self._callFUT(text)
        self.assertEqual(parsed.title, "hello")
        self.assertEqual(parsed.tags, ["aaa", "bb", "memo"])
        self.assertEqual(parsed.content, "\n".join(text.split("\n")[1:]).strip())
