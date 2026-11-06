# The `cli` module
This module provides an entry point to use this library's modules as a
script. It accepts configuration parameters and does all of the
processing steps. The downloaded and cleaned documents are put
into the user's Download folder unless changed by the `--downloads`
option.

There are two ways to call it:
```shell
# Replace "python3" with the Python executable's name on your system
python3 -m scraper_parser.cli
# or
scraper-parser
```

You can check which parameters are available by calling the command
line with the `--help` option.