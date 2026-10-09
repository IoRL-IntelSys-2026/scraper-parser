'''Functions for interacting with the instructions database.'''
__all__ = []
import logging
import os
import pathlib
import sqlite3
from typing import Self, TypedDict

class InstrList(TypedDict):
    pass

logger = logging.getLogger(__name__)

class InstructionDatabase:
    @staticmethod
    def _convert_to_path(db_loc: str | None) -> pathlib.Path:
        '''Validates the path provided as the `db_loc` argument
        or the `SCRAPER_DB_PATH` environment variable if `db_loc`
        is empty or `None`, then converts it into a `Path`.'''
        if not db_loc:
            db_env_path = os.getenv('SCRAPER_DB_PATH')
            if not db_env_path:
                logger.warn('No path was provided, using current directory')
                db_loc = '.'
            else:
                db_loc = db_env_path

        # If the provided path doesn't exist, this is likely a mistake,
        # so the OSError exception is intentionally propagated.
        actual_path = pathlib.Path(db_loc).resolve(True)
        # Make sure that the path ends in a filename.
        if not actual_path.name:
            logger.warn('File name missing, assuming it is "instr_db.sqlite3"')
            actual_path /= 'instr_db.sqlite3'
        return actual_path
                

    def __init__(self, db_loc: str | pathlib.Path | None) -> None:
        if isinstance(db_loc, str | None):
            db_loc = self._convert_to_path(db_loc)
            
        if not db_loc.is_file():
            raise ValueError(
                'db_loc must be a path to the location'
                ' of the instructions database.'
            )

        self._con = sqlite3.connect(f'{db_loc.as_uri()}?mode=ro')
        self._cur = self._con.cursor()

    def __del__(self) -> None:
        self._con.close()

    @classmethod
    def bootstrap(cls, db_loc: str | None) -> Self:
        '''Creates a new database using the SQL scripts from the src/sql
        directory.'''
        db_path = cls._convert_to_path(db_loc)
        # Should paths to bootstrap files be configurable?
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.executescript(pathlib.Path(
                f'{__file__}/../../sql/instr_schema.sql'
            ).resolve(True).read_text())
            cur.executescript(pathlib.Path(
                f'{__file__}/../../sql/instr_data.sql'
            ).resolve(True).read_text())
        return cls(db_path)

    def get_page_instrs(self, page_num: int) -> InstrList:
        self._cur.execute(
            'select inst_attr.*, doc_inst.inst from doc_inst'
            ' join inst_attr on doc_inst.doc = inst_attr.doc'
            ' and doc_inst.step = inst_attr.step'
            ' where doc_inst.doc = ?',
            (page_num,)
        )
        
