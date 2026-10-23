# The `cleaner` module
Provides a function for removing noise from downloaded
HTML pages. The only (public) function is `clean_html_directory`.
It accepts a path to the directory with the HTML files,
removes unnecessary elements from each document and saves
cleaned versions as `cleaned_{name}.html`.
