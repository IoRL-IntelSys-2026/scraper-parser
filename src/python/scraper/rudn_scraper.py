"""Module for interacting with the web scraper."""

# rudn_scraper - web scraper that can fetch pages and files
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

__all__ = ["Options",
           "path_chooser",
           "the_downloader"]

import logging
import ssl
from pathlib import Path

# библиотека urllib очень мощная для работы со ссылками
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import urlopen

import certifi

# доп проверка для универсальности кода (привет pycharm)
from database.instr_db import InstructionDatabase, Mnemonic, TargetPage

# долой edge, слава chrome
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


def path_chooser(
    db_path: Path | None = None,  # локация для базы данных
    downloads: Path | None = None,  # папка для загрузок
) -> tuple[InstructionDatabase, Path]:

    # стандартная локация для датабазы (в папке sql)
    if db_path is None:
        db_path = Path(__file__).resolve().parents[2] / "sql" / "instr_db.sqlite3"
        logger.warning(f"Путь до БД не указан, используется {db_path}")

    # дефолтное название для файла
    if db_path.is_dir() or not db_path.suffix:
        db_path = db_path / "instr_db.sqlite3"

    # выбор конструктора определяет, создавать ли новую базу.
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = (
        InstructionDatabase.bootstrap(str(db_path))
        # автоматизирует создание датабазы при отсутствии
        if not db_path.is_file()
        else InstructionDatabase(db_path)
    )

    # стандартное место для папки загрузок
    if downloads is None:
        downloads = Path(__file__).parent / "downloads"
        logger.warning(f"Папка для загрузок не указана, используется {downloads}")

    downloads.mkdir(parents=True, exist_ok=True)

    return db, downloads


def the_downloader(
    db: InstructionDatabase, download_dir: Path, options: Options
) -> None:
    driver = None

    try:
        driver = webdriver.Chrome(options=options)

        for page in db.get_pages():
            instructions = db.get_doc_instrs(page.idx)

            if not instructions:
                logger.warning(
                    f"Нет инструкций - совершён пропуск: {page.link}"
                )  # warn - устаревший
                continue

            logger.info(f"Скачивание: {page.link}")
            process_page(driver, db, page, download_dir)

    finally:
        if driver is not None:
            driver.quit()
    logger.info(f"Все скаченные файлы находятся в папке {download_dir}.")


def process_page(
    driver: WebDriver, db: InstructionDatabase, page: TargetPage, download_dir: Path
) -> None:
    driver.get(page.link)

    # инструкции для сайтов
    instructions = db.get_doc_instrs(page.idx)

    for instruction in instructions:
        attrs = instruction.attrs
        action = instruction.inst

        # уточнение если инструкция - это скачивание
        if action is Mnemonic.DOWNLOAD_TARGET:
            # найти указанный элемент
            tag = attrs["tag"] or "a"
            elements = driver.find_elements(By.TAG_NAME, tag)

            for name, value in attrs.items():
                if name != "tag":
                    elements = [
                        element
                        for element in elements
                        if element.get_attribute(name) == value
                    ]

            if not elements:
                logger.error("Ссылка для скачивания не найдена!")
                continue

            # получить ссылку сайта
            url = urljoin(driver.current_url, elements[0].get_attribute("href"))

            filename = unquote(
                Path(url.split("?")[0]).name
            )  # unquote делает названия файлов нормальными
            if not filename:
                filename = f"document_{page.idx}.pdf"
            filepath = download_dir / filename

            # таймер для ожидания - 30 секунд, но можно изменить
            with (
                urlopen(
                    url,
                    timeout=30,
                    context=ssl.create_default_context(cafile=certifi.where()),
                ) as sock,
                filepath.open("wb") as f,
            ):
                f.write(
                    sock.read()
                )  # readinto() ожидает буфер, доступный для записи, однако f.raw является файлом, а не буфером, который требуется этому методу

            logger.info(f"Скачано: {filename}")

        # код для HTML
        elif action is Mnemonic.EXTRACT_SUBTREE:
            tag = attrs.get("tag", "*")
            # если wifi рудн начнет создавать проблемы - это решит их
            from selenium.common.exceptions import (
                StaleElementReferenceException,
            )

            for attempt in range(2):
                try:
                    elements = driver.find_elements(By.TAG_NAME, tag)
                    for name in ("id", "class"):
                        if name in attrs:
                            elements = [
                                element
                                for element in elements
                                if (
                                    # <= проверяет, присутствуют ли все запрашиваемые классы,
                                    # даже если у элемента есть дополнительные классы
                                    attrs["class"]
                                    <= frozenset(
                                        (element.get_attribute(name) or "").split()
                                    )
                                    if name == "class"
                                    else element.get_attribute(name)
                                    == attrs.get(name, "")
                                )
                            ]
                    break  # все классно и супер
                except StaleElementReferenceException:
                    if attempt == 1:
                        elements = []  # продолжить код не ломаясь
                    continue

            # скачать страницу как файл html
            if elements:
                # я копирую последнее слово из ссылки чтобы было понятнее, что скачалось помимо просто "page_9.html"
                last_word = urlparse(page.link).path.rstrip("/").split("/")[-1]
                filename = f"page_{page.idx} {unquote(last_word)}.html"
                filepath = download_dir / filename
                filepath.write_text(
                    elements[0].get_attribute("outerHTML") or "", encoding="utf-8"
                )
                logger.info(f"HTML скачан: {filename}")
            else:
                logger.error(f"Не найден подходящий HTML элемент в {page.link}")


