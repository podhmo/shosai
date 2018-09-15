import unittest
import textwrap


class ParseTitleTests(unittest.TestCase):
    def _callFUT(self, text):
        from docbasesync.parsing import parse_title
        return parse_title(text)

    def test_it(self):
        title = "[aaa][bb][memo]hello"
        got = self._callFUT(title)
        self.assertEqual(got.tags, ["aaa", "bb", "memo"])
        self.assertEqual(got.title, "hello")

    def test_it__notags(self):
        title = "hello"
        got = self._callFUT(title)
        self.assertEqual(got.title, "hello")

    def test_it__notags2(self):
        title = "hello [xxx]"
        got = self._callFUT(title)
        self.assertEqual(got.title, "hello [xxx]")

    def test_it__with_whitespace(self):
        title = " [aaa]  [bb] [memo] hello"
        got = self._callFUT(title)
        self.assertEqual(got.tags, ["aaa", "bb", "memo"])
        self.assertEqual(got.title, "hello")

    def test_it__with_suffix(self):
        title = "[aaa][bb][memo]hello [xxx]"
        got = self._callFUT(title)
        self.assertEqual(got.tags, ["aaa", "bb", "memo"])
        self.assertEqual(got.title, "hello [xxx]")


class ParseArticleTests(unittest.TestCase):
    def _getTarget(self):
        from docbasesync.parsing import parse_article
        return parse_article

    def _callFUT(self, text):
        return self._getTarget()(text)

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

    def test_it__with_image(self):
        from docbasesync.parsing import Image
        text = textwrap.dedent(
            """
# section

![foo](https://example.net/images/foo.png))
![bar](https://example.net/images/bar.png))
![boo](boo.png))
"""
        ).strip()
        parsed = self._callFUT(text)
        self.assertEqual(parsed.title, "section")
        self.assertEqual(parsed.tags, [])
        self.assertEqual(parsed.content, "\n".join(text.split("\n")[1:]).strip())
        images = [
            Image(**{
                'src': 'https://example.net/images/foo.png',
                'text': 'foo'
            }),
            Image(**{
                'src': 'https://example.net/images/bar.png',
                'text': 'bar'
            }),
            Image(**{
                'src': 'boo.png',
                'text': 'boo'
            }),
        ]
        self.assertEqual(parsed.images, images)
