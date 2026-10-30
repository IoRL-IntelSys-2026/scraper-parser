# The `database` module
Contains an object-oriented interface to query the
web scraper instructions database.

## The `instr_db` submodule
Provides a class to initialize, connect to and query
the instructions database.
 - `bootstrap` accepts a path to a directory, creates
 a new copy of the database there and returns an `InstructionDatabase`
 instance connected to it.
 - `get_pages` returns the identifiers, links and file types of
 all pages in the database as a list of `NamedTuple`s.
 - `get_doc_instrs` takes a document identifier and returns
 scraping intructions for it. Returns an empty list if no instructions
 are available.
