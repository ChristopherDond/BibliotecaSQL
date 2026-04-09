from pathlib import Path

from database import Database


def criar_db_temporario(tmp_path: Path) -> Database:
    return Database(db_path=tmp_path / "test.db")


def test_adicionar_e_listar_livro(tmp_path: Path):
    db = criar_db_temporario(tmp_path)

    db.adicionar_livro("Clean Code", "Robert C. Martin", 2008)
    livros = db.listar_livros()

    assert len(livros) == 1
    assert livros[0]["titulo"] == "Clean Code"
    assert livros[0]["autor"] == "Robert C. Martin"
    assert livros[0]["ano"] == 2008
    assert livros[0]["disponivel"] == 1


def test_filtrar_por_termo_e_status(tmp_path: Path):
    db = criar_db_temporario(tmp_path)

    db.adicionar_livro("Dom Casmurro", "Machado de Assis", 1899)
    db.adicionar_livro("Clean Architecture", "Robert C. Martin", 2017)
    livros = db.listar_livros(termo="clean", disponivel=1, ordenar_por="titulo", ordem="ASC")

    assert len(livros) == 1
    assert livros[0]["titulo"] == "Clean Architecture"


def test_atualizar_livro_e_disponibilidade(tmp_path: Path):
    db = criar_db_temporario(tmp_path)

    db.adicionar_livro("Refactoring", "Martin Fowler", 1999)
    livro = db.listar_livros()[0]

    db.atualizar_livro(livro["id"], "Refactoring 2nd", "Martin Fowler", 2018)
    db.atualizar_disponibilidade(livro["id"], 0)

    atualizado = db.obter_livro(livro["id"])
    assert atualizado is not None
    assert atualizado["titulo"] == "Refactoring 2nd"
    assert atualizado["ano"] == 2018
    assert atualizado["disponivel"] == 0
