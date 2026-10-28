"""Tests for the RUDN scraper."""

# test_rudn_scraper - tests for the smart web scraper
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

import os
import tempfile
from pathlib import Path
from typing import Final

from database.instr_db import Mnemonic
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from scraper.rudn_scraper import path_chooser, process_page


def test_download_one_page() -> None:
    if (chromedriver := os.getenv("CHROMEWEBDRIVER")) is not None:
        # I LOVE GITHUB
        # I LOVE UBUNTU RAHHHHHHH
        chromedriver_path = Path(chromedriver).resolve(True) / "chromedriver"
        service: Final = Service(str(chromedriver_path))
        options: Final = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=Options())

    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
        db, _ = path_chooser(downloads=tmp_path)

        page = next(
            (
                page
                for page in db.get_pages()
                if any(
                    instruction.inst is Mnemonic.DOWNLOAD_TARGET
                    for instruction in db.get_doc_instrs(page.idx)
                )
            ),
            None,
        )

        assert page is not None, "Не найдена страница с инструкцией для скачивания."

        try:
            process_page(driver, db, page, tmp_path)
        finally:
            driver.quit()

        files = list(tmp_path.iterdir())

        assert files, f"Файлы не были скачаны из {page.link}"

        assert any(file.is_file() and file.stat().st_size > 0 for file in files), (
            "Скачанные файлы пустые."
        )

        print(f"Успешный тест: {page.link}")
