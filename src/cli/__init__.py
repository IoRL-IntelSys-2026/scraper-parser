"""Command-line interface for the RUDN scraper."""

__all__ = ["main", "parse_args"]

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


def _check_positive(arg: str) -> int:
    """Проверяет, является ли аргумент положительным числом.
    
    Parameters
    ----------
    arg : str
        Аргумент, который нужно проверить.
    
    Raises
    ------
    argparse.ArgumentTypeError
        Если аргумент — не число, или он меньше 1.
    
    Returns
    -------
    int
        Число, полученное из аргумента."""
    try:
        res = int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError(f'"{arg}" is not an integer.')
    if res < 1:
        raise argparse.ArgumentTypeError(f"{res} is not a positive integer.")
    return res


def parse_args(
    args: list[str] | None, exit_on_error: bool
) -> tuple[argparse.Namespace, list[str], argparse.ArgumentParser]:
    """Разбирает аргументы командной строки.

    Parameters
    ----------
    args : list of str, optional
        Список аргументов для разбора. Если не указан, используются
        аргументы, с которыми запущена программа.

    Returns
    -------
    argparse.Namespace
        Объект с разобранными параметрами: путь к базе данных, папка
        загрузок, уровень журналирования, размер буфера, выбранный
        браузер, путь к драйверу и аргументы для браузера.
    """
    parser: Final = argparse.ArgumentParser(
        description=(
            "Загрузка документов и HTML-страниц по инструкциям из базы данных."
            " Все незнакомые (которых нет в списке ниже) аргументы передаются"
            " драйверу браузера."
        ),
        exit_on_error=exit_on_error,
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
        type=_check_positive,
        default=33554432,  # 32 мебибайта
        help="Размер буфера для загрузки файлов (в байтах).",
    )
    parser.add_argument(
        "--browser",
        choices=(
            "chrome",
            "edge",
            "firefox",
            "ie",
            "safari",
            "webkitgtk",
            "wpewebkit",
        ),
        type=BrowserType,
        required=True,
        help="Браузер, которым нужно управлять.",
    )
    parser.add_argument(
        "--driver-path",
        type=Path,
        nargs="?",
        help="Путь до драйвера для выбранного браузера.",
    )
    return parser.parse_known_args(args) + (parser,)


def main() -> None:
    """Запускает загрузчик с параметрами командной строки.

    Разбирает аргументы, настраивает журналирование, выбирает
    базу данных и папку загрузок, запускает браузер и скачивает
    документы по инструкциям из базы. После этого очищает
    скачанные HTML-файлы с помощью `clean_html_directory`.
    """
    args, browser_args, _ = parse_args(None, True)

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
            args.browser, browser_args, args.driver_path, str(downloads)
        ),
        args.buffer_size,
    )

    clean_html_directory(downloads)
