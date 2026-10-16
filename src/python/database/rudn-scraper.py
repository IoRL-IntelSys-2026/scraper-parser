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

# этот код находит, где находится папка (это для пичарма)
BASE_DIR = Path(__file__).resolve().parents[2] # папка src
DB_PATH = BASE_DIR / "instr_db.sqlite3"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# проверка наличия уже существующей датабазы
if not DB_PATH.exists():
    db = InstructionDatabase.bootstrap(str(DB_PATH))
else:
    db = InstructionDatabase(str(DB_PATH))

# папка downloads для файлов
download_dir = str(
    Path(__file__).resolve().parent / "downloads"
)
os.makedirs(download_dir, exist_ok=True)

options = Options()
# это заставляет edge не быть проблемным и нормально скачивать фалы
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
        if action == Mnemonic.DOWNLOAD_TARGET:
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

            # Get the file URL
            url = urljoin(
                driver.current_url,
                elements[0].get_attribute("href")
            )

            # таймер для ожидания - 30 секунд, но можно изменить
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            filename = unquote(os.path.basename(url.split("?")[0])) # unquote делает названия файлов нормальными
            if not filename:
                filename = f"document_{page['idx']}.pdf"

            filepath = os.path.join(download_dir, filename)

            with open(filepath, "wb") as file:
                file.write(response.content)

            print(f"Скачено: {filename}")

        # код для HTML
        elif action == Mnemonic.EXTRACT_SUBTREE:
            tag = attrs.get("tag", "*")
            elements = driver.find_elements(By.TAG_NAME, tag)

            for name in ("id", "class"):
                if name in attrs:
                    elements = [
                        element for element in elements
                        if (
                            attrs[name] in
                            (element.get_attribute(name) or "").split()
                            if name == "class"
                            else element.get_attribute(name) == attrs[name]
                        )
                    ]

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
# фейлсейф чтобы программа работала при ошибке
finally:
    if driver is not None:
        driver.quit()

    db._con.close()

print("Все скаченные файлы находятся в папке downloads.")