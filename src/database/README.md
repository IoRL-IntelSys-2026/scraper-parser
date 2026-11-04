# The `database` module
Contains an object-oriented interface to query the
web scraper instructions database.

## The `instr_db` submodule
Provides a class to initialize, connect to and query
the instructions database.
 - `bootstrap` accepts a path to a directory, creates
 a new copy of the database there and returns an `InstructionDatabase`
 instance connected to it.
 - `get_pages` returns the identifiers, links, file types and topics of
 all pages in the database as a list of `NamedTuple`s.
 - `get_doc_instrs` takes a document identifier and returns
 scraping intructions for it. Returns an empty list if no instructions
 are available.
# Модуль `database`

Содержит объектно-ориентированный интерфейс для запросов к базе данных инструкций веб-скрапера.

## Подмодуль `instr_db`

Предоставляет класс для инициализации, подключения к базе данных инструкций и выполнения запросов к ней.

 - `bootstrap` — принимает путь к каталогу, создаёт там новую копию базы данных и возвращает экземпляр `InstructionDatabase`, подключённый к ней.
 - `get_pages` — возвращает идентификаторы, ссылки, типы файлов и темы всех страниц в базе данных в виде списка `NamedTuple`.
 - `get_doc_instrs` — принимает идентификатор документа и возвращает инструкции по скрапингу для него. Если инструкции отсутствуют, возвращает пустой список.

