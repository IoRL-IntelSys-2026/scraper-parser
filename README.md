# Internal website scraping and parsing tool

> [!IMPORTANT]
> This project is a work in progress. Its interface and internal structure may change without notice.
>
> Make sure to mark `src/python` as **Sources Root** in your IDE (e.g. PyCharm).

This command-line tool collects webpages containing information that may be useful to students and converts them into an easy-to-process format.

## Project structure

The project is divided into the following components:

- **Database** (`src/python/database`) — stores machine-readable instructions describing how individual webpages should be parsed.
- **Web scraper** (`src/python/scraper`) — uses Selenium to retrieve webpages and interpret the corresponding parsing instructions.
- **HTML cleaner** (`src/python/cleaner`) — removes unnecessary information from fetched webpages.
- **Command-line interface** (`src/python/cli.py`) — serves as the main entry point to run the program.
- **SQL scripts** (`src/sql`) — contain the database and initial data.

## Running the tool

Run `src/python/cli.py` to start the application.

Make sure the required Python dependencies are installed and that `src/python` is configured as a Sources Root.

## How to run tests
This project uses Pytest for unit testing.
Every source code file has a matching test case
named as the original file but with the "test_"
prefix. So one can select all test files like
this:
```shell
python3 -m pytest
```