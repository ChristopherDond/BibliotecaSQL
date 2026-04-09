from datetime import date

from database import Database
from models import Livro


class BibliotecaService:
    def __init__(self, database: Database):
        self.database = database
        self.ano_atual = date.today().year

    def validar_livro(self, titulo: str, autor: str, ano: int | None):
        if not titulo or not autor:
            raise ValueError("Titulo e autor sao obrigatorios.")

        if len(titulo) < 2 or len(autor) < 2:
            raise ValueError("Titulo e autor devem ter ao menos 2 caracteres.")

        if len(titulo) > 120 or len(autor) > 120:
            raise ValueError("Titulo e autor devem ter no maximo 120 caracteres.")

        if ano is not None and (ano < 1450 or ano > self.ano_atual):
            raise ValueError(f"Ano invalido. Informe entre 1450 e {self.ano_atual}.")

    def _para_livro(self, row) -> Livro:
        return Livro(
            id=int(row["id"]),
            titulo=row["titulo"],
            autor=row["autor"],
            ano=row["ano"],
            disponivel=bool(row["disponivel"]),
            criado_em=row["criado_em"],
            atualizado_em=row["atualizado_em"],
        )

    def listar_livros(
        self,
        termo: str = "",
        filtro_status: str = "todos",
        ordenar_por: str = "id",
        ordem: str = "DESC",
    ) -> list[Livro]:
        mapa_status = {
            "todos": None,
            "disponivel": 1,
            "emprestado": 0,
        }
        disponivel = mapa_status.get(filtro_status, None)

        rows = self.database.listar_livros(
            termo=termo,
            disponivel=disponivel,
            ordenar_por=ordenar_por,
            ordem=ordem,
        )
        return [self._para_livro(row) for row in rows]

    def adicionar_livro(self, titulo: str, autor: str, ano: int | None):
        self.validar_livro(titulo, autor, ano)
        self.database.adicionar_livro(titulo, autor, ano)

    def editar_livro(self, livro_id: int, titulo: str, autor: str, ano: int | None):
        self.validar_livro(titulo, autor, ano)
        livro = self.obter_livro(livro_id)
        if livro is None:
            raise ValueError("Livro nao encontrado.")
        self.database.atualizar_livro(livro_id, titulo, autor, ano)

    def obter_livro(self, livro_id: int) -> Livro | None:
        row = self.database.obter_livro(livro_id)
        return None if row is None else self._para_livro(row)

    def marcar_emprestado(self, livro_id: int):
        livro = self.obter_livro(livro_id)
        if livro is None:
            raise ValueError("Livro nao encontrado.")
        if not livro.disponivel:
            raise ValueError("O livro selecionado ja esta emprestado.")
        self.database.atualizar_disponibilidade(livro_id, 0)

    def marcar_devolvido(self, livro_id: int):
        livro = self.obter_livro(livro_id)
        if livro is None:
            raise ValueError("Livro nao encontrado.")
        if livro.disponivel:
            raise ValueError("O livro selecionado ja esta disponivel.")
        self.database.atualizar_disponibilidade(livro_id, 1)

    def remover_livro(self, livro_id: int):
        livro = self.obter_livro(livro_id)
        if livro is None:
            raise ValueError("Livro nao encontrado.")
        self.database.remover_livro(livro_id)
