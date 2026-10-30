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