"""Tests for the command line entry point."""

from argparse import Action, ArgumentError
from pathlib import Path

import pytest

from cli import parse_args
from scraper.rudn_scraper import BrowserType


def test_good_args() -> None:
    """Тест: проверяет форму обработанных аргументов.

    Вызывает обработчик параметров с возможными аргументами
    и проверяет, что он возвращает их в виде, ожидаемом
    остальными функциями.

    Raises
    ------
    AssertionError
        Если аргументы не соответствуют ожидаемой форме.

    Returns
    -------
    None
        Это тест, он не должен выполняться напрямую. Вместо этого
        ``pytest`` проверяет правильность условий ``assert`` при
        запуске.
    """
    args, unknown, _ = parse_args(
        [
            "--db-path=./nonexistent/path",
            "--create-db",
            "--loglevel=WARNING",
            "--browser=chrome",
            "--no-create-db",
            "--headless=new",
        ],
        False,
    )
    assert unknown == ["--headless=new"]
    assert (
        args.db_path == Path("./nonexistent/path")
        and args.create_db is False
        and args.downloads == Path.home() / "Downloads"
        and args.loglevel == "WARNING"
        and args.buffer_size == 33554432
        and args.browser is BrowserType.CHROME
        and args.driver_path is None
    )


def test_exhaustive_browser_choice() -> None:
    """Тест: проверяет, что все доступные браузеры указаны в списке.

    Raises
    ------
    AssertionError
        Если в списке вариантов аргумента ``--browser`` указаны не
        все браузеры.

    Returns
    -------
    None
        Это тест, он не должен выполняться напрямую. Вместо этого
        ``pytest`` проверяет правильность условия ``assert`` при
        запуске.
    """
    _, _, parser = parse_args(["--no-create-db", "--browser=edge"], False)
    browser_choices = next(
        (
            action.choices
            for action in parser._actions
            if isinstance(action, Action)
            and action.option_strings[0] == "--browser"
            and isinstance(action.choices, tuple)
        ),
        (),
    )
    assert all(browser.value in browser_choices for browser in BrowserType)


def test_bad_args() -> None:
    """
    Тест: проверяет, что обработчик аргументов не принимает
    неправильные значения аргументов.

    Returns
    -------
    None
        Это тест, он не должен выполняться напрямую. Вместо этого
        ``pytest`` проверяет правильность условий ``assert`` при
        запуске.
    """
    with pytest.raises(ArgumentError):
        parse_args([], False)
    with pytest.raises(ArgumentError):
        parse_args(["--browser=nonexistent"], False)
    with pytest.raises(ArgumentError):
        parse_args(["--buffer-size=0.0045832", "--browser=ie"], False)
