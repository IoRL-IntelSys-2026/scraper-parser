"""Module for cleaning HTML pages."""

# parser - Functions for removing unneeded elements from HTML
# Copyright (C) 2026  The scraper-parser contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["clean_html_directory"]

import logging
import re
from pathlib import Path
from typing import Final, TypeIs

from bs4 import BeautifulSoup, Comment
from bs4.element import NavigableString, PageElement, Tag

logger = logging.getLogger(__name__)


def is_pe_subclass(elem: PageElement) -> TypeIs[NavigableString | Tag]:
    """Checks that `elem` is a strict subclass of `PageElement`."""
    return isinstance(elem, PageElement) and type(elem) is not PageElement


def clean_html_directory(target_dir: str | Path = ".") -> None:
    """
    Scans a directory for HTML files, strips out tracking tags/comments,
    unnests structural wrappers, and saves optimized output copies.
    """
    directory: Final = Path(target_dir)
    logger.info(
        f"Starting Batch HTML Parser scanning directory: {directory.resolve(True)}"
    )

    # 4. Using pathlib glob to find html targets safely
    for file_path in directory.glob("*.html"):
        if file_path.name.startswith("cleaned_"):
            continue

        logger.info(f"Processing file: {file_path.name}")

        # Read the file text directly using pathlib
        html_content = file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html_content, "html.parser")

        # 2. Replaced extract() with decompose() as they behave identically here
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.decompose()

        # 3. Clean up unwanted layout tags
        for tag_name in ["script", "style", "link", "header", "footer"]:
            for element in soup.find_all(tag_name):
                element.decompose()

        # Flatten nested styling wrappers
        flattening = True
        while flattening:
            flattening = False
            for div in soup.find_all("div"):
                # mypy cannot narrow the type by itself, so a type
                # narrowing function is used.
                children_tags = [
                    c for c in div.contents if is_pe_subclass(c) and c.name is not None
                ]
                if len(children_tags) == 1 and children_tags[0].name == "div":
                    div.unwrap()
                    flattening = True

        # Optimize vertical empty line spacing
        cleaned_html_string = re.sub(r"\n\s*\n", "\n", str(soup))

        # Save output file cleanly via pathlib path math
        output_file_path = directory / f"cleaned_{file_path.name}"
        output_file_path.write_text(cleaned_html_string, encoding="utf-8")

        # 3. Utilizing logging instead of print calls
        logger.info(f"Saved clean file as: {output_file_path.name}")


if __name__ == "__main__":
    clean_html_directory()
