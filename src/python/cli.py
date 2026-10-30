"""Command-line interface for the RUDN scraper."""

import argparse
import logging
from pathlib import Path

# все необходимые импорты? F401 будет подавлять ruff
import cleaner.parser  # noqa: F401
import database.instr_db  # noqa: F401
import scraper.rudn_scraper


def parse_args() -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Загрузка документов и HTML-страниц по инструкциям из базы данных."
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Путь к файлу базы данных или папке для него.",
    )

    # если --create-db указан, args.create_db == True.
    # если не указан, args.create_db == False.
    parser.add_argument(
        "--downloads",
        type=Path,
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
    args = parse_args()

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
    )

    options = scraper.rudn_scraper.Options()
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


if __name__ == "__main__":
    main()
