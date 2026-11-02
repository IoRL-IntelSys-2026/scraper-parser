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

__all__ = [
    "BrowserType",
    "create_browser_instance",
    "path_chooser",
    "process_page",
    "the_downloader"
]

import enum
import logging
import ssl
from pathlib import Path
from typing import Final

# библиотека urllib очень мощная для работы со ссылками
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import urlopen

import certifi

# долой edge, слава chrome
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

# доп проверка для универсальности кода (привет pycharm)
from database.instr_db import (
    InstAttribute,
    InstructionDatabase,
    Mnemonic,
    TargetPage,
)

logger: Final = logging.getLogger(__name__)

class BrowserType(enum.StrEnum):
    CHROME = "chrome"
    EDGE = "edge"
    FIREFOX = "firefox"
    IE = "ie"
    SAFARI = "safari"
    WEBKITGTK = "webkitgtk"
    WPEWEBKIT = "wpewebkit"

def create_browser_instance(
        browser: BrowserType,
        instance_args: list[str],
        driver_path: str | None = None,
        downloads: str = '.'
) -> WebDriver:
    """Creates a browser instance based on the chosen parameters."""
    prefs: Final = {
        "download.default_directory": downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }
    # Это нарушает DRY (и ужасно выглядит), но mypy иначе не понимает
    if browser is BrowserType.CHROME:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", prefs)
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.ChromeService(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    elif browser is BrowserType.EDGE:
        options = webdriver.EdgeOptions()
        options.add_experimental_option("prefs", prefs)
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.EdgeService(driver_path)
        driver = webdriver.Edge(service=service, options=options)
    elif browser is BrowserType.FIREFOX:
        options = webdriver.FirefoxOptions()
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.FirefoxService(driver_path)
        driver = webdriver.Firefox(service=service, options=options)
    elif browser is BrowserType.IE:
        options = webdriver.IeOptions()
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.IeService(driver_path)
        driver = webdriver.Ie(service=service, options=options)
    elif browser is BrowserType.SAFARI:
        options = webdriver.SafariOptions()
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.SafariService(driver_path)
        driver = webdriver.Safari(service=service, options=options)
    elif browser is BrowserType.WEBKITGTK:
        options = webdriver.WebKitGTKOptions()
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.WebKitGTKService(driver_path)
        driver = webdriver.WebKitGTK(service=service, options=options)
    else:
        options = webdriver.WPEWebKitOptions()
        for arg in instance_args:
            options.add_argument(arg)
        service = webdriver.WPEWebKitService(driver_path)
        driver = webdriver.WPEWebKit(service=service, options=options)

    return driver
        

def path_chooser(
    create_db: bool, # Создавать ли базу данных
    db_path: Path | None = None,  # локация для базы данных
    downloads: Path | None = None,  # папка для загрузок
) -> tuple[InstructionDatabase, Path]:

    # стандартная локация для датабазы (в папке sql)
    if db_path is None:
        db_path = Path(__file__).parents[1] / "sql" / "instr_db.sqlite3"
        logger.warning(f"Путь до БД не указан, используется {db_path}")

    # дефолтное название для файла
    if db_path.is_dir() or not db_path.suffix:
        db_path = db_path / "instr_db.sqlite3"

    db_path.parent.mkdir(exist_ok=True)
    # выбор конструктора определяет, создавать ли новую базу.
    # Бросает исключение, если БД должна существовать, а её нет.
    db = (
        InstructionDatabase.bootstrap(str(db_path))
        if create_db
        else InstructionDatabase(db_path)
    )

    # стандартное место для папки загрузок
    if downloads is None:
        downloads = Path.home() / "Downloads"
        logger.warning(f"Папка для загрузок не указана, используется {downloads}")

    downloads.mkdir(exist_ok=True)

    return db, downloads


def the_downloader(
    db: InstructionDatabase,
    download_dir: Path,
    driver: WebDriver,
    chunksz: int = 33554432 # 32 мебибайта
) -> None:
    try:
        for page in db.get_pages():
            logger.info(f"Скачивание: {page.link}")
            process_page(driver, db, page, download_dir, chunksz)
    finally:
        driver.quit()
    logger.info(f"Все скаченные файлы находятся в папке {download_dir}.")

def compare_attrs(attrs: InstAttribute, elem: WebElement) -> bool:
    return all(
        attrs["class"] <= frozenset((elem.get_attribute(name) or "").split())
        if name == "class"
        else elem.get_attribute(name) == value
        for name, value in attrs.items()
        if name != "tag"
    )

def process_page(
    driver: WebDriver,
    db: InstructionDatabase,
    page: TargetPage,
    download_dir: Path,
    chunksz: int
) -> None:
    # инструкции для сайтов
    instructions: Final = db.get_doc_instrs(page.idx)
    ctx: Final = ssl.create_default_context(cafile=certifi.where())
    # Для хранения полученного фрагмента
    chunk_buffer: Final = bytearray(chunksz)
    # Через `memoryview` можно заполнять буфер без копий
    chunk_view: Final = memoryview(chunk_buffer)
    elements: Final = [] # В конце записывает все одновременно
    nbytes = 0 # сколько байтов прочитано
    driver.get(page.link)

    if not instructions:
        logger.warning(f"Нет инструкций - совершён пропуск: {page.link}")

    for instruction in instructions:
        attrs = instruction.attrs
        action = instruction.inst

        # уточнение если инструкция - это скачивание
        if action is Mnemonic.DOWNLOAD_TARGET:
            # найти указанный элемент
            tag = attrs["tag"] or "a"
            targets = [
                element
                for element in driver.find_elements(By.TAG_NAME, tag)
                if compare_attrs(attrs, element)
            ]

            if not targets:
                logger.error("Ссылки для скачивания не найдены!")
                continue

            for (i, target) in enumerate(targets):
                # получить ссылку сайта
                url = urljoin(driver.current_url, target.get_attribute("href"))

                filename = unquote(
                    Path(url.split("?")[0]).name
                )  # unquote делает названия файлов нормальными
                if not filename:
                    filename = f"document_{page.idx}_{i}.pdf"
                filepath = download_dir / filename

                # таймер для ожидания - 30 секунд, но можно изменить
                with (
                        urlopen(url, timeout=30, context=ctx) as sock,
                        filepath.open("wb") as f
                ):
                    # Читает и записывает файл кусками размером `chunksz`.
                    # Можно уменьшить кол-во шагов, читая напрямую в `mmap`,
                    # но тогда пользователь должен заранее знать максимальный
                    # размер файла, т.к. расширение проецированного файла -
                    # долгая операция
                    while (nbytes := sock.readinto(chunk_view)):
                        f.write(chunk_view[:nbytes])
                logger.info(f"Скачано: {filename}")

        # код для HTML
        elif action is Mnemonic.EXTRACT_SUBTREE:
            tag = attrs.get("tag", "*")
            # если wifi рудн начнет создавать проблемы - это решит их
            for attempt in range(2):
                try:
                    temp_elem = driver.find_elements(By.TAG_NAME, tag)
                    elements.extend([
                        element
                        for element in temp_elem
                        if compare_attrs(attrs, element)
                    ])
                    break  # все классно и супер
                except StaleElementReferenceException as e:
                    logger.warning(
                        f"Поймано исключение: {e}, попытка #{attempt}"
                    )

            # скачать страницу как файл html
            if elements:
                # я копирую последнее слово из ссылки
                # чтобы было понятнее, что скачалось помимо просто "page_9.html"
                last_word = urlparse(page.link).path.rstrip("/").split("/")[-1]
                filename = f"page_{page.idx} {unquote(last_word)}.html"
                filepath = download_dir / filename
                filepath.write_text(
                    "".join(
                        elem.get_attribute("outerHTML") or ""
                        for elem in elements
                    ),
                    encoding="utf-8"
                )
                logger.info(f"HTML скачан: {filename}")
            else:
                logger.error(f"Не найден подходящий HTML элемент в {page.link}")


