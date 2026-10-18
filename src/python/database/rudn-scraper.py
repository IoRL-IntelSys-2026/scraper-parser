# https://i.pinimg.com/474x/f7/20/20/f72020244e330f7415319513208af87d.jpg

import os
import requests

# да я использую edge, я злой
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

from pathlib import Path
# библиотека urllib очень мощная для работы со ссылками
from urllib.parse import urljoin, unquote, urlparse

from instr_db import InstructionDatabase
from instr_db import Mnemonic

# оформлено в виде функции, по просьбе asdftowel
def path_chooser(
    db_path: Path | None = None, # локация для датабазы
    downloads: Path | None = None # локация для загрузок
) -> tuple[InstructionDatabase, Path]:

    # стандартная локация для датабазы (в папке sql)
    if db_path is None:
        db_path = Path(__file__).resolve().parents[2] / "instr_db.sqlite3"

    # дефолтное название для файла
    if db_path.is_dir() or not db_path.suffix:
        db_path = db_path / "instr_db.sqlite3"

    db_path.parent.mkdir(parents=True, exist_ok=True)

    # создает датабазу либо открывает существующую
    if not db_path.exists():
        db = InstructionDatabase.bootstrap(str(db_path))
    else:
        db = InstructionDatabase(str(db_path))

    # стандартное место для папки загрузок
    if downloads is None:
        downloads = Path(__file__).resolve().parent / "downloads"

    downloads.mkdir(parents=True, exist_ok=True)

    return db, downloads

# я ОЧЕНЬ хотел назвать функцию "the_downloaderrrrrr" но в рамках чистого кода делать так не буду
# оформлено в виде функции, по просьбе asdftowel
def the_downloader(db, download_dir, options):
    driver = None

    try:
        driver = webdriver.Edge(options=options)

        for page in db.get_pages():
            instructions = db.get_doc_instrs(page["idx"])

            if not instructions:
                print(f"Нету инструкций - совершён пропуск: {page['link']}")
                continue

            print(f"\nСкачивание: {page['link']}")
            process_page(driver, db, page, download_dir)

    finally:
        if driver is not None:
            driver.quit()

db, downloads = path_chooser()
download_dir = str(downloads)

options = Options()
# это заставляет edge не быть проблемным и нормально скачивать файлы
options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
})



def process_page(driver, db, page, download_dir):
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
                print("Ссылка для скачивания не найдена!")
                continue

            # получить ссылку сайта
            url = urljoin(
                driver.current_url,
                elements[0].get_attribute("href")
            )

            # таймер для ожидания - 30 секунд, но можно изменить
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            filename = unquote(Path(url.split("?")[0]).name) # unquote делает названия файлов нормальными
            if not filename:
                filename = f"document_{page['idx']}.pdf"

            filepath = Path(download_dir) / filename
            filepath.write_bytes(response.content)

            print(f"Скачено: {filename}")

        # код для HTML
        elif action == Mnemonic.EXTRACT_SUBTREE:
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
                filepath = os.path.join(download_dir, filename)

                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(
                        elements[0].get_attribute("outerHTML")
                    )

                print(f"HTML скачен: {filename}")
            else:
                print(f"Не найден подходящий HTML элемент в {page['link']}")
if __name__ == "__main__":
    the_downloader(db, download_dir, options)

print("Все скаченные файлы находятся в папке downloads.")
