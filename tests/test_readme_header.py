"""Acceptance checks for the README header's HTML comment boundaries.

Uses only the Python standard library; does not fetch remote images.
Run with: python3 -m unittest discover -s tests -p test_readme_header.py
"""

from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import parse_qs, urlsplit


class VisibleImages(HTMLParser):
    """Collect HTML image elements; HTMLParser ignores commented markup."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


class ReadmeHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        readme = Path(__file__).resolve().parents[1] / "README.md"
        parser = VisibleImages()
        parser.feed(readme.read_text(encoding="utf-8"))
        parser.close()
        cls.images = parser.images

    def test_header_banner_is_not_visible(self):
        for image in self.images:
            with self.subTest(image=image.get("alt", image.get("src"))):
                self.assertNotEqual(image.get("alt"), "Deb Barman header")
                source = urlsplit(image.get("src") or "")
                if source.hostname == "capsule-render.vercel.app":
                    self.assertNotIn(
                        "header", parse_qs(source.query).get("section", [])
                    )

    def test_comment_ends_before_the_profile_image(self):
        self.assertTrue(self.images, "The header comment must not hide the README")
        self.assertEqual(self.images[0].get("src"), "public/profile_img.jpeg")
        self.assertEqual(self.images[0].get("alt"), "Deb Barman")

    def test_footer_banner_remains_visible(self):
        footers = []
        for image in self.images:
            source = urlsplit(image.get("src") or "")
            if (
                source.hostname == "capsule-render.vercel.app"
                and "footer" in parse_qs(source.query).get("section", [])
            ):
                footers.append(image)
        self.assertEqual(len(footers), 1, "Only the header banner should be hidden")


if __name__ == "__main__":
    unittest.main()
