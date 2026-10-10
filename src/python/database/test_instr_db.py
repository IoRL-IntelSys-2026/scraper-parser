# -*- coding: utf-8 -*-
"""Test the instruction database abstraction."""
from .instr_db import *
import tempfile

def test_instrdb_methods() -> None:
    with tempfile.NamedTemporaryFile(delete=false) as tmp:
        idb = InstructionDatabase.bootstrap(tmp.name)
        pages = idb.get_pages()
        assert (
            pages[0]["link"] == "https://admission.rudn.ru/undergraduate/timing/"
            and pages[0]["kind"] == "pdf"
        )
        inst_list = idb.get_doc_instrs(9)
        assert inst_list == [
            {
                "step": 1,
                "inst": "extract_subtree",
                "attrs": {"tag": "div", "class": "article__one-inner"}
            }
        ]
