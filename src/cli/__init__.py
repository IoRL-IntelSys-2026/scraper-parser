"""Command-line interface for the RUDN scraper."""

__all__ = ["main"]

import argparse
import logging
from pathlib import Path
from typing import Final

from cleaner.parser import clean_html_directory
from scraper.rudn_scraper import (
    BrowserType,
    create_browser_instance,
    path_chooser,
    the_downloader,
)


# Аргумент позволяет программно добавлять аргументы для тестирования
def parse_args(args: list[str] | None = None) -> argparse.Namespace:
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
        help="Можно ли создать базу данных, если по указанному пути её нет.",
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
        help="Минимальный уровень журналирования.",
    )
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=33554432,  # 32 мебибайта
        help="Размер буфера для загрузки файлов (в байтах).",
    )
    parser.add_argument(
        "--browser", type=BrowserType, help="Браузер, которым нужно управлять."
    )
    parser.add_argument(
        "--driver-path",
        type=Path,
        nargs="?",
        help="Путь до драйвера для выбранного браузера.",
    )
    parser.add_argument(
        "browser-opts",
        nargs="*",
        help="Аргументы, передаваемые напрямую браузеру.",
    )
    return parser.parse_args(args)


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

    db, downloads = path_chooser(
        db_path=args.db_path,
        downloads=args.downloads,
        create_db=args.create_db,
    )

    the_downloader(
        db,
        downloads,
        create_browser_instance(
            args.browser, args.browser_opts, args.driver_path, str(downloads)
        ),
        args.buffer_size,
    )

    clean_html_directory(downloads)
