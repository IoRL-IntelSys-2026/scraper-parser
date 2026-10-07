# -*- coding: utf-8 -*-
'''Functions for interacting with the instructions database.'''
__all__ = []
import sqlite3
import pathlib

class InstructionDatabase:
    def __init__(self, db_loc: pathlib.Path) -> None:
        self.__conn = sqlite3.connect(f'{db_loc.resolve(True).as_uri()}?mode=ro')

    def __del__(self) -> None:
        self.__conn.close()
