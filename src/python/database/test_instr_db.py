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
