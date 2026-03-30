import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "biblioteca.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


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
            schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
            conn.executescript(schema_sql)
            conn.commit()

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
                "UPDATE livros SET disponivel = ? WHERE id = ?",
                (disponivel, livro_id),
            )
            conn.commit()

    def remover_livro(self, livro_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM livros WHERE id = ?", (livro_id,))
            conn.commit()
