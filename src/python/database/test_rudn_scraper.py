
"""Functions for the RUDN scraper."""

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# доп проверка для универсальности кода (привет pycharm)
try:
    from .rudn_scraper import path_chooser, process_page, Mnemonic
except ImportError as error:
    if error.name != __package__:
        raise
    from rudn_scraper import path_chooser, process_page, Mnemonic


def test_download_one_page(tmp_path: Path) -> None:
    db, _ = path_chooser(downloads=tmp_path)

    # находит страницу с инструкциями
    page = next(
        (
            page
            for page in db.get_pages()
            if any(
                instruction.inst is Mnemonic.DOWNLOAD_TARGET
                for instruction in db.get_doc_instrs(page.idx)
            )
        ),
        None,
    )

    assert page is not None, "Не найдена страница с инструкцией для скачивания."

    driver = webdriver.Chrome(options=Options())

    try:
        process_page(driver, db, page, tmp_path)
    finally:
        driver.quit()

    # проверка скачивания файла
    files = list(tmp_path.iterdir())

    assert files, f"Файлы не были скачены из {page.link}"

    assert any(
        file.is_file() and file.stat().st_size > 0
        for file in files
    ), "Скаченные файлы пустые."

    print(f"Successfully tested: {page.link}")
