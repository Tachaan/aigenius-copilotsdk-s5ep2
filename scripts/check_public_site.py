#!/usr/bin/env python3
"""Reject unexpected files in the Pages artifact; this is not a secret scanner."""

from __future__ import annotations

import argparse
from pathlib import Path

ALLOWED_SUFFIXES = {
    ".css", ".html", ".ico", ".jpeg", ".jpg", ".js", ".json", ".map",
    ".png", ".svg", ".webp", ".woff", ".woff2", ".xml",
}
ALLOWED_NAMES = {".nojekyll", "sitemap.xml.gz"}
FORBIDDEN_PARTS = {
    ".git", ".github", ".vscode", "__pycache__", "logs", "node_modules",
    "src", "tests",
}


def check_site(site: Path) -> list[str]:
    """Return artifact boundary violations, without printing file contents."""
    if site.is_symlink() or not site.is_dir():
        return ["site must be an existing, non-symlink directory"]
    problems: list[str] = []
    for required in ("index.html", "search/search_index.json"):
        if not (site / required).is_file():
            problems.append(f"missing {required}")
    for path in sorted(site.rglob("*")):
        relative = path.relative_to(site)
        parts = [part.lower() for part in relative.parts]
        if path.is_symlink():
            problems.append(f"symlink: {relative.as_posix()}")
        elif any(
            part in FORBIDDEN_PARTS
            or (part.startswith(".") and part != ".nojekyll")
            for part in parts
        ):
            problems.append(f"private/build path: {relative.as_posix()}")
        elif path.is_file() and (
            path.name not in ALLOWED_NAMES
            and path.suffix.lower() not in ALLOWED_SUFFIXES
        ):
            problems.append(f"unapproved file type: {relative.as_posix()}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", nargs="?", type=Path, default=Path("site"))
    args = parser.parse_args()
    problems = check_site(args.site)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1
    print("Pages artifact boundary check passed (content review still required).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
