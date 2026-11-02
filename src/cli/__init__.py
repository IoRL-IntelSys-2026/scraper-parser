"""Command-line interface for the RUDN scraper."""

__all__ = ["main"]

import argparse
import logging
from pathlib import Path
from typing import Final

from selenium.webdriver.chrome.options import Options

import scraper.rudn_scraper
from cleaner.parser import clean_html_directory


def parse_args() -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser: Final = argparse.ArgumentParser(
        description="Загрузка документов и HTML-страниц по инструкциям из базы данных."
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.cwd(),
        help="Путь к файлу базы данных или папке для него.",
    )
    parser.add_argument(
        "--create-db",
        action=argparse.BooleanOptionalAction,
        help="Можно ли создать базу данных, если по указанному пути её нет."
    )
    parser.add_argument(
        "--downloads",
        type=Path,
        default=Path.home() / "Downloads",
        help="Папка для загруженных документов.",
    )
    parser.add_argument(
        "--loglevel",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="INFO",
        help="Минимальный уровень журналирования (по умолчанию: INFO).",
    )
    return parser.parse_args()


def main() -> None:
    """Запускает загрузчик с параметрами командной строки."""
    args: Final = parse_args()

    logging.basicConfig(
        level=args.loglevel,
        format=(
            "%(asctime)s - %(module)s.%(funcName)s:%(lineno)d: "
            "%(levelname)s - %(message)s"
        ),
    )

    db, downloads = scraper.rudn_scraper.path_chooser(
        db_path=args.db_path,
        downloads=args.downloads,
        create_db=args.create_db,
    )

    options: Final = Options()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(downloads.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
        },
    )

    scraper.rudn_scraper.the_downloader(db, downloads, options)

    clean_html_directory(downloads)
