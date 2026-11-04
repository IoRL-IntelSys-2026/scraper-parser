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
    """
    Поддерживаемые типы браузеров для Selenium WebDriver.

    Значения соответствуют именам браузеров в нижнем регистре.
    """
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
    """
    Создаёт экземпляр веб-драйвера выбранного браузера.

    Для Chromium-подобных браузеров (Chrome, Edge) настраиваются
    параметры скачивания файлов: каталог загрузок, отключение запроса
    подтверждения, автоматическое открытие PDF во внешнем просмотрщике.
    Для остальных браузеров применяются только аргументы из
    ``instance_args``.

    Parameters
    ----------
    browser : BrowserType
        Тип создаваемого браузера.
    instance_args : list of str
        Дополнительные аргументы командной строки, передаваемые
        драйверу (например, ``["--headless", "--no-sandbox"]``).
    driver_path : str or None, optional
        Путь к исполняемому файлу драйвера. Если ``None``, Selenium
        попытается найти драйвер автоматически. По умолчанию — ``None``.
    downloads : str, optional
        Каталог, в который браузер будет сохранять скачанные файлы.
        Учитывается только для Chrome и Edge. По умолчанию — ``'.'``.

    Returns
    -------
    WebDriver
        Настроенный экземпляр веб-драйвера. Конкретный класс зависит
        от значения ``browser``.

    Notes
    -----
    Значение ``browser``, не совпадающее ни с одним из явно обработанных
    вариантов, трактуется как ``BrowserType.WPEWEBKIT`` — создаётся
    соответствующий драйвер.
    """
    prefs: Final = {
        "download.default_directory": downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }
    # Это нарушает DRY (и ужасно выглядит), но mypy иначе не понимает
    if browser is BrowserType.CHROME:
        chrome_options: Final = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", prefs)
        for arg in instance_args:
            chrome_options.add_argument(arg)
        chrome_service: Final = webdriver.ChromeService(driver_path)
        return webdriver.Chrome(service=chrome_service, options=chrome_options)
    elif browser is BrowserType.EDGE:
        edge_options: Final = webdriver.EdgeOptions()
        edge_options.add_experimental_option("prefs", prefs)
        for arg in instance_args:
            edge_options.add_argument(arg)
        edge_service: Final = webdriver.EdgeService(driver_path)
        return webdriver.Edge(service=edge_service, options=edge_options)
    elif browser is BrowserType.FIREFOX:
        firefox_options: Final = webdriver.FirefoxOptions()
        for arg in instance_args:
            firefox_options.add_argument(arg)
        firefox_service: Final = webdriver.FirefoxService(driver_path)
        return webdriver.Firefox(
            service=firefox_service,
            options=firefox_options
        )
    elif browser is BrowserType.IE:
        ie_options: Final = webdriver.IeOptions()
        for arg in instance_args:
            ie_options.add_argument(arg)
        ie_service: Final = webdriver.IeService(driver_path)
        return webdriver.Ie(service=ie_service, options=ie_options)
    elif browser is BrowserType.SAFARI:
        safari_options: Final = webdriver.SafariOptions()
        for arg in instance_args:
            safari_options.add_argument(arg)
        safari_service: Final = webdriver.SafariService(driver_path)
        return webdriver.Safari(service=safari_service, options=safari_options)
    elif browser is BrowserType.WEBKITGTK:
        gtk_options: Final = webdriver.WebKitGTKOptions()
        for arg in instance_args:
            gtk_options.add_argument(arg)
        gtk_service: Final = webdriver.WebKitGTKService(driver_path)
        return webdriver.WebKitGTK(service=gtk_service, options=gtk_options)
    else:
        wpe_options: Final = webdriver.WPEWebKitOptions()
        for arg in instance_args:
            wpe_options.add_argument(arg)
        wpe_service: Final = webdriver.WPEWebKitService(driver_path)
        return webdriver.WPEWebKit(service=wpe_service, options=wpe_options)
        

def path_chooser(
    create_db: bool, # Создавать ли базу данных
    db_path: Path | None = None,  # локация для базы данных
    downloads: Path | None = None,  # папка для загрузок
) -> tuple[InstructionDatabase, Path]:
    """
    Готовит базу данных инструкций и каталог для скачивания файлов.

    При необходимости создаёт каталог для БД и сам файл базы
    (через :meth:`InstructionDatabase.bootstrap`), а также каталог
    для загрузок, если он ещё не существует.

    Parameters
    ----------
    create_db : bool
        Если ``True``, база данных создаётся заново (схема + начальные
        данные). Если ``False``, открывается существующая база;
        при её отсутствии будет выброшено исключение.
    db_path : pathlib.Path or None, optional
        Путь к файлу базы данных или каталогу, в котором он должен
        находиться. Если ``None``, используется
        ``<корень проекта>/sql/instr_db.sqlite3``. Если передан каталог
        или путь без суффикса, к нему добавляется имя
        ``instr_db.sqlite3``. По умолчанию — ``None``.
    downloads : pathlib.Path or None, optional
        Каталог для сохранения скачанных файлов. Если ``None``,
        используется ``~/Downloads``. Каталог создаётся при отсутствии.
        По умолчанию — ``None``.

    Returns
    -------
    db : InstructionDatabase
        Экземпляр базы данных, подключённый к выбранному файлу.
    downloads : pathlib.Path
        Путь к каталогу загрузок.

    Raises
    ------
    ValueError
        Если ``create_db=False``, а файл базы данных по указанному пути
        не существует.

    Notes
    -----
    Если ``db_path`` или ``downloads`` не заданы, в лог пишется
    предупреждение с использованным значением по умолчанию.
    """
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
    """
    Обходит все страницы в базе и обрабатывает их по инструкциям.

    Для каждой страницы из :meth:`InstructionDatabase.get_pages`
    вызывает :func:`process_page`. По завершении (в том числе при
    исключении) закрывает веб-драйвер через ``driver.quit()``.

    Parameters
    ----------
    db : InstructionDatabase
        База данных с инструкциями и списком целевых страниц.
    download_dir : pathlib.Path
        Каталог, в который сохраняются скачанные файлы и HTML.
    driver : WebDriver
        Активный экземпляр веб-драйвера. Будет закрыт по завершении.
    chunksz : int, optional
        Размер буфера для чтения файлов по частям, в байтах.
        По умолчанию — ``33554432`` (32 МиБ).

    Returns
    -------
    None
        Функция ничего не возвращает; результаты — файлы на диске
        и записи в логе.

    Notes
    -----
    Драйвер закрывается в блоке ``finally``, поэтому даже при ошибке
    на одной из страниц ресурсы будут освобождены.
    """
    try:
        for page in db.get_pages():
            logger.info(f"Скачивание: {page.link}")
            process_page(driver, db, page, download_dir, chunksz)
    finally:
        driver.quit()
    logger.info(f"Все скаченные файлы находятся в папке {download_dir}.")

def compare_attrs(attrs: InstAttribute, elem: WebElement) -> bool:
    """
    Проверяет, что HTML-элемент соответствует заданным атрибутам.

    Атрибут ``class`` сравнивается как подмножество: все классы
    из ``attrs["class"]`` должны присутствовать у элемента. Остальные
    атрибуты сравниваются на точное совпадение значения. Атрибут
    ``tag`` игнорируется (поиск по тегу выполняется отдельно).

    Parameters
    ----------
    attrs : InstAttribute
        Ожидаемые атрибуты элемента. Может содержать ключи ``tag``,
        ``id``, ``class``, ``text``, ``data-editor``; отсутствующие
        ключи не проверяются.
    elem : selenium.webdriver.remote.webelement.WebElement
        HTML-элемент, полученный от веб-драйвера.

    Returns
    -------
    bool
        ``True``, если элемент удовлетворяет всем заданным атрибутам,
        иначе ``False``.
    """
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
    """
    Выполняет инструкции по скрапингу для одной страницы.

    Поддерживаемые действия:

    - ``Mnemonic.DOWNLOAD_TARGET`` — находит элементы по тегу и атрибутам,
      скачивает связанные файлы в ``download_dir`` (имя берётся из URL,
      при пустом имени формируется ``document_<idx>_<i>.pdf``);
    - ``Mnemonic.EXTRACT_SUBTREE`` — находит подходящие HTML-элементы
      (с повторной попыткой при ``StaleElementReferenceException``)
      и сохраняет их ``outerHTML`` в файл
      ``page_<idx> <последний_сегмент_URL>.html``.

    Если для страницы нет инструкций, пишется предупреждение в лог
    и страница фактически пропускается.

    Parameters
    ----------
    driver : WebDriver
        Активный веб-драйвер, уже нацеленный на нужный браузер.
    db : InstructionDatabase
        База данных, из которой берутся шаги инструкции.
    page : TargetPage
        Описание обрабатываемой страницы (``idx``, ``link``, ``kind``,
        ``topic``).
    download_dir : pathlib.Path
        Каталог для сохранения файлов и HTML.
    chunksz : int
        Размер буфера чтения файла при скачивании, в байтах.

    Returns
    -------
    None
        Функция ничего не возвращает; результат — файлы на диске
        и записи в логе.

    Notes
    -----
    Скачивание файлов выполняется потоково через ``urlopen`` с
    ``memoryview``-буфером, чтобы не держать в памяти весь файл.
    Таймаут сетевого запроса — 30 секунд, SSL-контекст использует
    сертификаты из ``certifi``.

    При отсутствии подходящих элементов для ``DOWNLOAD_TARGET`` или
    ``EXTRACT_SUBTREE`` в лог пишется сообщение об ошибке; выполнение
    продолжается со следующего шага.
    """
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


