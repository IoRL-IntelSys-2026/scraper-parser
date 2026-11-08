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

import logging
import os
import tempfile
from pathlib import Path
from typing import Final

from database.instr_db import Mnemonic
from scraper.rudn_scraper import (
    BrowserType,
    create_browser_instance,
    path_chooser,
    process_page,
)

logger = logging.getLogger(__name__)


def test_download_one_page() -> None:
    """
    Интеграционный тест: скачивает одну страницу и один HTML-фрагмент.

    Создаёт временную базу данных и каталог загрузок через
    :func:`path_chooser`, поднимает headless-экземпляр Chrome через
    :func:`create_browser_instance` и проверяет работу
    :func:`process_page` на двух страницах из БД:

    - странице с инструкцией ``Mnemonic.DOWNLOAD_TARGET`` (скачивание
      связанного файла);
    - странице с инструкцией ``Mnemonic.EXTRACT_SUBTREE`` (извлечение
      HTML-фрагмента).

    В конце проверяет, что во временном каталоге появился хотя бы один
    непустой файл.

    Notes
    -----
    Если переменная окружения ``CHROMEWEBDRIVER`` задана (например,
    в CI на GitHub Actions / Ubuntu), путь к драйверу берётся из неё,
    а к Chrome добавляются headless-опции: ``--headless=new``,
    ``--disable-gpu``, ``--js-flags="--jitless"``,
    ``--disable-dev-shm-usage``, ``--window-size=1920,1200``.
    В остальных случаях используется драйвер, найденный Selenium
    автоматически, без дополнительных опций.

    Драйвер закрывается в блоке ``finally``, временный каталог
    удаляется автоматически по выходе из ``TemporaryDirectory``.
    """
    options: Final = []
    chromedriver_path = None
    if (chromedriver := os.getenv("CHROMEWEBDRIVER")) is not None:
        # I LOVE GITHUB
        # I LOVE UBUNTU RAHHHHHHH
        chromedriver_path = Path(chromedriver).resolve(True) / "chromedriver"
        options.extend(
            [
                "--headless=new",
                "--disable-gpu",
                '--js-flags="--jitless"',
                "--disable-dev-shm-usage",
                "--window-size=1920,1200",
            ]
        )

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        tmp_path: Final = Path(temp_dir)
        db, downloads = path_chooser(True, tmp_path, tmp_path)
        driver: Final = create_browser_instance(
            BrowserType.CHROME,
            options,
            str(chromedriver_path) if chromedriver_path is not None else None,
            str(downloads),
        )
        chunksz: Final = 33554432  # 32 мебибайта
        pages: Final = db.get_pages()
        dl_page: Final = next(
            (
                page
                for page in pages
                if any(
                    instruction.inst is Mnemonic.DOWNLOAD_TARGET
                    for instruction in db.get_doc_instrs(page.idx)
                )
            ),
            None,
        )

        et_page: Final = next(
            (
                page
                for page in pages
                if any(
                    instruction.inst is Mnemonic.EXTRACT_SUBTREE
                    for instruction in db.get_doc_instrs(page.idx)
                )
            ),
            None,
        )

        assert dl_page is not None, (
            "Не найдена страница с инструкциями для скачивания файла."
        )
        assert et_page is not None, (
            "Не найдена страница с инструкциями для скачивания HTML."
        )

        try:
            process_page(driver, db, dl_page, tmp_path, chunksz)
            process_page(driver, db, et_page, tmp_path, chunksz)
        finally:
            driver.quit()

        files: Final = list(tmp_path.iterdir())

        assert files, "Файлы не были скачаны."

        assert any(
            file.is_file() and file.stat().st_size > 0 for file in files
        ), "Скачанные файлы пустые."
