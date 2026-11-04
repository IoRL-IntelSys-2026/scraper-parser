"""Module for interacting with the web scraper."""
"""
Модуль для взаимодействия с веб-скрапером.

Реэкспортирует подмодуль :mod:`scraper.rudn_scraper`, предоставляя
его как часть публичного API пакета (см. ``__all__``).
"""

__all__ = ["rudn_scraper"]
from scraper import rudn_scraper
