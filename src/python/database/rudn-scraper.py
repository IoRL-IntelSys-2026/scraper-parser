# https://i.pinimg.com/474x/f7/20/20/f72020244e330f7415319513208af87d.jpg

import certifi
import logging
import ssl

from .instr_db import InstructionDatabase, Mnemonic, TargetPage
from pathlib import Path
# да я использую edge, я злой
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

# библиотека urllib очень мощная для работы со ссылками
from urllib.parse import urljoin, unquote, urlparse
from urllib.request import urlopen

logger = logging.getLogger(__name__)

# оформлено в виде функции, по просьбе asdftowel
def path_chooser(
    db_path: Path | None = None, # локация для датабазы
    downloads: Path | None = None # локация для загрузок
) -> tuple[InstructionDatabase, Path]:

    # стандартная локация для датабазы (в папке sql)
    if db_path is None:
        db_path = Path(__file__).parents[2] / "sql/instr_db.sqlite3"
        logger.warning(f"Путь до БД не указан, используется {db_path}")

    # PathInfo кэширует информацию о пути, может уменьшить кол-во
    # stat()ов
    # дефолтное название для файла
    if db_path.info.is_dir() or not db_path.suffix:
        db_path = db_path / "instr_db.sqlite3"

    # создает датабазу либо открывает существующую
    if not db_path.info.is_file():
        db = InstructionDatabase.bootstrap(str(db_path))
    else:
        db = InstructionDatabase(db_path)

    # стандартное место для папки загрузок
    if downloads is None:
        downloads = Path(__file__).parent / "downloads"
        logger.warning(f"Папка для загрузок не указана, используется {downloads}")

    downloads.mkdir(exist_ok=True)

    return db, downloads

# я ОЧЕНЬ хотел назвать функцию "the_downloaderrrrrr" но в рамках чистого кода делать так не буду
# оформлено в виде функции, по просьбе asdftowel
def the_downloader(
    db: InstructionDatabase,
    download_dir: Path,
    options: Options
) -> None:
    driver = None

    try:
        driver = webdriver.Edge(options=options)

        for page in db.get_pages():
            instructions = db.get_doc_instrs(page["idx"])

            if not instructions:
                logger.warn(f"Нет инструкций - совершён пропуск: {page['link']}")
                continue

            logger.info(f"Скачивание: {page['link']}")
            process_page(driver, db, page, download_dir)

    finally:
        if driver is not None:
            driver.quit()
    logger.info(f"Все скаченные файлы находятся в папке {download_dir}.")


def process_page(
    driver: WebDriver,
    db: InstructionDatabase,
    page: TargetPage,
    download_dir: Path
) -> None:
    driver.get(page["link"])

    # инструкции для сайтов
    instructions = db.get_doc_instrs(page["idx"])

    for instruction in instructions:
        attrs = instruction["attrs"]
        action = instruction["inst"]

        # уточнение если инструкция - это скачивание
        if action is Mnemonic.DOWNLOAD_TARGET:
            # найти указанный элемент
            tag = attrs.get("tag", "a")
            elements = driver.find_elements(By.TAG_NAME, tag)

            for name, value in attrs.items():
                if name != "tag":
                    elements = [
                        element for element in elements
                        if element.get_attribute(name) == value
                    ]

            if not elements:
                logger.error("Ссылка для скачивания не найдена!")
                continue

            # получить ссылку сайта
            url = urljoin(
                driver.current_url,
                elements[0].get_attribute("href")
            )

            filename = unquote(Path(url.split("?")[0]).name) # unquote делает названия файлов нормальными
            if not filename:
                filename = f"document_{page['idx']}.pdf"
            filepath = download_dir / filename

            # таймер для ожидания - 30 секунд, но можно изменить
            with urlopen(
                url,
                timeout=30,
                context=ssl.create_default_context(cafile=certifi.where())
            ) as sock, filepath.open("wb") as f:
                sock.readinto(f)

            logger.info(f"Скачано: {filename}")

        # код для HTML
        elif action is Mnemonic.EXTRACT_SUBTREE:
            tag = attrs.get("tag", "*")
            # бог знает почему, но у меня вылезла ошибка при импорте html на wifi рудн, поэтому делаем пока так
            from selenium.common.exceptions import StaleElementReferenceException
            for attempt in range(2):
                try:
                    elements = driver.find_elements(By.TAG_NAME, tag)
                    for name in ("id", "class"):
                        if name in attrs:
                            elements = [
                                element for element in elements
                                if (
                                    attrs[name] == frozenset((element.get_attribute(name) or "").split())
                                    if name == "class"
                                    else element.get_attribute(name) == attrs[name]
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
                last_word = urlparse(page["link"]).path.rstrip("/").split("/")[-1]
                filename = f"page_{page['idx']} {unquote(last_word)}.html"
                filepath = download_dir / filename
                filepath.write_text(elements[0].get_attribute("outerHTML") or "", encoding="utf-8")
                logger.info(f"HTML скачан: {filename}")
            else:
                logger.error(f"Не найден подходящий HTML элемент в {page['link']}")

if __name__ == "__main__":
    db, downloads = path_chooser()
    options = Options()
    # это заставляет edge не быть проблемным и нормально скачивать файлы
    options.add_experimental_option("prefs", {
        "download.default_directory": str(downloads),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })
    the_downloader(db, downloads, options)
