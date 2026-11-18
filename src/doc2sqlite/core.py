from abc import ABC, abstractmethod
from typing import Final, List, Tuple, Optional, Any

import os, sys, argparse, re, sqlite3, yaml, json
from importlib.resources import files as imprsrcs
from pathlib import Path

import pandas as pd

import logging

# ------------------------------------------------------------------ Logger ---


def setup_logging(my_name: str, log_file=None):
    """
    Configures the root logger.
    """
    # Define formatter
    formatter = logging.Formatter(
        "%(asctime)s|%(levelname)-8s|%(name)s| %(message)s",
        # "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Get root logger
    root_logger = logging.getLogger(my_name)
    root_logger.setLevel(logging.DEBUG)  # Capture all levels

    # Remove existing handlers to avoid duplicates if called multiple times
    root_logger.handlers = []

    # Console Handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler (DEBUG and above) - Optional
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


MY_NAME = "doc2sqlite"
logger = setup_logging(MY_NAME, log_file=f"{MY_NAME}.log")


def flush_logger(logger):
    for handler in logger.handlers:
        try:
            handler.flush()  # All standard handlers support .flush()
        except AttributeError:
            pass  # Handle custom handlers that might not support flush


# ---------------------------------------------------------------- hello!!! ---


def hello():
    logger.info(f"{MY_NAME}, hello!")
    pass


# ----------------------------------------------------------- ConfigHandler ---


class EmptyCommandLine(Exception):
    """Exception raised when a user do not used any command line flag."""

    pass


class ConfigHandler:

    # --- Static Configuration Definitions ---
    # Structure: key_name: {"arg_flag": str, "default": bool, "depends_on": str or None}
    CONFIG_SCHEMA: Final[dict] = {
        # Paths
        "InputPdf": {"default": None, "depends_on": None, "type": "path"},
        # "OutputDb": {"default": "output.db", "depends_on": None, "type": "path"},
        # "ConfigFile": {"default": None, "depends_on": None, "type": "path"},
        # Booleans - Document Level
        "All": {"default": False, "depends_on": None},
        #
        "DocumentInfo": {"default": True, "depends_on": None},
        "DocumentPageLabel": {"default": True, "depends_on": None},
        "DocumentToC": {"default": True, "depends_on": None},
        "DocumentEmbeddedFileInfo": {"default": False, "depends_on": None},
        "DocumentEmbeddedFile": {
            "default": False,
            "depends_on": "DocumentEmbeddedFileInfo",
        },
        "DocumentFont": {"default": False, "depends_on": "PageFont"},
        "DocumentUniqueFont": {"default": False, "depends_on": "DocumentFont"},
        "DocumentLink": {"default": False, "depends_on": "PageLink"},
        # Booleans - Page Level
        "PagePhysical2Label": {
            "default": False,
            "depends_on": None,
        },  # Note: Original default was False, property returned True? Fixed to match arg default False.
        "PageFont": {"default": False, "depends_on": None},
        "PageBlock": {"default": True, "depends_on": None},
        "PageBlockVersioned": {"default": True, "depends_on": "PageBlock"},
        "PageBlockTranslated": {"default": True, "depends_on": "PageBlock"},
        "PageBlockFTS": {"default": False, "depends_on": "PageBlock"},
        "PageLink": {"default": True, "depends_on": None},
        "PageHtml": {"default": False, "depends_on": None},
        "PageXHtml": {"default": False, "depends_on": None},
        "PageXml": {"default": False, "depends_on": None},
        "PageText": {
            "default": False,
            "depends_on": None,
        },  # Original default was False in help, but property returned True? Fixed to False.
        "PageDict": {"default": False, "depends_on": None},
        "PageRawDict": {"default": False, "depends_on": None},
        "PageJson": {"default": False, "depends_on": None},
        "PageRawJson": {"default": False, "depends_on": None},
        "PageSvg": {"default": False, "depends_on": None},
        "PageSvgTextAsPath": {"default": False, "depends_on": None},
        "PagePixmap": {"default": False, "depends_on": None},
        "PageDrawings": {"default": False, "depends_on": None},
        "PageWord": {"default": False, "depends_on": None},
        "DocumentWordFrequency": {"default": False, "depends_on": "PageWord"},
        "PageWordFrequency": {"default": False, "depends_on": "PageWord"},
        #
        "PageTable": {"default": False, "depends_on": None},
        "PageTableCsv": {"default": False, "depends_on": "PageTable"},
        "PageTableHtml": {"default": False, "depends_on": "PageTable"},
        "PageTableJson": {"default": False, "depends_on": "PageTable"},
        "PageTableList": {"default": False, "depends_on": "PageTable"},
        "PageTableMarkdown": {"default": False, "depends_on": "PageTable"},
        "PageTablePixMap": {"default": False, "depends_on": "PageTable"},
        "PageTableSql": {"default": False, "depends_on": "PageTable"},
        #
        "PageImageInfo": {"default": False, "depends_on": None},
        "PageImage": {"default": False, "depends_on": None},
        "PageAnnotation": {"default": False, "depends_on": None},
        # "PageBlockKG": {"default": False, "depends_on": None},
    }
    RUTIME_CONFIG_SCHEMA: Final[dict] = CONFIG_SCHEMA

    def __init__(self, logger, args: Optional[List[str]] = None):
        self.logger = logger
        I = self.logger.info

        self._myname = os.path.basename(sys.argv[0])
        abs_path = Path(__file__).resolve()

        I("Parsing SQLite3 statements...")
        self.STATEMENTS_YAML = abs_path.parent / "statements.yaml"
        self._stmt = None
        self.load_statements()

        I("Parsing command line parameters...")

        # Combine sys.argv and passed args
        self.final_args: List[str] = sys.argv[1:]
        if args:
            self.final_args.extend(args)

        # Build Parser
        parser = argparse.ArgumentParser(
            description="Extract document information.",
            epilog=f"Example: python {self._myname} --InputPdf file.pdf",
            add_help=True,
        )
        self.build_argument_parser(parser)

        if len(self.final_args) == 0:
            # parser.print_usage()
            parser.print_help()
            raise EmptyCommandLine()

        try:
            self._args = parser.parse_args(self.final_args)
        except SystemExit:
            raise

        I("Parsing config file parameters...")
        self._cfg = None
        cfg_path = self._args.ConfigFile
        if cfg_path:
            if self._file_exists_and_readable(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    self._cfg = yaml.safe_load(f)

        # TODO : .venv/bin/python src/doc2sqlite/main.py --All
        if self._args.All is not None:
            for key, schInfo in self.RUTIME_CONFIG_SCHEMA.items():
                if key.startswith("Document") or key.startswith("Page"):
                    if schInfo.get("default") is not None:
                        # Optional: print to verify
                        schInfo["default"] = self._args.All

        I("Done!")

    def load_statements(self):
        try:
            # 1. Get the path object for the resource
            yaml_path = imprsrcs(MY_NAME).joinpath(str(self.STATEMENTS_YAML))

            # 2. Check if the resource exists
            # Note: In Python 3.9+, files() returns a Traversable.
            # It doesn't raise an error if the file doesn't exist immediately,
            # but reading it will. However, we can check existence if needed.
            if yaml_path.is_file():
                # 3. Read the content as a UTF-8 string
                yaml_content = yaml_path.read_text(encoding="utf-8")

                # 4. Parse the YAML
                self._stmt = yaml.safe_load(yaml_content)
            else:
                # Handle case where file is missing in the package
                raise FileNotFoundError(
                    f"Resource {self.STATEMENTS_YAML} not found in package {MY_NAME}"
                )

        except Exception as e:
            # Handle errors (e.g., YAML syntax errors, import errors)
            raise RuntimeError(f"Failed to load statements: {e}")

    def build_argument_parser(self, parser):
        # Helper to add boolean arguments dynamically to reduce boilerplate
        # We still need to add them explicitly for argparse to recognize them,
        # but we can streamline the loop.

        # Mandatory/Path arguments
        parser.add_argument(
            "-i",
            "--InputPdf",
            required=False,
            default=None,
            type=str,
            dest="InputPdf",
            help="Path to the input PDF file",
        )
        # parser.add_argument(
        #     "-o",
        #     "--OutputDb",
        #     required=False,
        #     default="output.db",
        #     type=self._validate_output_db,
        #     dest="OutputDb",
        #     help="Output database file path",
        # )
        parser.add_argument(
            "-c",
            "--ConfigFile",
            required=False,
            dest="ConfigFile",
            help="YAML config file path",
        )
        parser.add_argument(
            "-l",
            "--log",
            default=sys.stdout,
            type=argparse.FileType("w"),
            help="Log file path",
        )

        # Dynamic Boolean Arguments based on Schema
        for key, config in self.RUTIME_CONFIG_SCHEMA.items():
            # if key in ["InputPdf", "OutputDb", "ConfigFile"]:
            if key in ["InputPdf", "ConfigFile"]:
                continue  # Handled above

            # Determine help text default status based on schema default
            default_val = config["default"]
            help_text = f"(default: {default_val}) "

            # Map specific descriptions if needed, otherwise generic
            # In a real refactoring, these descriptions should be in the schema too.
            # For now, we keep the argparse calls minimal.

            parser.add_argument(
                f"--{key}",
                action=argparse.BooleanOptionalAction,
                dest=key,
                help=help_text,
            )

    def _resolve_config_value(self, key: str) -> Any:
        """
        Resolves configuration value based on priority:
        1. Command Line Args
        2. Config File (_cfg)
        3. Default Value from Schema
        """
        # 1. Check Args
        if self._args and hasattr(self._args, key):
            val = getattr(self._args, key)
            if val is not None:
                return val

        # 2. Check Config File
        if self._cfg and key in self._cfg:
            return self._cfg[key]

        # 3. Default
        if key in self.RUTIME_CONFIG_SCHEMA:
            return self.RUTIME_CONFIG_SCHEMA[key]["default"]

        # Fallback for undefined keys (should not happen with current schema)
        return None

    # --- Property Accessors ---
    # These properties handle the dependency logic and type casting if necessary.
    # Using __getattr__ or explicit properties? Explicit properties are safer for IDE support and dependency checks.

    def _get_bool_with_dep_check(self, key: str) -> bool:
        """Helper to get boolean and check dependencies."""
        val = self._resolve_config_value(key)
        if not isinstance(val, bool):
            # Handle case where config might return non-bool string/None
            val = bool(val)

        config = self.RUTIME_CONFIG_SCHEMA.get(key, {})
        depends_on = config.get("depends_on")

        if depends_on:
            # Recursively ensure dependency is True
            if not self._get_bool_with_dep_check(depends_on):
                raise ValueError(f"{key} requires {depends_on} to be True")

        return val

    @property
    def InputPdf(self) -> str:
        return self._resolve_config_value(sys._getframe().f_code.co_name) or None

    # @property
    # def OutputDb(self) -> str:
    #     x = sys._getframe().f_code.co_name
    #     return self._resolve_config_value(x) or x

    @property
    def All(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentInfo(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentPageLabel(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentToC(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentEmbeddedFileInfo(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentEmbeddedFile(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PagePhysical2Label(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageFont(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentFont(self) -> bool:
        return self._get_bool_with_dep_check(sys._getframe().f_code.co_name)

    @property
    def DocumentUniqueFont(self) -> bool:
        return self._get_bool_with_dep_check(sys._getframe().f_code.co_name)

    @property
    def PageBlock(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageBlockVersioned(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageBlockTranslated(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageBlockFTS(self) -> bool:
        return self._get_bool_with_dep_check(sys._getframe().f_code.co_name)

    @property
    def PageLink(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentLink(self) -> bool:
        return self._get_bool_with_dep_check(sys._getframe().f_code.co_name)

    @property
    def PageHtml(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageXHtml(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageXml(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageText(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageDict(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageRawDict(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageJson(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageRawJson(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageSvg(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageSvgTextAsPath(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PagePixmap(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageDrawings(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageWord(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def DocumentWordFrequency(self) -> bool:
        return self._get_bool_with_dep_check(sys._getframe().f_code.co_name)

    @property
    def PageWordFrequency(self) -> bool:
        return self._get_bool_with_dep_check(sys._getframe().f_code.co_name)

    @property
    def PageTable(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageTableCsv(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageTableHtml(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageTableJson(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageTableList(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageTableMarkdown(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageTablePixMap(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageTableSql(self) -> bool:
        return bool(self._get_bool_with_dep_check(sys._getframe().f_code.co_name))

    @property
    def PageImageInfo(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageImage(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    @property
    def PageAnnotation(self) -> bool:
        return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    # @property
    # def PageBlockKG(self) -> bool:
    #     return bool(self._resolve_config_value(sys._getframe().f_code.co_name))

    # --- Validation Helpers ---

    def _file_exists_and_readable(self, path: str) -> bool:
        if not path:
            return False
        if not os.path.exists(path):
            return False
        if not os.path.isfile(path):
            return False
        if not os.access(path, os.R_OK):
            return False
        return True

    def _validate_pdf_file(self, path: str) -> str:
        if not os.path.exists(path):
            raise argparse.ArgumentTypeError(f"The file '{path}' does not exist.")
        if not os.path.isfile(path):
            raise argparse.ArgumentTypeError(f"'{path}' is not a file.")
        if not os.access(path, os.R_OK):
            raise argparse.ArgumentTypeError(f"The file '{path}' is not readable.")
        if not path.lower().endswith(".pdf"):
            raise argparse.ArgumentTypeError(f"The file '{path}' is not a PDF file.")
        try:
            with open(path, "rb") as f:
                f.read(4)
        except Exception as e:
            raise argparse.ArgumentTypeError(f"Cannot read file '{path}': {e}")
        return path

    def _validate_output_db(self, path: str) -> str:
        parent = os.path.dirname(path) or "."
        if not os.access(parent, os.W_OK):
            raise argparse.ArgumentTypeError(f"Directory '{parent}' is not writable.")
        if os.path.exists(path):
            raise argparse.ArgumentTypeError(f"File '{path}' already exists.")
        return path

    def print(self):
        I = self.logger.info
        I("\n")
        I(f"Command-line arguments:\n{self.final_args}\n")
        I(f"Config file arguments:\n{self._cfg}\n")
        I("Execution parameters : command line + config file + default config:")

        # Print all resolved configs dynamically to keep this method clean
        # Iterate over schema keys to ensure consistent order and coverage
        for key in self.RUTIME_CONFIG_SCHEMA:
            # Skip internal/path configs if they are handled differently,
            # but the original code printed everything.
            try:
                val = self.__getattribute__(key)
                I(f"{key}: {val}")
            except Exception:
                # Fallback if property fails (e.g., dependency error not caught yet)
                I(f"{key}: <Error resolving>")

        for key, schInfo in self.RUTIME_CONFIG_SCHEMA.items():
            if key.startswith("Document") or key.startswith("Page"):
                if schInfo.get("default") is not None:
                    # Optional: print to verify
                    schInfo["default"] = self._args.All


# --------------------------------------------------- PandasToSqliteOffline ---


class PandasToSqliteOffline:
    """
    A utility class to convert pandas DataFrames into SQLite3
    SQL script strings completely offline without a database connection.
    """

    @staticmethod
    def _map_dtype(dtype_str: str) -> str:
        """Maps a pandas data type string to an SQLite3 storage class."""
        dtype_lower = dtype_str.lower()
        if any(x in dtype_lower for x in ["int", "bool"]):
            return "INTEGER"
        elif any(x in dtype_lower for x in ["float", "double", "decimal"]):
            return "REAL"
        elif any(
            x in dtype_lower for x in ["str", "object", "category", "date", "time"]
        ):
            return "TEXT"
        return "BLOB"

    @classmethod
    def get_column_definitions(cls, df_sql: pd.DataFrame) -> List[str]:
        column_definitions = []
        for col, dtype in df_sql.dtypes.items():
            column_name = "RID" if col == "index" else col
            sqlite_type = cls._map_dtype(str(dtype))
            column_definitions.append(f'    "{column_name}" {sqlite_type}')
        return column_definitions

    @classmethod
    def generate_view(cls, df: pd.DataFrame, view_name: str = "VIEW_NAME") -> str:
        select_rows = []

        for i, row in enumerate(df.itertuples(index=False)):
            formatted_values = []
            for col_idx, value in enumerate(row):
                if pd.isna(value):
                    val_str = "NULL"
                elif isinstance(value, bool):
                    val_str = "1" if value else "0"
                elif isinstance(value, str):
                    val_str = f"'{value.replace("'", "''")}'"
                else:
                    val_str = str(value)

                # Assign names & alias overrides to the first row columns
                if i == 0:
                    raw_col_name = df.columns[col_idx]
                    sql_col_name = "RID" if raw_col_name == "index" else raw_col_name
                    val_str = f'{val_str} AS "{sql_col_name}"'

                formatted_values.append(val_str)

            select_rows.append(f"   SELECT {', '.join(formatted_values)}")

        view_body = "\nUNION ALL\n".join(select_rows)

        return f'-- DROP VIEW IF EXISTS "{view_name}";\nCREATE VIEW IF NOT EXISTS\n"{view_name}"\nAS\n{view_body}\n;'

    @classmethod
    def generate_sql(
        cls,
        df: pd.DataFrame,
        table_name: str = "TABLE_NAME",
        include_index: bool = True,
    ) -> Tuple[str, List[str]]:
        # 1. Capture original column headers as a single-row DataFrame
        header_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)
        # 2. Stack the header row on top of the original data and reset the index
        df_transformed = pd.concat([header_row, df], ignore_index=True)
        # 3. Rename columns using zero-padded sequential integers (Col01, Col02, etc.)
        df_transformed.columns = [
            f"C{i:02d}" for i in range(1, len(df_transformed.columns) + 1)
        ]
        # 4. Handle index configuration
        df_sql = (
            df_transformed.reset_index() if include_index else df_transformed.copy()
        )

        column_definitions = cls.get_column_definitions(df_sql)
        view_definition = cls.generate_view(df_sql, table_name)

        drop_statement = f'DROP TABLE IF EXISTS "{table_name}"\n;'

        schema_body = ",\n".join(column_definitions)
        create_statement = (
            f'CREATE TABLE IF NOT EXISTS\n"{table_name}"\n(\n{schema_body}\n)\n;'
        )

        # 3. Build INSERT INTO Statements
        insert_statements = ""
        # columns_header = ", ".join([f'"{col}"' for col in df_sql.columns])
        columns_header = ", ".join(
            [f'"{ "RID" if col == "index" else col }"' for col in df_sql.columns]
        )

        for row in df_sql.itertuples(index=False):
            formatted_values = []
            for value in row:
                if pd.isna(value):
                    formatted_values.append("NULL")
                elif isinstance(value, bool):
                    formatted_values.append("1" if value else "0")
                elif isinstance(value, str):
                    escaped_str = value.replace("'", "''")  # Escape single quotes
                    formatted_values.append(f"'{escaped_str}'")
                elif isinstance(value, (int, float)):
                    formatted_values.append(str(value))
                else:
                    formatted_values.append(f"'{value}'")

            values_body = ", ".join(formatted_values)
            insert_statements += f'INSERT INTO "{table_name}"\n({columns_header})\nVALUES ({values_body})\n;\n'

        # 4. Build SELECT FROM Statements
        select_statements = f'SELECT {columns_header}\n  FROM "{table_name}"\n;'

        return (
            drop_statement,
            create_statement,
            insert_statements,
            select_statements,
            view_definition,
        )


# --------------------------------------------------------- get_fts_matches ---


def get_fts_matches(db_connection, search_query, column_index=1):
    """Executes FTS5 query and extracts only the exact strings that matched."""
    """
    # 3. Test the extraction with prefix matching (data* or python*)
    search_term = "python* OR data*"
    matched_words = get_fts_matches(conn, search_term, column_index=1)

    print(f"Search Query: {search_term}")
    print(f"Exact Strings Matched: {matched_words}")
    """
    # Use highlight() to wrap matches in specific delimiters
    sql = f"""
        SELECT highlight(articles, {column_index}, '|||', '|||') 
        FROM articles 
        WHERE articles MATCH ?
    """

    cursor = db_connection.cursor()
    cursor.execute(sql, (search_query,))

    # Find everything between our '|||' boundaries
    pattern = re.compile(r"\|\|\|(.*?)\|\|\|")
    all_matches = []

    for (highlighted_text,) in cursor.fetchall():
        # Extract matches from the current row
        row_matches = pattern.findall(highlighted_text)
        all_matches.extend(row_matches)

    # Return a unique, lowercase list of the words that matched
    return list(set(word.lower() for word in all_matches))


# --------------------------------------------------------------- BaseClass ---

from pymupdf import (
    pymupdf,
    Document as PyMuPDFDoc,
    Page as PyMuPDFPage,
    # TextPage as PyMuPDFTxt,
    Rect,
    Matrix,
)


class BaseClass(ABC):

    def __enter__(self):
        # print(f"{sys._getframe(0).f_code.co_name}.{self.__class__.__name__}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Guaranteed to run
        # print(f"{sys._getframe(0).f_code.co_name}.{self.__class__.__name__}")
        self.data = None
        return False

    def __del__(self):
        # May not run
        # print(f"{sys._getframe(0).f_code.co_name}.{self.__class__.__name__}")
        pass

    def __init__(self, cfg: ConfigHandler):
        self.cfg = cfg
        I = cfg.logger.info
        I(f"{self.__class__.__name__}.{sys._getframe(0).f_code.co_name}")

        self.data: List[Tuple[Any, ...]] = []
        if not getattr(cfg, self.__class__.__name__):
            return

        # zoom (float): Zoom factor for image resolution (default 2).
        self.zoom = 2.0
        # Create zoom matrix for better resolution
        self.mat = Matrix(self.zoom, self.zoom)

    def append(self, page: PyMuPDFPage):
        pass

    def append(self, doc: PyMuPDFDoc):
        pass

    def persist(self, cfg: ConfigHandler):
        I = cfg.logger.info
        I(f"{self.__class__.__name__}.{sys._getframe(0).f_code.co_name}")
        #
        self.dbNm = cfg._stmt[self.__class__.__name__]["NAME"]
        drop = cfg._stmt[self.__class__.__name__]["DDL"]["DROP"]
        create = cfg._stmt[self.__class__.__name__]["DDL"]["CREATE"]
        insert = cfg._stmt[self.__class__.__name__]["DML"]["INSERT"]

        dbPath = Path(self.dbNm)
        dbPath.parent.mkdir(parents=True, exist_ok=True)

        conn: DbConn = sqlite3.connect(self.dbNm)

        conn.execute(drop)
        conn.execute(create)

        if getattr(self, "data", None) is not None:
            curs: DbCursor = conn.cursor()
            curs.execute("BEGIN TRANSACTION")
            curs.executemany(insert, self.data)
            curs.execute("COMMIT")

        conn.close()

        conn = None

        pass

    def persist_view(self, cfg: ConfigHandler):
        I = cfg.logger.info
        I(f"{self.__class__.__name__}.{sys._getframe(0).f_code.co_name}")
        #
        self.dbNm = cfg._stmt[self.__class__.__name__]["NAME"]
        drop = cfg._stmt[self.__class__.__name__]["DDL"]["DROP"]
        create = cfg._stmt[self.__class__.__name__]["DDL"]["CREATE"]

        conn: DbConn = sqlite3.connect(self.dbNm)

        conn.execute(drop)
        conn.execute(create)
        conn.close()

        conn = None

        pass


# ------------------------------------------------ DocumentEmbeddedFileInfo ---


class DocumentEmbeddedFileInfo(BaseClass):

    def append(self, doc: PyMuPDFDoc):

        for name in doc.embfile_names():
            info_dict = doc.embfile_info(name)
            entry = json.dumps(info_dict, ensure_ascii=False, default=str)
            self.data.append((entry,))
            flush_logger(self.cfg.logger)
            pass


# ------------------------------------------------ DocumentEmbeddedFile ---


class DocumentEmbeddedFile(BaseClass):

    def append(self, doc: PyMuPDFDoc):

        # entry = (None,)  # DOC_ID - unique identifier
        # self.data.append(entry)
        # flush_logger(self.cfg.logger)
        pass


# ------------------------------------------------------------ DocumentInfo ---


class DocumentInfo(BaseClass):

    def append(self, doc: PyMuPDFDoc):

        entry = (
            None,  # DOC_ID - unique identifier
            doc.name,  # NAME - document filename
            doc.page_count,  # PAGE_COUNT - total pages (int)
            doc.chapter_count,  # CHAPTER_COUNT - number of chapters (int)
            doc.permissions,  # PERMISSIONS - permission flags (int)
            doc.is_closed,  # IS_CLOSED - closed/finalized status (bool)
            doc.is_dirty,
            doc.is_pdf,  # IS_PDF - format type (bool)
            doc.is_encrypted,  # IS_ENCRYPTED - password protected (bool)
            doc.is_repaired,  # IS_REPAIRED - repair was applied (bool)
            doc.is_reflowable,  # IS_REFLOWABLE - reflowable format (bool)
            doc.is_form_pdf,  # IS_FORM_PDF - interactive form (bool)
            doc.is_fast_webaccess,
            doc.needs_pass,  # NEED_PASS - password required (bool)
            doc.version_count,  # VERSION_COUNT - incremental versions (int)
            doc.pagelayout,  # PAGELAYOUT - page layout mode (str)
            doc.pagemode,  # PAGEMODE - initial display mode (str)
            doc.get_sigflags(),  # SIGNATURE_FIELDS - number of signatures (int)
            doc.embfile_count(),  # EMBFILE_COUNT - embedded files count (int)
            doc.has_annots(),  # HAS_ANNOTS - has annotations (bool)
            doc.has_links(),  # HAS_LINKS - has hyperlinks (bool)
            doc.get_xml_metadata(),  # XML_METADATA - XMP metadata (str)
            str(doc.markinfo),  # MARKINFO - stringified mark dict (str)
            str(doc.outline),
            str(doc.metadata),
            str(doc.last_location),
            str(doc.FormFonts),
        )
        self.data.append(entry)
        flush_logger(self.cfg.logger)


# ------------------------------------------------------- DocumentPageLabel ---


class DocumentPageLabel(BaseClass):

    def append(self, doc: PyMuPDFDoc):

        # type: list[{'startpage': int, 'prefix': str, 'style': str, 'firstpagenum': int}]
        page_labels = doc.get_page_labels()

        # {'startpage': int, 'prefix': str, 'style': str, 'firstpagenum': int}
        for pl in page_labels:
            entry = (
                pl["startpage"],  # type: int
                pl["prefix"],  # type: str
                pl["firstpagenum"],  # type: int
                pl.get("style", None),  # type: str
            )
            self.data.append(entry)
        flush_logger(self.cfg.logger)


# ------------------------------------------------------------- DocumentToC ---


class DocumentToC(BaseClass):

    def append(self, doc: PyMuPDFDoc):

        # type: list[tuple[lvl:int, title:str, page:int, dest:dic[]]]
        toc = doc.get_toc(False)

        LINK_DESTINATION_KINDS = [
            "LINK_NONE",  # 0 – No destination. Indicates a dummy link.
            "LINK_GOTO",  # 1 – Points to a place in this document.
            "LINK_URI",  # 2 – Points to a URI – typically a resource specified with internet syntax.
            # - PyMuPDF treats any external link that contains a colon and does not start
            # with 'file:' as LINK_URI.
            "LINK_LAUNCH",  # 3 – Launch (open) another file (of any “executable” type).
            # - PyMuPDF treats any external link that starts with 'file:' or doesn’t
            #   contain a colon, as LINK_LAUNCH.
            "LINK_NAMED",  # 4 – points to a named location.
            "LINK_GOTOR",  # 5 – Points to a place in another PDF document.
        ]

        for tocEntry in toc:
            level, title, page, dest = tocEntry

            dest_kind = None
            dest_kind_name = None
            dest_file = None
            dest_page_0based = None
            dest_to = None
            dest_zoom = None
            dest_xref = None
            dest_color = None
            dest_view = None
            dest_bold = None
            dest_italic = None
            dest_collapse = None
            dest_nameddest = None
            dest_to_x = None
            dest_to_y = None

            if dest is not None:
                dest_kind = dest.get("kind")
                dest_kind_name = (
                    LINK_DESTINATION_KINDS[dest_kind]
                    if dest_kind is not None and 0 <= dest_kind <= 5
                    else "UNKNOWN"
                )

                dest_file = dest.get("file")
                dest_page_0based = dest.get("page")
                dest_zoom = dest.get("zoom")
                dest_xref = dest.get("xref")
                dest_view = dest.get("view")
                dest_color = str(dest.get("color"))
                dest_bold = dest.get("bold")
                dest_italic = dest.get("italic")
                dest_collapse = dest.get("collapse")
                dest_nameddest = dest.get("nameddest")

                dest_to = dest.get("to")
                if dest_to is not None:
                    dest_to_x = dest_to.x
                    dest_to_y = dest_to.y

            entry = (
                level,  # type: int
                page,  # type: int
                title,  # type: str
                dest_kind,
                dest_kind_name,
                dest_file,
                dest_page_0based,
                dest_zoom,
                dest_xref,
                dest_view,
                dest_color,
                dest_bold,
                dest_italic,
                dest_collapse,
                dest_nameddest,
                dest_to_x,
                dest_to_y,
                str(dest),  # type: str
            )
            self.data.append(entry)

        flush_logger(self.cfg.logger)


# ---------------------------------------------------------- PageAnnotation ---


class PageAnnotation(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Clean up the page contents to ensure accurate image extraction.
        page.clean_contents()

        counter = 0

        for annot in page.annots():

            if annot is None:
                continue

            counter += 1

            # annot_parent = annot.parent
            # annot_next = annot.next

            # Render page to a Pixmap, clipped to table rect
            pix = page.get_pixmap(matrix=annot.apn_matrix, clip=annot.rect)

            entry = (
                page.number,
                counter,
                str(annot.type),
                str(annot.apn_bbox),
                str(annot.apn_matrix),
                str(annot.blendmode),
                str(annot.colors),
                # annot_file_info = annot.file_info
                str(annot.flags),
                str(annot.has_popup),
                str(annot.is_open),
                str(json.dumps(annot.info)),
                str(annot.irt_xref),
                str(annot.language),
                str(annot.line_ends),
                str(annot.popup_rect),
                str(annot.popup_xref),
                str(annot.rect),
                str(annot.rotation),
                str(annot.opacity),
                str(annot.rect_delta),
                str(annot.vertices),
                str(annot.xref),
                pix.tobytes(),  # BLOB
            )

            self.data.append(entry)

        pass


# --------------------------------------------------------------- PageBlock ---


class PageBlock(BaseClass):

    def append(self, page: PyMuPDFPage):

        flags = (
            #  If set, then images will be stored in the TextPage.
            #  This causes the presence of (usually large!) binary image content in the
            #  output of text extractions of types:
            #  “blocks”, “dict”, “json”, “rawdict”, “rawjson”, “html”, and “xhtml”
            #  and is the default there.
            #  If used with “blocks” however, only image metadata will be returned,
            #  not the image itself.
            pymupdf.TEXT_PRESERVE_IMAGES
            # | pymupdf.TEXT_COLLECT_VECTORS
            | pymupdf.TEXTFLAGS_BLOCKS
            | pymupdf.TEXT_DEHYPHENATE
            # | pymupdf.TEXTFLAGS_DICT
            | pymupdf.TEXT_COLLECT_STYLES
        )
        # Page level... May include TEXT AND IMAGES.
        # (x0, y0, x1, y1, "lines in the block", block_no, block_type)
        page_blocks: str = page.get_text("blocks", flags=flags, sort=True)

        # dict[str, str]
        for block in page_blocks:

            x0 = y0 = x1 = y1 = block_text = block_no = block_type = None
            x0, y0, x1, y1, block_text, block_no, block_type = block

            entry = (
                page.number,  # 1
                block_type,  # 2
                ({0: "TEXT", 1: "IMAGE"}.get(block_type, "UNKNOWN")),  # 3
                block_no,  # 4
                block_text,  # 5
                x0,  # 6
                y0,  # 7
                x1,  # 8
                y1,  # 9
            )
            self.data.append(entry)

        pass


# ------------------------------------------------------- PageBlockVersioned ---


class PageBlockVersioned(BaseClass):
    def persist_view(self, cfg: ConfigHandler):
        super().persist_view(cfg)
        #
        # I = cfg.logger.info
        # I(f"{self.__class__.__name__}.{sys._getframe(0).f_code.co_name} (instance)")
        # self.dbNm = cfg._stmt[self.__class__.__name__]["NAME"]
        # # insert_into = cfg._stmt[self.__class__.__name__]["DML"]["INSERT_INTO"]
        # obj = cfg._stmt[self.__class__.__name__]
        # dml = obj["DML"]
        # stmt = dml["INSERT_INTO"]

        # conn: DbConn = sqlite3.connect(self.dbNm)

        # conn.execute(stmt)
        # conn.commit()
        # conn.close()

        # conn = None

        pass

    pass


# ------------------------------------------------------ PageBlockTranslated ---


class PageBlockTranslated(BaseClass):
    def persist_view(self, cfg: ConfigHandler):
        super().persist_view(cfg)


# ------------------------------------------------------------ PageBlockFTS ---


class PageBlockFTS(BaseClass):
    def persist_view(self, cfg: ConfigHandler):
        super().persist_view(cfg)
        #
        I = cfg.logger.info
        I(f"{self.__class__.__name__}.{sys._getframe(0).f_code.co_name} (instance)")
        self.dbNm = cfg._stmt[self.__class__.__name__]["NAME"]
        # insert_into = cfg._stmt[self.__class__.__name__]["DML"]["INSERT_INTO"]
        obj = cfg._stmt[self.__class__.__name__]
        dml = obj["DML"]
        stmt = dml["INSERT_INTO"]

        conn: DbConn = sqlite3.connect(self.dbNm)

        conn.execute(stmt)
        conn.commit()
        conn.close()

        conn = None

        pass

    pass


# ---------------------------------------------------------------- PageDict ---


class PageDict(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_dict: dict = page.get_text("dict", sort=True)

        entry = (
            page.number,  # 1
            str(page_dict),  # 2
        )
        self.data.append(entry)

        pass


# ------------------------------------------------------------ PageDrawings ---


class PageDrawings(BaseClass):

    def append(self, page: PyMuPDFPage):

        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_drawings
        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_cdrawings
        page_cdrawings: str = page.get_cdrawings(extended=True)

        entry = (
            page.number,  # 1
            str(page_cdrawings),  # 2
        )
        self.data.append(entry)

        pass


# ---------------------------------------------------------------- PageFont ---


class PageFont(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        font_list = page.get_fonts(full=True)

        # (xref, ext, type, basefont, name, encoding, referencer)
        for font in font_list:

            xref = ext = type = basefont = name = encoding = referencer = None
            xref, ext, type, basefont, name, encoding, referencer = font

            entry = (
                page.number,
                xref,
                ext,
                type,
                basefont,
                name,
                encoding,
                (  # referencer, default to 0 if missing
                    referencer if len(font) > 6 else 0
                ),
            )
            self.data.append(entry)

        pass


# ------------------------------------------------------------ DocumentFont ---


class DocumentFont(BaseClass):
    pass


# ------------------------------------------------------ DocumentUniqueFont ---


class DocumentUniqueFont(BaseClass):
    pass


# ---------------------------------------------------------------- PageHtml ---


class PageHtml(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_html: str = page.get_text("html")

        entry = (
            page.number,  # 1
            page_html,  # 2
        )
        self.data.append(entry)

        pass


# --------------------------------------------------------------- PageImage ---


class PageImage(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Clean up the page contents to ensure accurate image extraction.
        if page.number > 0:
            page.clean_contents()

        # list[dict] = [
        #    (
        #       xref, smask, width, height, bpc,
        #       colorspace, alt_colorspace,
        #       name, filter, referencer
        #    )
        # ]
        img_list: str = page.get_images(full=True)
        for img_info in img_list:
            xref = img_info[0]  # image object number
            #
            xtract_img = page.parent.extract_image(xref)
            #
            ext_ = xtract_img.get("ext")  # image type/extension
            smask_ = xtract_img.get("smask")  # xref of soft-mask image
            width_ = xtract_img.get("width")  # image width
            height_ = xtract_img.get("height")  # image height
            colorspace_ = xtract_img.get("colorspace")  # colorspace number
            cs_name_ = xtract_img.get("cs-name")  # colorspace name
            xres_ = xtract_img.get("xres")  # x resolution
            yres_ = xtract_img.get("yres")  # y resolution
            image_data_ = xtract_img.get("image")  # image bytes
            smask = img_info[1]  # soft-mask image object number
            width = img_info[2]  # image width
            height = img_info[3]  # image height
            bpc = img_info[4]  # bits per component
            colorspace = img_info[5]  # colorspace name
            alt_colorspace = img_info[6]  # alternate colorspace
            name = img_info[7]  # symbolic image name
            filter = img_info[8]  # decode filter
            referencer = (
                img_info[9] if len(img_info) > 9 else None
            )  # xref of referencer
            entry = (
                page.number,  # PAGE_NUMBER
                xref,  # XREF
                smask,  # SMASK
                width,  # WIDTH
                height,  # HEIGHT
                bpc,  # BPC
                colorspace,  # COLORSPACE
                alt_colorspace,  # ALT_COLORSPACE
                name,  # NAME
                filter,  # FILTER
                referencer,  # REFERENCER
                ext_,  # EXT_
                smask_ if smask != smask_ else None,  # SMASK_
                width_ if width != width_ else None,  # WIDTH_
                height_ if height != height_ else None,  # HEIGHT_
                colorspace_ if colorspace != colorspace_ else None,  # COLORSPACE_
                cs_name_,  # CS_NAME_
                xres_,  # XRES_
                yres_,  # YRES_
                image_data_,  # IMAGE_
            )

            self.data.append(entry)

        pass


# ----------------------------------------------------------- PageImageInfo ---


class PageImageInfo(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Clean up the page contents to ensure accurate image extraction.
        page.clean_contents()
        img_info_list: str = page.get_image_info(hashes=True, xrefs=False)
        for img_info in img_info_list:
            digest_bytes = img_info.get("digest")
            digest_hex = digest_bytes.hex() if digest_bytes is not None else None
            entry = (
                page.number,
                img_info.get("number"),  # BLOCK_NUMBER
                str(img_info.get("bbox")),  # BBOX
                img_info.get("width"),  # WIDTH
                img_info.get("height"),  # HEIGHT
                img_info.get("cs-name"),  # CS_NAME
                img_info.get("colorspace"),  # COLORSPACE
                img_info.get("xres"),  # XRES
                img_info.get("yres"),  # YRES
                img_info.get("bpc"),  # BPC
                img_info.get("size"),  # SIZE
                digest_hex,  # DIGEST as hex string
                img_info.get("xref"),  # XREF
                str(img_info.get("transform")),  # TRANSFORM
                img_info.get("has-mask"),  # HAS_MASK
            )
            self.data.append(entry)

        pass


# ---------------------------------------------------------------- PageJson ---


class PageJson(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_json: dict = page.get_text("json", sort=True)

        entry = (
            page.number,  # 1
            str(page_json),  # 2
        )
        self.data.append(entry)

        pass


# ---------------------------------------------------------------- PageLink ---


class PageLink(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[dict[str, str]]
        page_links = page.get_links()

        # dict[str, str]
        for page_link in page_links:

            # Point|str or None
            to_page = page_link.get("to", None)
            to_page = str(to_page) if to_page is not None else None

            page_link_kind_dest_code = page_link["kind"]
            page_link_kind_dest_name = {
                0: "LINK_NONE",
                1: "LINK_GOTO",
                2: "LINK_URI",
                3: "LINK_LAUNCH",
                4: "LINK_NAMED",
                5: "LINK_GOTOR",
            }.get(page_link_kind_dest_code, "unknown")

            entry = (
                page.number,  # 01 : type: int
                page_link["id"] if "id" in page_link else None,
                page_link_kind_dest_code,  # 03 : type int
                page_link_kind_dest_name,  # 04 : type str
                str("from"),  # 05 : type Rect
                page_link.get("page", None),  # 06 : type int or None
                to_page,  # 07 : type Point|str or None
                page_link.get("file", None),  # 08 : type str or None
                page_link.get("uri", None),  # 09 : type str or None
                page_link["xref"],  # 10 : type int
            )
            self.data.append(entry)

        pass


# ------------------------------------------------------------ DocumentLink ---


class DocumentLink(BaseClass):
    pass


# ------------------------------------------------------ PagePhysical2Label ---


class PagePhysical2Label(BaseClass):

    def append(self, page: PyMuPDFPage):

        entry = (page.number, page.get_label())
        self.data.append(entry)

        pass


# -------------------------------------------------------------- PagePixmap ---


class PagePixmap(BaseClass):

    def append(self, page: PyMuPDFPage):

        # https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_pixmap

        """
        Pass the format name as a string to tobytes(format):

        Format	Lossless	Notes
        "png"	Yes	Default, good quality, larger size.
        "jpeg"	No	Compressed, smaller size, configurable quality (via pix.save options).
        "jpg"	No	Alias for "jpeg".
        "bmp"	Yes	Uncompressed, very large size, rarely used.
        "ppm"	Yes	Portable Pixmap format, uncompressed.
        "pgm"	Yes	Grayscale only.
        "pbm"	Yes	Binary monochrome only.

        Recommendation for SQLite
        Use "jpeg" if image quality is less critical than storage size, or "png" if
        transparency/lossless quality is required. Note that storing images directly in SQLite
        is generally discouraged for performance reasons; consider storing paths to files on
        disk instead.
        """
        format = "jpeg"

        # pymupdf.csGRAY, pymupdf.csCMYK, pymupdf.csRGB, pymupdf.csLAB, pymupdf.csYCCK
        colorspace = pymupdf.csRGB

        page_pixmap: bytes = page.get_pixmap(
            alpha=False, matrix=pymupdf.Identity, colorspace=colorspace
        ).tobytes(format)

        entry = (
            page.number,  # 1
            str(pymupdf.Identity),  # 2
            page_pixmap,  # 3
        )
        self.data.append(entry)

        pass


# ------------------------------------------------------------- PageRawDict ---


class PageRawDict(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_rawdict: dict = page.get_text("rawdict", sort=True)

        entry = (
            page.number,  # 1
            str(page_rawdict),  # 2
        )
        self.data.append(entry)

        pass


# ------------------------------------------------------------- PageRawJson ---


class PageRawJson(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_rawjson: dict = page.get_text("rawjson", sort=True)

        entry = (
            page.number,  # 1
            str(page_rawjson),  # 2
        )
        self.data.append(entry)

        pass


# ----------------------------------------------------------------- PageSvg ---


class PageSvg(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_svg: str = page.get_svg_image(text_as_path=False)

        entry = (
            page.number,  # 1
            page_svg,  # 2
        )
        self.data.append(entry)

        pass


# ------------------------------------------------------- PageSvgTextAsPath ---


class PageSvgTextAsPath(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_svg_textaspath: str = page.get_svg_image(text_as_path=True)

        entry = (
            page.number,  # 1
            page_svg_textaspath,  # 2
        )
        self.data.append(entry)

        pass


# --------------------------------------------------------------- PageTable ---


class PageTable(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # Get the rectangle bounding the table
            x0, y0, x1, y1 = table.bbox
            # PANDAS
            entry = (
                page.number,
                idx,
                table.header.external,  # 0 or 1
                x0,
                y0,
                x1,
                y1,
            )
            self.data.append(entry)

        pass


# ------------------------------------------------------------ PageTableCsv ---


class PageTableCsv(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # PANDAS
            to_pandas: DataFrame = table.to_pandas()
            to_csv = to_pandas.to_csv(index=True)
            entry = (
                page.number,
                idx,
                to_csv,
            )
            self.data.append(entry)

        pass


# ----------------------------------------------------------- PageTableHtml ---


class PageTableHtml(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # PANDAS
            to_pandas: DataFrame = table.to_pandas()
            to_html = to_pandas.to_html()
            entry = (
                page.number,
                idx,
                to_html,
            )
            self.data.append(entry)

        pass


# ----------------------------------------------------------- PageTableJson ---


class PageTableJson(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # PANDAS
            to_pandas: DataFrame = table.to_pandas()
            to_json: str = to_pandas.to_json()
            entry = (
                page.number,
                idx,
                to_json,
            )
            self.data.append(entry)

        pass


# ----------------------------------------------------------- PageTableList ---


class PageTableList(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            to_extract = table.extract()
            entry = (
                page.number,
                idx,
                str(to_extract),
            )
            self.data.append(entry)

        pass


# ------------------------------------------------------- PageTableMarkdown ---


class PageTableMarkdown(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # PANDAS
            to_pandas: DataFrame = table.to_pandas()
            to_markdown = to_pandas.to_markdown()
            entry = (
                page.number,
                idx,
                to_markdown,
            )
            self.data.append(entry)

        pass


# ------------------------------------------------------- PageTableSql ---


class PageTableSql(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # PANDAS
            to_pandas: DataFrame = table.to_pandas()

            drop_sql = create_sql = insert_sqls = select_sql = view_sql = None

            drop_sql, create_sql, insert_sqls, select_sql, view_sql = (
                PandasToSqliteOffline.generate_sql(
                    df=to_pandas,
                    table_name=f"T-P{page.number:04}-#{idx:03d}",
                    include_index=True,
                )
            )
            entry = (
                page.number,
                idx,
                drop_sql,
                create_sql,
                str(insert_sqls),
                select_sql,
                view_sql,
            )
            self.data.append(entry)

        pass


# --------------------------------------------------------- PageTablePixMap ---


class PageTablePixMap(BaseClass):

    def append(self, page: PyMuPDFPage):

        # list[ (xref, ext, type, basefont, name, encoding, referencer) ]
        tableList: TableFinder = page.find_tables()
        # Extract tables as pandas DataFrames
        table: Table = None

        for idx, table in enumerate(tableList):
            # Get the rectangle bounding the table
            x0, y0, x1, y1 = table.bbox
            # Transform by zoom factor
            clip = Rect(x0, y0, x1, y1)  # use table's rect
            # Render page to a Pixmap, clipped to table rect
            pix = page.get_pixmap(matrix=self.mat, clip=clip)

            entry = (
                page.number,
                idx,
                pix.tobytes(),  # BLOB
            )
            self.data.append(entry)

        pass


# ---------------------------------------------------------------- PageText ---


class PageText(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_text: str = page.get_text("text", sort=True)

        entry = (
            page.number,  # 1
            page_text,  # 2
        )
        self.data.append(entry)

        pass


# ---------------------------------------------------------------- PageWord ---


class PageWord(BaseClass):

    STOPWORDS = {
        "i",
        "me",
        "my",
        "myself",
        "we",
        "our",
        "ours",
        "ourselves",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "he",
        "him",
        "his",
        "himself",
        "she",
        "her",
        "hers",
        "herself",
        "it",
        "its",
        "itself",
        "they",
        "them",
        "their",
        "theirs",
        "themselves",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "am",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "having",
        "do",
        "does",
        "did",
        "doing",
        "a",
        "an",
        "the",
        "and",
        "but",
        "if",
        "or",
        "because",
        "as",
        "until",
        "while",
        "of",
        "at",
        "by",
        "for",
        "with",
        "about",
        "against",
        "between",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "to",
        "from",
        "up",
        "down",
        "in",
        "out",
        "on",
        "off",
        "over",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "s",
        "t",
        "can",
        "will",
        "just",
        "don",
        "should",
        "now",
    }
    # STOPWORDS = set(stopwords.words("english"))

    def append(self, page: PyMuPDFPage):

        # (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        words = page.get_text("words", sort=True)

        for word in words:
            x0 = y0 = x1 = y1 = wrd = block_no = line_no = word_no = None
            x0, y0, x1, y1, wrd, block_no, line_no, word_no = word
            # Keep only alphanumeric characters in each string
            alphanum = re.sub(r"[^a-zA-Z0-9]", "", wrd)

            # ipa_repr = ipa_repr_str = None
            # ipa_repr = ipa.ipa_list(wrd)
            # ipa_repr_str = str(ipa_repr)

            entry = (
                page.number,
                block_no,
                line_no,
                word_no,
                wrd,
                alphanum,
                alphanum.lower().strip() in self.STOPWORDS,
                x0,
                y0,
                x1,
                y1,
            )

            self.data.append(entry)

        pass


# --------------------------------------------------- DocumentWordFrequency ---


class DocumentWordFrequency(BaseClass):
    pass


# ------------------------------------------------------- PageWordFrequency ---


class PageWordFrequency(BaseClass):
    pass


# --------------------------------------------------------------- PageXHtml ---


class PageXHtml(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_xhtml: str = page.get_text("xhtml")

        entry = (
            page.number,  # 1
            page_xhtml,  # 2
        )
        self.data.append(entry)

        pass


# ----------------------------------------------------------------- PageXml ---


class PageXml(BaseClass):

    def append(self, page: PyMuPDFPage):

        # Page level... May include TEXT AND IMAGES.
        page_xml: str = page.get_text("xml")

        entry = (
            page.number,  # 1
            page_xml,  # 2
        )
        self.data.append(entry)

        pass


# -------------------------------------------------------------------- MAIN ---


def main():
    logger.info("Starting PDF Extraction Tool")

    try:
        cfg = ConfigHandler(logger)
        cfg.print()

        I = cfg.logger.info

        I(f"Opening PDF: {cfg.InputPdf}")

        with pymupdf.open(cfg.InputPdf) as doc:
            with DocumentInfo(cfg) as di:
                di.append(doc)
                di.persist(cfg)
                pass
            with DocumentPageLabel(cfg) as dpl:
                dpl.append(doc)
                dpl.persist(cfg)
                pass
            with DocumentToC(cfg) as dtoc:
                dtoc.append(doc)
                dtoc.persist(cfg)
                pass
            with DocumentEmbeddedFileInfo(cfg) as dei:
                dei.append(doc)
                dei.persist(cfg)
                pass
            # with DocumentEmbeddedFile(cfg) as defile:
            #     defile.append(doc)
            #     defile.persist(cfg)
            #     pass
            #
            pa = PageAnnotation(cfg)
            pb = PageBlock(cfg)
            pdict = PageDict(cfg)
            pdrawings = PageDrawings(cfg)
            pf = PageFont(cfg)
            ph = PageHtml(cfg)
            pi = PageImage(cfg)
            pii = PageImageInfo(cfg)
            pjson = PageJson(cfg)
            pl = PageLink(cfg)
            pp2l = PagePhysical2Label(cfg)
            ppmap = PagePixmap(cfg)
            prdict = PageRawDict(cfg)
            prjson = PageRawJson(cfg)
            psvg = PageSvg(cfg)
            psvgtap = PageSvgTextAsPath(cfg)
            #
            pt = PageTable(cfg)
            ptcsv = PageTableCsv(cfg)
            pthtml = PageTableHtml(cfg)
            ptjson = PageTableJson(cfg)
            ptlist = PageTableList(cfg)
            ptmdwn = PageTableMarkdown(cfg)
            ptpix = PageTablePixMap(cfg)
            ptsql = PageTableSql(cfg)
            #
            ptxt = PageText(cfg)
            pw = PageWord(cfg)
            pxh = PageXHtml(cfg)
            px = PageXml(cfg)

            for page in doc:
                I(f"Page #{page.number}/{doc.page_count}...")
                cfg.PageAnnotation and pa.append(page)
                cfg.PageBlock and pb.append(page)
                cfg.PageDict and pdict.append(page)
                cfg.PageDrawings and pdrawings.append(page)
                cfg.PageFont and pf.append(page)
                cfg.PageHtml and ph.append(page)
                cfg.PageImage and pi.append(page)
                cfg.PageImageInfo and pii.append(page)
                cfg.PageJson and pjson.append(page)
                cfg.PageLink and pl.append(page)
                cfg.PagePhysical2Label and pp2l.append(page)
                cfg.PagePixmap and ppmap.append(page)
                cfg.PageRawDict and prdict.append(page)
                cfg.PageRawJson and prjson.append(page)
                cfg.PageSvg and psvg.append(page)
                cfg.PageSvgTextAsPath and psvgtap.append(page)
                #
                cfg.PageTable and pt.append(page)
                cfg.PageTableCsv and ptcsv.append(page)
                cfg.PageTableHtml and pthtml.append(page)
                cfg.PageTableJson and ptjson.append(page)
                cfg.PageTableList and ptlist.append(page)
                cfg.PageTableMarkdown and ptmdwn.append(page)
                cfg.PageTablePixMap and ptpix.append(page)
                cfg.PageTableSql and ptsql.append(page)
                #
                cfg.PageText and ptxt.append(page)
                cfg.PageWord and pw.append(page)
                cfg.PageXHtml and pxh.append(page)
                cfg.PageXml and px.append(page)
                pass

            cfg.PageAnnotation and pa.persist(cfg)
            cfg.PageBlock and pb.persist(cfg)
            cfg.PageDict and pdict.persist(cfg)
            cfg.PageDrawings and pdrawings.persist(cfg)
            cfg.PageFont and pf.persist(cfg)
            cfg.PageHtml and ph.persist(cfg)
            cfg.PageImage and pi.persist(cfg)
            cfg.PageImageInfo and pii.persist(cfg)
            cfg.PageJson and pjson.persist(cfg)
            cfg.PageLink and pl.persist(cfg)
            cfg.PagePhysical2Label and pp2l.persist(cfg)
            cfg.PagePixmap and ppmap.persist(cfg)
            cfg.PageRawDict and prdict.persist(cfg)
            cfg.PageRawJson and prjson.persist(cfg)
            cfg.PageSvg and psvg.persist(cfg)
            cfg.PageSvgTextAsPath and psvgtap.persist(cfg)
            #
            cfg.PageTable and pt.persist(cfg)
            cfg.PageTableCsv and ptcsv.persist(cfg)
            cfg.PageTableHtml and pthtml.persist(cfg)
            cfg.PageTableJson and ptjson.persist(cfg)
            cfg.PageTableList and ptlist.persist(cfg)
            cfg.PageTableMarkdown and ptmdwn.persist(cfg)
            cfg.PageTablePixMap and ptpix.persist(cfg)
            cfg.PageTableSql and ptsql.persist(cfg)
            #
            cfg.PageText and ptxt.persist(cfg)
            cfg.PageWord and pw.persist(cfg)
            cfg.PageXHtml and pxh.persist(cfg)
            cfg.PageXml and px.persist(cfg)

            if cfg.PageBlockFTS:
                pbFts = PageBlockFTS(cfg)
                pbFts.persist_view(cfg)

            if cfg.PageBlockVersioned:
                pbVer = PageBlockVersioned(cfg)
                pbVer.persist_view(cfg)

            if cfg.PageBlockTranslated:
                pbTrans = PageBlockTranslated(cfg)
                pbTrans.persist_view(cfg)

            if cfg.DocumentFont:
                df = DocumentFont(cfg)
                df.persist_view(cfg)
                duf = DocumentUniqueFont(cfg)
                duf.persist_view(cfg)

            if cfg.DocumentLink:
                dl = DocumentLink(cfg)
                dl.persist_view(cfg)

            if cfg.DocumentWordFrequency:
                dwf = DocumentWordFrequency(cfg)
                dwf.persist_view(cfg)
                pwf = PageWordFrequency(cfg)
                pwf.persist_view(cfg)

        logger.info("Extraction completed successfully.")
        flush_logger(logger)

        pass

    except Exception as e:
        logger.exception(f"Fatal error during extraction: {e}")
        sys.exit(1)

    pass


# -------------------------------------------------------- MAIN ENTRY-POINT ---

if __name__ == "__main__":
    main()

pass
