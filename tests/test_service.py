from pathlib import Path

import pytest

from database import Database
from services import BibliotecaService


def criar_service_temporario(tmp_path: Path) -> BibliotecaService:
    db = Database(db_path=tmp_path / "service.db")
    return BibliotecaService(db)


def test_service_emprestar_e_devolver(tmp_path: Path):
    service = criar_service_temporario(tmp_path)

    service.adicionar_livro("Python Fluente", "Luciano Ramalho", 2015)
    livro = service.listar_livros()[0]

    service.marcar_emprestado(livro.id)
    emprestado = service.obter_livro(livro.id)
    assert emprestado is not None
    assert not emprestado.disponivel

    service.marcar_devolvido(livro.id)
    devolvido = service.obter_livro(livro.id)
    assert devolvido is not None
    assert devolvido.disponivel


def test_service_bloqueia_emprestimo_repetido(tmp_path: Path):
    service = criar_service_temporario(tmp_path)

    service.adicionar_livro("DDD", "Eric Evans", 2003)
    livro = service.listar_livros()[0]

    service.marcar_emprestado(livro.id)
    with pytest.raises(ValueError, match="ja esta emprestado"):
        service.marcar_emprestado(livro.id)


def test_service_valida_campos(tmp_path: Path):
    service = criar_service_temporario(tmp_path)

    with pytest.raises(ValueError, match="obrigatorios"):
        service.adicionar_livro("", "Autor", 2000)

    with pytest.raises(ValueError, match="ao menos 2 caracteres"):
        service.adicionar_livro("A", "B", 2000)
