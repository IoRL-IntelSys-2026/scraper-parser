# The `cleaner` module
Provides functionality for removing unnecessary elements and structural noise from downloaded HTML pages, making them easier to process.

## The `parser` submodule
Provides a function for batch-processing HTML files.
- `clean_html_directory` accepts a path to a directory (defaults to the current working directory) and processes all `.html` files located directly inside it.
- Removes HTML comments and unnecessary elements: `script`, `style`, `link`, `header` and `footer` tags.
- Unwraps redundant `div` wrappers that contain only a single child `div`.
- Removes excessive empty-line spacing from the resulting HTML.
- Saves cleaned copies alongside the original files, prefixing their names with `cleaned_`. Files that already have this prefix are skipped.
The function uses UTF-8 encoding for reading and writing files and logs its progress through Python's `logging` module.