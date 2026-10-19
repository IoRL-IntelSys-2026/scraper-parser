"""Test the instruction database abstraction."""

import tempfile

import instr_db


def test_instrdb_methods() -> None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        idb = instr_db.InstructionDatabase.bootstrap(tmp.name)
        pages = idb.get_pages()
        page1: instr_db.TargetPage = {
            "idx": 1,
            "link": "https://admission.rudn.ru/undergraduate/timing/",
            "kind": DocumentKind.PDF,
        }
        inst9: list[instr_db.Instruction] = [
            {
                "step": 1,
                "inst": Mnemonic.EXTRACT_SUBTREE,
                "attrs": {"tag": "div", "class": frozenset({"article__one-inner"})},
            }
        ]
        assert pages[0] == page1
        inst_list = idb.get_doc_instrs(9)
        assert inst_list == inst9
