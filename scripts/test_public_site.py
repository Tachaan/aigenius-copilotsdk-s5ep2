from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_public_site import check_site
from rewrite_doc_links import repo_url_target


class PublicSiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        self.write("index.html")
        self.write("search/search_index.json")

    def write(self, relative: str) -> None:
        path = self.site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    def test_static_assets_are_allowed(self) -> None:
        for name in ("assets/main.js", "assets/main.css", "Slide1.png",
                     "system-map/map.html", "system-map/map.json",
                     "sitemap.xml.gz", ".nojekyll"):
            self.write(name)
        self.assertEqual([], check_site(self.site))

    def test_sensitive_and_unexpected_files_are_rejected(self) -> None:
        for name in (".env", ".git/config", "retail.db", "trace.log",
                     "key.pem", "backup.zip", "app.py", "app.cs",
                     "logs/activity.json", ".github/config.json"):
            with self.subTest(name=name):
                self.write(name)
                self.assertTrue(any(name in error for error in check_site(self.site)))

    def test_required_output_is_checked(self) -> None:
        (self.site / "index.html").unlink()
        self.assertIn("missing index.html", check_site(self.site))

    def test_missing_site_is_rejected(self) -> None:
        self.assertTrue(check_site(self.site / "absent"))

    def test_fork_and_original_document_links_are_validated(self) -> None:
        for owner in ("Tachaan", "vicperdana"):
            for kind in ("blob", "tree"):
                url = (
                    f"https://github.com/{owner}/aigenius-copilotsdk-s5ep2"
                    f"/{kind}/main/docs/index.md"
                )
                self.assertEqual((kind, "docs/index.md"), repo_url_target(url))


if __name__ == "__main__":
    unittest.main()
