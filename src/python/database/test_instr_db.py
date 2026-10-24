"""Test the instruction database abstraction."""

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
