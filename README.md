# Internal website scraping and parsing tool

> [!IMPORTANT]
> It is a work in progress. Don't rely on any
> part having a stable interface.

This command line tool collects webpages that
have information that might be useful to
students and converts them into an easy to
manipulate format.

Right now it's split into the following parts:
 - A database that holds instructions in a
   machine-readable format on how to parse
   every page;
 - A web scraper based on Selenium that
   interprets the aforementioned instructions;
 - A HTML cleaner that strips out unnecessary
   information from the fetched pages.

What still needs to be done:
 - A command line interface to control all of
   these parts;
 - A database for monitoring scraping results;
 - A pass to convert fetched documents into a
   different format.

## How to run tests
This project uses Pytest for unit testing.
Every source code file has a matching test case
named as the original file but with the "test_"
prefix. So one can select all test files like
this:
```shell
python3 -m pytest src/**/test_*.py
```
