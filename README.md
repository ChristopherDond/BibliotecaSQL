# Sistema de Biblioteca (PyQt + SQL)

**[Versão em Português](README.pt-BR.md)**

Projeto simples de biblioteca com:
- Interface grafica em PyQt6
- Banco de dados SQLite
- Script SQL para criar a tabela
- Regras de integridade no banco (constraints)
- Migracoes versionadas via PRAGMA user_version

## Funcionalidades
- Adicionar livro
- Editar livro
- Listar livros
- Marcar livro como emprestado
- Marcar livro como devolvido
- Remover livro
- Buscar livros por titulo/autor
- Filtrar por status (todos, disponiveis, emprestados)
- Ordenar colunas na tabela

## Regras de banco (fase 2)
- `titulo` e `autor` nao podem ser vazios
- `ano` deve ser `NULL` ou entre `1450` e `2100`
- `disponivel` so aceita `0` ou `1`
- Colunas de auditoria: `criado_em` e `atualizado_em`
- Indices em `titulo` e `autor`

## Estrutura
- `main.py`: interface grafica
- `database.py`: conexao, schema e migracoes
- `services.py`: regras de negocio
- `models.py`: modelo de dominio (`Livro`)
- `schema.sql`: criacao das tabelas
- `biblioteca.db`: banco SQLite gerado automaticamente ao executar
- `tests/`: testes unitarios e de integracao
- `.github/workflows/ci.yml`: pipeline de lint + testes

## Como rodar
1. Instale as dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o sistema:
   ```bash
   python main.py
   ```

Ao iniciar, o sistema cria o arquivo `biblioteca.db` automaticamente e aplica o `schema.sql`.

## Quality and tests (phase 5)
1. Install development dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   ```
2. Run lint:
   ```bash
   ruff check .
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Packaging
To generate a local executable:
```bash
pyinstaller --onefile --windowed --name BibliotecaSQL main.py
```
