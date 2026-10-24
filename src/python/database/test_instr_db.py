"""Test the instruction database abstraction."""

import tempfile

from database.instr_db import *


def test_instrdb_methods() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        idb = InstructionDatabase.bootstrap(tmp.name)
        pages = idb.get_pages()
        page1 = TargetPage(
            idx=1,
            link="https://admission.rudn.ru/undergraduate/timing/",
            kind=DocumentKind.PDF,
            topic=Topic.ADMISSIONS,
        )
        inst4 = [
            Instruction(
                step=1,
                inst=Mnemonic.DOWNLOAD_TARGET,
                attrs={"tag": "a", "data-editor": "pdf.link"},
            )
        ]
        inst14 = [
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
        inst_list = idb.get_doc_instrs(4)
        assert inst_list == inst4
        inst_list = idb.get_doc_instrs(14)
        assert inst_list == inst14
