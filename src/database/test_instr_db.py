"""Test the instruction database abstraction."""

# test_instr_db - tests for the object-oriented interface
# Copyright (C) 2026  The scraper-parser contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tempfile
from typing import Final

from database.instr_db import *


def test_instrdb_methods() -> None:
    """
    Проверяет корректность работы методов :class:`InstructionDatabase`.

    Создаёт временную базу данных через :meth:`InstructionDatabase.bootstrap`,
    после чего проверяет:

    - :meth:`InstructionDatabase.get_pages` — первая страница в списке
      совпадает с ожидаемым ``TargetPage`` (``idx=1``, ссылка на раздел
      приёмной кампании, формат PDF, тема ``ADMISSIONS``);
    - :meth:`InstructionDatabase.get_doc_instrs` для документа ``4`` —
      инструкция состоит из одного шага ``DOWNLOAD_TARGET`` с атрибутами
      ``tag="a"`` и ``data-editor="pdf.link"``;
    - :meth:`InstructionDatabase.get_doc_instrs` для документа ``14`` —
      инструкция состоит из двух шагов ``EXTRACT_SUBTREE`` с тегами
      ``section`` и CSS-классами ``page-subtitle-help`` и ``main``
      соответственно.

    Returns
    -------
    None
        Функция ничего не возвращает; результат проверяется через
        ``assert``.

    Notes
    -----
    Временный файл создаётся с ``delete=False``, поэтому после завершения
    теста он не удаляется автоматически. Соединение с БД закрывается
    при уничтожении объекта ``InstructionDatabase``.

    Examples
    --------
    >>> test_instrdb_methods()  # проходит без исключений при корректной БД
    """
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        idb: Final = InstructionDatabase.bootstrap(tmp.name)
        pages: Final = idb.get_pages()
        page1: Final = TargetPage(
            idx=1,
            link="https://admission.rudn.ru/undergraduate/timing/",
            kind=DocumentKind.PDF,
            topic=Topic.ADMISSIONS,
        )
        inst4: Final = [
            Instruction(
                step=1,
                inst=Mnemonic.DOWNLOAD_TARGET,
                attrs={"tag": "a", "data-editor": "pdf.link"},
            )
        ]
        inst14: Final = [
            Instruction(
                step=1,
                inst=Mnemonic.EXTRACT_SUBTREE,
                attrs={"tag": "section", "class": frozenset({"page-subtitle-help"})},
            ),
            Instruction(
                step=2,
                inst=Mnemonic.EXTRACT_SUBTREE,
                attrs={"tag": "section", "class": frozenset({"main"})},
            ),
        ]
        assert pages[0] == page1
        assert idb.get_doc_instrs(4) == inst4
        assert idb.get_doc_instrs(14) == inst14
