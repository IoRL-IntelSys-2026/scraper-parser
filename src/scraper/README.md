# The `rudn_scraper` module

Downloads documents and HTML content from web pages using
scraping instructions stored in the instructions database.
## The `instr_db` submodule
Provides functionality for retrieving webpages and downloading documents
from the RUDN website using Selenium and the instructions stored in the database.
* `path_chooser` connects to the instructions database
  and creates the downloads directory. Returns the database instance
  and the download directory path.
* `the_downloader` iterates over pages in the database, skips pages
  without scraping instructions and processes the remaining pages.
* `process_page` executes scraping instructions for a given page.
  It supports downloading linked files and extracting HTML elements
  based on their tags and attributes. Logs errors when the requested
  elements cannot be found.

When executed through cli.py, the module initializes the database and download
directory, configures Chrome for downloading files and starts the
downloader.
# Модуль `rudn_scraper`

Скачивает документы и HTML-содержимое с веб-страниц, используя инструкции по скрапингу, хранящиеся в базе данных инструкций.

## Подмодуль `instr_db`

Предоставляет функциональность для получения веб-страниц и скачивания документов с сайта РУДН с помощью Selenium и инструкций, хранящихся в базе данных.

* `path_chooser` — подключается к базе данных инструкций и создаёт каталог для скачивания. Возвращает экземпляр базы данных и путь к каталогу загрузок.
* `the_downloader` — перебирает страницы в базе данных, пропускает страницы без инструкций по скрапингу и обрабатывает оставшиеся.
* `process_page` — выполняет инструкции по скрапингу для заданной страницы. Поддерживает скачивание связанных файлов и извлечение HTML-элементов по их тегам и атрибутам. При невозможности найти запрошенные элементы записывает ошибки в лог.

При запуске через `cli.py` модуль инициализирует базу данных и каталог загрузок, настраивает Chrome для скачивания файлов и запускает загрузчик.