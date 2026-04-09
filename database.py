import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "biblioteca.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
SCHEMA_VERSION = 2


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_database(self):
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Arquivo de schema nao encontrado: {SCHEMA_PATH}")

        with self._get_connection() as conn:
            self._apply_schema(conn)
            self._run_migrations(conn)
            conn.commit()

    def _apply_schema(self, conn: sqlite3.Connection):
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema_sql)

    def _table_columns(self, conn: sqlite3.Connection, table_name: str) -> set[str]:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        return {row["name"] for row in cursor.fetchall()}

    def _get_user_version(self, conn: sqlite3.Connection) -> int:
        cursor = conn.execute("PRAGMA user_version")
        return int(cursor.fetchone()[0])

    def _set_user_version(self, conn: sqlite3.Connection, version: int):
        conn.execute(f"PRAGMA user_version = {version}")

    def _run_migrations(self, conn: sqlite3.Connection):
        current_version = self._get_user_version(conn)

        if current_version < 1:
            self._migration_v1_add_auditoria_e_indices(conn)
            self._set_user_version(conn, 1)
            current_version = 1

        if current_version < 2:
            self._migration_v2_rebuild_constraints(conn)
            self._set_user_version(conn, 2)
            current_version = 2

        if current_version < SCHEMA_VERSION:
            self._set_user_version(conn, SCHEMA_VERSION)

    def _migration_v1_add_auditoria_e_indices(self, conn: sqlite3.Connection):
        columns = self._table_columns(conn, "livros")

        if "atualizado_em" not in columns:
            conn.execute(
                "ALTER TABLE livros ADD COLUMN atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP"
            )

        conn.execute("CREATE INDEX IF NOT EXISTS idx_livros_titulo ON livros (titulo)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_livros_autor ON livros (autor)")

    def _migration_v2_rebuild_constraints(self, conn: sqlite3.Connection):
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'livros'"
        )
        row = cursor.fetchone()
        if row is None or row["sql"] is None:
            return

        table_sql = row["sql"].lower()
        has_constraints = all(
            token in table_sql
            for token in (
                "length(trim(titulo)) > 0",
                "length(trim(autor)) > 0",
                "ano between 1450 and 2100",
                "disponivel in (0, 1)",
            )
        )

        if has_constraints:
            return

        columns = self._table_columns(conn, "livros")
        has_updated_at = "atualizado_em" in columns

        conn.execute("ALTER TABLE livros RENAME TO livros_legacy")
        self._apply_schema(conn)

        if has_updated_at:
            conn.execute(
                """
                INSERT INTO livros (id, titulo, autor, ano, disponivel, criado_em, atualizado_em)
                SELECT
                    id,
                    trim(titulo),
                    trim(autor),
                    CASE WHEN ano BETWEEN 1450 AND 2100 THEN ano ELSE NULL END,
                    CASE WHEN disponivel = 0 THEN 0 ELSE 1 END,
                    COALESCE(criado_em, CURRENT_TIMESTAMP),
                    COALESCE(atualizado_em, criado_em, CURRENT_TIMESTAMP)
                FROM livros_legacy
                WHERE length(trim(COALESCE(titulo, ''))) > 0
                  AND length(trim(COALESCE(autor, ''))) > 0
                """
            )
        else:
            conn.execute(
                """
                INSERT INTO livros (id, titulo, autor, ano, disponivel, criado_em, atualizado_em)
                SELECT
                    id,
                    trim(titulo),
                    trim(autor),
                    CASE WHEN ano BETWEEN 1450 AND 2100 THEN ano ELSE NULL END,
                    CASE WHEN disponivel = 0 THEN 0 ELSE 1 END,
                    COALESCE(criado_em, CURRENT_TIMESTAMP),
                    COALESCE(criado_em, CURRENT_TIMESTAMP)
                FROM livros_legacy
                WHERE length(trim(COALESCE(titulo, ''))) > 0
                  AND length(trim(COALESCE(autor, ''))) > 0
                """
            )

        conn.execute("DROP TABLE livros_legacy")

    def adicionar_livro(self, titulo: str, autor: str, ano: int | None):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO livros (titulo, autor, ano) VALUES (?, ?, ?)",
                (titulo.strip(), autor.strip(), ano),
            )
            conn.commit()

    def listar_livros(self):
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, titulo, autor, ano, disponivel FROM livros ORDER BY id DESC"
            )
            return cursor.fetchall()

    def atualizar_disponibilidade(self, livro_id: int, disponivel: int):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE livros SET disponivel = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                (disponivel, livro_id),
            )
            conn.commit()

    def remover_livro(self, livro_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
            conn.commit()
