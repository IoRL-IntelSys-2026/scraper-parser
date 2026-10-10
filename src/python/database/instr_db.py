# -*- coding: utf-8 -*-
"""Functions for interacting with the instructions database."""

__all__ = ["InstructionDatabase"]
import logging
import os
import pathlib
import sqlite3
from typing import Literal, Self, TypedDict, cast

type DocumentKind = Literal["html", "pdf"]

type Mnemonic = Literal[
    "click_first", "extract_subtree", "download_target", "if_matches"
]


class Instruction(TypedDict):
    """Represents an individual instruction for the web scraper."""

    step: int
    inst: Mnemonic
    attrs: dict[str, str]


class TargetPage(TypedDict):
    """Represents a link to a webpage that needs to be parsed."""

    idx: int
    link: str
    kind: DocumentKind


logger = logging.getLogger(__name__)


class InstructionDatabase:
    @staticmethod
    def _convert_to_path(db_loc: str | None) -> pathlib.Path:
        """Validates the path provided as the `db_loc` argument
        or the `SCRAPER_DB_PATH` environment variable if `db_loc`
        is empty or `None`, then converts it into a `Path`."""
        if not db_loc:
            db_env_path = os.getenv("SCRAPER_DB_PATH")
            if not db_env_path:
                logger.warning("No path was provided, using current directory")
                db_loc = "."
            else:
                db_loc = db_env_path

        # If the provided path doesn't exist, this is likely a mistake,
        # so the OSError exception is intentionally propagated.
        actual_path = pathlib.Path(db_loc).resolve(True)
        # Make sure that the path ends in a filename.
        if not actual_path.name:
            logger.warning('File name missing, assuming it is "instr_db.sqlite3"')
            actual_path /= "instr_db.sqlite3"
        return actual_path

    def __init__(self, db_loc: str | pathlib.Path | None) -> None:
        if isinstance(db_loc, str | None):
            db_loc = self._convert_to_path(db_loc)

        if not db_loc.is_file():
            raise ValueError(
                "db_loc must be a path to the location of the instructions database."
            )

        self._con = sqlite3.connect(f"{db_loc.as_uri()}?mode=ro")
        self._con.row_factory = sqlite3.Row
        self._cur = self._con.cursor()
        # This might need to be changed later
        self._cur.arraysize = 20

    def __del__(self) -> None:
        self._con.close()

    @classmethod
    def bootstrap(cls, db_loc: str | None) -> Self:
        """Creates a new database using the SQL scripts from the src/sql
        directory."""
        db_path = cls._convert_to_path(db_loc)
        # Should paths to bootstrap files be configurable?
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.executescript(
                pathlib.Path(f"{__file__}/../../sql/instr_schema.sql")
                .resolve(True)
                .read_text()
            )
            cur.executescript(
                pathlib.Path(f"{__file__}/../../sql/instr_data.sql")
                .resolve(True)
                .read_text()
            )
        return cls(db_path)

    def get_pages(self) -> list[TargetPage]:
        """Fetch all pages available for scraping."""
        # MyPy cannot know what the database looks like,
        # so there's no way to guarantee type safety here.
        return cast(
            list[TargetPage], self._cur.execute("select * from document").fetchall()
        )

    def get_doc_instrs(self, idx: int) -> list[Instruction]:
        """Fetch instructions for a document with this identifier."""
        res: list[Instruction] = []
        last_step = 0
        self._cur.execute(
            "select inst_attr.*, doc_inst.inst from doc_inst"
            " join inst_attr on doc_inst.doc = inst_attr.doc"
            " and doc_inst.step = inst_attr.step"
            " where doc_inst.doc = ? order by doc_inst.step",
            (idx,),
        )
        for row in self._cur:
            if row["step"] != last_step:
                last_step = row["step"]
                res.append(
                    {
                        "step": last_step,
                        "inst": row["inst"],
                        "attrs": {row["kind"]: row["val"]},
                    }
                )
            else:
                res[-1]["attrs"][row["kind"]] = row["val"]
        return res
