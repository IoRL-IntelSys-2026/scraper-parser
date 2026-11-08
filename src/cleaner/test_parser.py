"""Тесты для модуля очистки HTML."""

# test_parser - Tests for the HTML cleaner
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

import re
import tempfile
from pathlib import Path

from .parser import clean_html_directory


def _normalize_whitespace(text: str) -> str:
    """Заменяет любые последовательности пробельных символов одним пробелом.

    Parameters
    ----------
    text : str
        Исходный текст.

    Returns
    -------
    str
        Текст с единичными пробелами, без пробелов по краям.
    """
    return re.sub(r"\s+", " ", text).strip()


def test_clean_html() -> None:
    """Проверяет, что `clean_html_directory` очищает HTML-файл.

    Во временном каталоге создаётся страница со скриптами и тремя
    вложенными `div`. После очистки должен появиться файл
    `cleaned_example.html` без скриптов и с одним `div` вместо трёх.
    Содержимое сравнивается без учёта пробельных символов.
    """
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        tmp_path = Path(d)
        input_file = tmp_path / "example.html"
        input_file.write_text(
            """<html>
  <head>
    <script>alert("this is a test");</script>
     <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  </head>
  <body>
    <div>
      <div>
        <div>
          <p>Hello</p>
        </div>
      </div>
    </div>
    <script>alert("this is a test");</script>
  </body>
</html>""",
            encoding="utf-8",
        )

        # 2. Run your cleaning function on the test folder
        clean_html_directory(target_dir=tmp_path)

        # 3. Verify the script stripped elements and flattened the structure properly
        output_file = tmp_path / "cleaned_example.html"
        assert output_file.exists(), (
            "The cleaned file output was not generated."
        )

        actual_output = output_file.read_text(encoding="utf-8")

    # Matches BeautifulSoup's attribute order and structural unnesting limit
    expected_output = """<html>
  <head>
     <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  </head>
  <body>
    <div>
      <p>Hello</p>
    </div>
  </body>
</html>"""

    assert _normalize_whitespace(actual_output) == _normalize_whitespace(
        expected_output
    )
