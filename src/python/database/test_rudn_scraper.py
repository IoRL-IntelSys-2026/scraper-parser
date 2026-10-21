
"""Functions for the RUDN scraper."""

import tempfile
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:
    from .rudn_scraper import path_chooser, process_page, Mnemonic
except ImportError as error:
    if error.name != __package__:
        raise
    from rudn_scraper import path_chooser, process_page, Mnemonic


def test_download_one_page() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
        db, _ = path_chooser(downloads=tmp_path)

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

        assert page is not None, (
            "Не найдена страница с инструкцией для скачивания."
        )

        driver = webdriver.Chrome(options=Options())

        try:
            process_page(driver, db, page, tmp_path)
        finally:
            driver.quit()

        files = list(tmp_path.iterdir())

        assert files, f"Файлы не были скачаны из {page.link}"

        assert any(
            file.is_file() and file.stat().st_size > 0
            for file in files
        ), "Скачанные файлы пустые."

        print(f"Успешный тест: {page.link}")