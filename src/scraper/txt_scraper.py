"""Download RUDN pages or documents from links.txt / files.txt.

Place this script next to links.txt and files.txt, then run:
    python txt_scraper.py
"""

from __future__ import annotations

import logging
import re
import ssl
from pathlib import Path
from typing import Final
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

import certifi
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException

BASE_DIR: Final = Path(__file__).resolve().parent
OUTPUT_DIR: Final = BASE_DIR / "txt_scraper_output"
CHUNK_SIZE: Final = 1024 * 1024  # 1 MB
MAX_FILE_SIZE: Final = 20 * 1024 * 1024  # 20 MB
TIMEOUT: Final = 45

logger = logging.getLogger("txt_scraper")


def configure_logging() -> None:
    """Write progress to the console and txt_scraper.log."""
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = logging.FileHandler(
        BASE_DIR / "txt_scraper.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(console)
    logger.addHandler(file_handler)


def read_urls(filename: str) -> list[str]:
    """Read non-empty URLs from a UTF-8 text file."""
    path = BASE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Не найден файл со ссылками: {path}")

    return [
        line.strip()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def make_filename(url: str, index: int, extension: str | None = None) -> str:
    """Create a safe, unique filename based on the URL."""
    parsed = urlparse(url)
    name = unquote(Path(parsed.path).name).strip()
    name = re.sub(r'[<>:"/\\\\|?*\\x00-\\x1f]', "_", name)

    if not name or name in {".", ".."}:
        name = "index"

    if extension and not Path(name).suffix:
        name += extension

    # Prefixing with the list index prevents collisions between equal basenames from different URLs.
    return f"{index:05d}_{name}"


def write_failed_urls(failed_urls: list[str], filename: str) -> None:
    """Export URLs that could not be processed."""
    path = BASE_DIR / filename
    path.write_text(
        "".join(f"{url}\n" for url in failed_urls),
        encoding="utf-8",
    )
    logger.info("Список ошибок сохранён: %s (%d ссылок)", path, len(failed_urls))


def download_file(
    url: str,
    destination: Path,
    context: ssl.SSLContext,
) -> None:
    """Download one document using a streamed HTTP request."""
    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; RUDN-Txt-Scraper/1.0)"},
    )

    with urlopen(request, timeout=TIMEOUT, context=context) as response:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_FILE_SIZE:
            raise ValueError(
                f"Файл превышает ограничение 20 МБ: {content_length} байт"
            )

        total_size = 0
        try:
            with destination.open("wb") as output:
                while chunk := response.read(CHUNK_SIZE):
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE:
                        raise ValueError("Файл превышает ограничение 20 МБ")
                    output.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise


def scrape_files(urls: list[str]) -> None:
    """Download documents listed in files.txt."""
    destination_dir = OUTPUT_DIR / "files"
    destination_dir.mkdir(parents=True, exist_ok=True)

    context = ssl.create_default_context(cafile=certifi.where())
    failed_urls: list[str] = []

    for index, url in enumerate(urls, start=1):
        destination = destination_dir / make_filename(url, index)
        logger.info("[%d/%d] Скачивание: %s", index, len(urls), url)

        try:
            download_file(url, destination, context)
            logger.info("Сохранено: %s", destination.name)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            logger.error("Не удалось скачать %s: %s", url, error)
            failed_urls.append(url)
        except Exception:
            logger.exception("Непредвиденная ошибка при скачивании %s", url)
            failed_urls.append(url)

    write_failed_urls(failed_urls, "failed_files.txt")


def create_browser(downloads: str = ".") -> webdriver.Chrome:
    """Create a headless Chrome instance for HTML page downloads."""
    prefs: Final = {
        "download.default_directory": downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }

    options: Final = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(TIMEOUT)
    return driver


def scrape_links(urls: list[str]) -> None:
    """Open each URL in Chrome and save the resulting HTML page."""
    destination_dir = OUTPUT_DIR / "html"
    destination_dir.mkdir(parents=True, exist_ok=True)

    failed_urls: list[str] = []
    driver: webdriver.Chrome | None = None

    try:
        driver = create_browser(str(destination_dir))

        for index, url in enumerate(urls, start=1):
            destination = destination_dir / make_filename(
                url, index, extension=".html"
            )
            # Keep HTML output extension even if the URL itself ends in .html.
            if destination.suffix.lower() != ".html":
                destination = destination.with_suffix(".html")

            logger.info("[%d/%d] Открытие: %s", index, len(urls), url)

            try:
                driver.get(url)
                destination.write_text(driver.page_source, encoding="utf-8")
                logger.info("HTML сохранён: %s", destination.name)
            except (TimeoutException, WebDriverException, OSError) as error:
                logger.error("Не удалось загрузить %s: %s", url, error)
                destination.unlink(missing_ok=True)
                failed_urls.append(url)
            except Exception:
                logger.exception("Непредвиденная ошибка при обработке %s", url)
                destination.unlink(missing_ok=True)
                failed_urls.append(url)
    finally:
        if driver is not None:
            try:
                driver.quit()
            except WebDriverException:
                logger.exception("Не удалось корректно закрыть браузер.")

    write_failed_urls(failed_urls, "failed_links.txt")


def main() -> None:
    configure_logging()

    print(
        "\nВыбрать необходимое скачивание: \n"
        "\n1 — links.txt — 11 017 URL страниц."
        "\n    Ядро ассистента: карточки и страницы образовательных программ"
        "\n    (/sveden/education/programs, /education/*), направления"
        "\n    бакалавриата/магистратуры/ординатуры/интернатуры (www + admission),"
        "\n    ППС по программам и приёмной комиссии (/sveden/employees/pps,"
        "\n    admission/staff), студенческая жизнь включая общежития (/life/*),"
        "\n    структура вуза и документы (/about/*), handbook/teachers-handbook"
        "\n    (рус. + англ.), образовательные разделы eng/international."
        "\n"
        "\n2 — files.txt — 1 364 файла ≤20 МБ."
        "\n    Проверены на уникальность по sha256, только актуальный год."
        "\n    Учебные планы (/pk/plans/2026), экзаменационные программы"
        "\n    (/pk/examprogs/2026), правила приёма (/pk/files/Rules_2023, faq),"
        "\n    расписание, приказы о стоимости и апелляциях."
        "\n"
    )

    choice = input("Введите 1 или 2: ").strip()

    if choice == "1":
        filename = "links.txt"
        scraper = scrape_links
    elif choice == "2":
        filename = "files.txt"
        scraper = scrape_files
    else:
        print("Неверный выбор. Запустите программу ещё раз и введите 1 или 2.")
        return

    try:
        urls = read_urls(filename)
    except (OSError, UnicodeError) as error:
        logger.error("Не удалось прочитать список ссылок: %s", error)
        return

    if not urls:
        logger.warning("В файле %s нет ссылок.", filename)
        return

    logger.info("Загружено ссылок: %d", len(urls))
    scraper(urls)
    logger.info("Обработка списка %s завершена.", filename)


if __name__ == "__main__":
    main()
