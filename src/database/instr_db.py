"""Functions for interacting with the instructions database."""

# instr_db - object-oriented interface for the instructions database
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

__all__ = [
    "DocumentKind",
    "InstAttribute",
    "Instruction",
    "InstructionDatabase",
    "Mnemonic",
    "TargetPage",
    "Topic",
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
    """
    Тип документа, на который ведёт ссылка.

    Определяет, в каком формате хранится целевой документ (HTML или PDF).
    """

    HTML = 1
    PDF = 2


class Mnemonic(enum.Enum):
    """
    Мнемоника шага инструкции для веб-скрапера.

    Каждое значение соответствует атомарному действию, которое
    скрапер должен выполнить при обработке страницы.
    """

    CLICK_FIRST = 1
    EXTRACT_SUBTREE = 2
    IF_MATCHES = 3
    DOWNLOAD_TARGET = 4


class Topic(enum.Enum):
    """
    Тематическая категория целевой страницы.

    Используется для группировки документов по разделам сайта.
    """

    DORMITORY = 1
    CATERING = 2
    ADMISSIONS = 3
    GENERAL_HELP = 4


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
    """Представляет отдельную инструкцию для веб-скрапера."""

    step: int
    inst: Mnemonic
    attrs: InstAttribute


class TargetPage(NamedTuple):
    """Представляет ссылку на веб-страницу, подлежащую парсингу."""

    idx: int
    link: str
    kind: DocumentKind
    topic: Topic


logger = logging.getLogger(__name__)


class InstructionDatabase:
    """
    Абстракция над базой данных инструкций веб-скрапера.

    Управляет соединением с SQLite (открывается в режиме «только чтение»)
    и предоставляет методы для получения страниц и шагов инструкций.
    """

    # Use introspection to get column names without copying code
    ATTR_NAMES: Final = frozenset(get_type_hints(InstAttribute).keys())

    @staticmethod
    def _convert_to_path(db_loc: str | None) -> pathlib.Path:
        """
        Проверяет путь к базе данных и приводит его к абсолютному ``Path``.

        Если ``db_loc`` пуст или ``None``, используется текущий каталог
        (с предупреждением в лог). Если у пути отсутствует имя файла
        (нет суффикса и это не существующий файл), к нему добавляется
        имя по умолчанию ``instr_db.sqlite3``.

        Parameters
        ----------
        db_loc : str or None
            Путь к файлу базы данных или каталогу, в котором он должен
            находиться. Может быть пустой строкой или ``None``.

        Returns
        -------
        pathlib.Path
            Абсолютный путь, гарантированно указывающий на файл
            (существующий или предполагаемый).
        """
        if not db_loc:
            logger.warning("No path was provided, using current directory")
            db_loc = "."
        actual_path = pathlib.Path(db_loc).resolve()
        # Make sure that the path ends in a filename.
        if not (actual_path.is_file() or actual_path.suffix):
            logger.warning(
                'File name missing, assuming it is "instr_db.sqlite3"'
            )
            actual_path /= "instr_db.sqlite3"
        return actual_path

    def __init__(self, db_loc: str | pathlib.Path | None) -> None:
        """
        Открывает соединение с существующей базой данных инструкций.

        Соединение открывается в режиме «только чтение» через URI
        (``mode=ro``). Строки результата возвращаются как ``sqlite3.Row``,
        что позволяет обращаться к колонкам по имени.

        Parameters
        ----------
        db_loc : str or pathlib.Path or None
            Путь к файлу базы данных. Строки и ``None`` проходят через
            :meth:`_convert_to_path`.

        Raises
        ------
        ValueError
            Если итоговый путь не указывает на существующий файл
            (база данных не найдена).
        """
        if isinstance(db_loc, str | None):
            db_loc = self._convert_to_path(db_loc)

        if not db_loc.is_file():
            raise ValueError(
                "db_loc must be a path to the location of the instructions database."
            )

        self._con: Final = sqlite3.connect(
            f"{db_loc.as_uri()}?mode=ro", uri=True
        )
        self._con.row_factory = sqlite3.Row
        self._cur: Final = self._con.cursor()
        # This might need to be changed later
        self._cur.arraysize = 20

    def __del__(self) -> None:
        """
        Закрывает соединение с базой данных при уничтожении объекта.

        Безопасно вызывается, даже если ``__init__`` завершился с ошибкой
        до создания соединения (проверяется наличие атрибута ``_con``).
        """
        if hasattr(self, "_con"):
            self._con.close()

    @classmethod
    def bootstrap(cls, db_loc: str | None) -> Self:
        """
        Создаёт новую базу данных инструкций и заполняет её данными.

        Выполняет SQL-скрипты ``src/sql/instr_schema.sql`` (схема) и
        ``src/sql/instr_data.sql`` (начальные данные) из каталога проекта,
        после чего возвращает экземпляр класса, подключённый к созданной БД.

        Parameters
        ----------
        db_loc : str or None
            Путь, по которому должна быть создана база данных.
            Обрабатывается так же, как в :meth:`_convert_to_path`.

        Returns
        -------
        Self
            Новый экземпляр :class:`InstructionDatabase`, связанный
            с только что созданной базой.

        Notes
        -----
        Если файл по указанному пути уже существует, SQL-скрипты будут
        выполнены поверх него — существующие объекты схемы могут вызвать
        ошибку или быть перезаписаны в зависимости от содержимого скриптов.
        """
        db_path: Final = cls._convert_to_path(db_loc)
        # Should paths to bootstrap files be configurable?
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.executescript(
                (pathlib.Path(__file__).parents[1] / "sql" / "instr_schema.sql")
                .resolve(True)
                .read_text(encoding="utf-8")
            )
            cur.executescript(
                (pathlib.Path(__file__).parents[1] / "sql" / "instr_data.sql")
                .resolve(True)
                .read_text(encoding="utf-8")
            )
        return cls(db_path)

    def get_pages(self) -> list[TargetPage]:
        """
        Возвращает все страницы, доступные для скрапинга.

        Выполняет соединение таблиц ``document`` и ``doc_link`` и
        сортирует результат по идентификатору документа.

        Returns
        -------
        list of TargetPage
            Список целевых страниц, упорядоченный по возрастанию ``idx``.
            Пустой список, если в базе нет документов.

        Notes
        -----
        Типобезопасность результата не гарантируется статически: структура
        таблиц известна только во время выполнения, поэтому значения
        приводятся к перечислениям явно.
        """
        # MyPy cannot know what the database looks like,
        # so there's no way to guarantee type safety here.
        self._cur.execute(
            "select document.*, doc_link.topic from document"
            " join doc_link on doc_link.link = document.link"
            " order by idx"
        )
        return [
            TargetPage(
                idx=row["idx"],
                link=row["link"],
                kind=DocumentKind(row["kind"]),
                topic=Topic(row["topic"]),
            )
            for row in self._cur
        ]

    def get_doc_instrs(self, idx: int) -> list[Instruction]:
        """
        Возвращает последовательность шагов инструкции для документа.

        Читает строки из соединения ``doc_inst`` и ``inst_attr``, группируя
        атрибуты по номеру шага. Атрибут ``class`` разбирается из строки,
        разделённой пробелами, в ``frozenset``. Неизвестные имена атрибутов
        пропускаются с предупреждением в лог.

        Parameters
        ----------
        idx : int
           Идентификатор документа (значение ``TargetPage.idx``).

        Returns
        -------
        list of Instruction
            Шаги инструкции, упорядоченные по возрастанию ``step``.
            Пустой список, если для документа нет ни одного шага.

        Notes
        -----
        Для каждого шага в результирующий ``InstAttribute`` попадают только
        те ключи, которые присутствуют в БД и входят в :attr:`ATTR_NAMES`.
        """
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
                        k: frozenset(attrs[k].split())
                        if k == "class"
                        else attrs[k]
                        for k in self.ATTR_NAMES
                        if k in attrs
                    },
                ),
            )
        )
        return res
