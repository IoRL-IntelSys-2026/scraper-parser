# The SQL sources folder
This folder currently contains the schema and data
for the web scraper instructions database. These
files are used by the `database` module to initialize
the database when the user doesn't provide a path
to an existing database.
 - `instr_schema.sql` contains the database schema and
   preferred parameters.
 - `instr_data.sql` contains data such as instructions,
   links to target pages and descriptions of HTML elements
   that need to be downloaded.
