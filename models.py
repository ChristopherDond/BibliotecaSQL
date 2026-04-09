from dataclasses import dataclass


@dataclass(slots=True)
class Livro:
    id: int
    titulo: str
    autor: str
    ano: int | None
    disponivel: bool
    criado_em: str | None = None
    atualizado_em: str | None = None

    @property
    def status(self) -> str:
        return "Disponivel" if self.disponivel else "Emprestado"
