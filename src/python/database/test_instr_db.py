"""Test the instruction database abstraction."""

import tempfile

from .instr_db import *


def test_instrdb_methods() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        idb = InstructionDatabase.bootstrap(tmp.name)
        pages = idb.get_pages()
        assert pages[0] == {
            "idx": 1,
            "link": "https://admission.rudn.ru/undergraduate/timing/",
            "kind": DocumentKind.PDF,
        }
        inst_list = idb.get_doc_instrs(9)
        assert inst_list == [
            {
                "step": 1,
                "inst": Mnemonic.EXTRACT_SUBTREE,
                "attrs": {"tag": "div", "class": frozenset({"article__one-inner"})},
            }
        ]
