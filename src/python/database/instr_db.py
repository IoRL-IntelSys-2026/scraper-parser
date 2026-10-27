"""Functions for interacting with the instructions database."""

__all__ = [
    "DocumentKind",
    "Instruction",
    "InstructionDatabase",
    "Mnemonic",
    "TargetPage",
]
import enum
import logging
import pathlib
import sqlite3
from typing import (
    Final,
    NamedTuple,
    ReadOnly,
    Self,
    TypedDict,
    cast,
    get_type_hints,
)


class DocumentKind(enum.Enum):
    HTML = 1
    PDF = 2


class Mnemonic(enum.Enum):
    CLICK_FIRST = 1
    EXTRACT_SUBTREE = 2
    IF_MATCHES = 3
    DOWNLOAD_TARGET = 4


InstAttribute = TypedDict(
    "InstAttribute",
    {
        "tag": ReadOnly[str],
        "id": ReadOnly[str],
        "class": ReadOnly[frozenset[str]],
        "text": ReadOnly[str],
        "data-editor": ReadOnly[str],
    },
    total=False,
)


class Instruction(NamedTuple):
    """Represents an individual instruction for the web scraper."""

    step: int
    inst: Mnemonic
    attrs: InstAttribute


class TargetPage(NamedTuple):
    """Represents a link to a webpage that needs to be parsed."""

    idx: int
    link: str
    kind: DocumentKind


logger = logging.getLogger(__name__)


class InstructionDatabase:
    """Abstraction over the web scraper instructions database.
    Manages the SQLite connection."""

    # Use introspection to get column names without copying code
    ATTR_NAMES: Final = frozenset(get_type_hints(InstAttribute).keys())

    @staticmethod
    def _convert_to_path(db_loc: str | None) -> pathlib.Path:
        """Validates the path provided as the `db_loc` argument
        or the `SCRAPER_DB_PATH` environment variable if `db_loc`
        is empty or `None`, then converts it into a `Path`."""
        if not db_loc:
            logger.warning("No path was provided, using current directory")
            db_loc = "."
        actual_path = pathlib.Path(db_loc).resolve()
        # Make sure that the path ends in a filename.
        if not (actual_path.is_file() or actual_path.suffix):
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

        self._con: Final = sqlite3.connect(f"{db_loc.as_uri()}?mode=ro", uri=True)
        self._con.row_factory = sqlite3.Row
        self._cur: Final = self._con.cursor()
        # This might need to be changed later
        self._cur.arraysize = 20

    def __del__(self) -> None:
        self._con.close()

    @classmethod
    def bootstrap(cls, db_loc: str | None) -> Self:
        """Creates a new database using the SQL scripts from the src/sql
        directory."""
        db_path: Final = cls._convert_to_path(db_loc)
        # Should paths to bootstrap files be configurable?
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.executescript(
                (pathlib.Path(__file__).parent / "../../sql/instr_schema.sql")
                .resolve(True)
                .read_text(encoding="utf-8")
            )
            cur.executescript(
                (pathlib.Path(__file__).parent / "../../sql/instr_data.sql")
                .resolve(True)
                .read_text(encoding="utf-8")
            )
        return cls(db_path)

    def get_pages(self) -> list[TargetPage]:
        """Fetch all pages available for scraping."""
        # MyPy cannot know what the database looks like,
        # so there's no way to guarantee type safety here.
        self._cur.execute("select * from document order by idx")
        return [
            TargetPage(idx=row["idx"], link=row["link"], kind=DocumentKind(row["kind"]))
            for row in self._cur
        ]

    def get_doc_instrs(self, idx: int) -> list[Instruction]:
        """Fetch instructions for a document with this identifier."""
        res: Final[list[Instruction]] = []
        attrs: Final[dict[str, str]] = {}
        self._cur.execute(
            "select doc_inst.step, doc_inst.inst, inst_attr.kind,"
            " inst_attr.val from doc_inst"
            " join inst_attr on doc_inst.doc = inst_attr.doc"
            " and doc_inst.step = inst_attr.step"
            " where doc_inst.doc = ? order by doc_inst.step",
            (idx,),
        )
        row = self._cur.fetchone()
        if row is None:
            return res
        attrs[row["kind"]] = row["val"]
        last_step: int = row["step"]
        last_inst = Mnemonic(row["inst"])
        for row in self._cur:
            step: int = row["step"]
            inst = Mnemonic(row["inst"])
            kind: str = row["kind"]
            val: str = row["val"]

            if last_step != step:
                res.append(
                    Instruction(
                        step=last_step,
                        inst=last_inst,
                        attrs=cast(
                            InstAttribute,
                            {
                                k: frozenset(attrs[k].split())
                                if k == "class"
                                else attrs[k]
                                for k in self.ATTR_NAMES
                                if k in attrs
                            },
                        ),
                    )
                )
                attrs.clear()

            if kind in self.ATTR_NAMES:
                attrs[kind] = val
            else:
                logger.warning(f"Unknown attribute {kind}, skipping it.")

            last_step = step
            last_inst = inst
        res.append(
            Instruction(
                step=last_step,
                inst=last_inst,
                attrs=cast(
                    InstAttribute,
                    {
                        k: frozenset(attrs[k].split()) if k == "class" else attrs[k]
                        for k in self.ATTR_NAMES
                        if k in attrs
                    },
                ),
            )
        )
        return res
