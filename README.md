# Library System (PyQt + SQL)

**[Versão em Português](README-pt-br.md)**

A simple library management system with:
- Graphical interface in PyQt6
- SQLite database
- SQL script to create the table
- Database integrity rules (constraints)
- Versioned migrations via `PRAGMA user_version`

## Features
- Add book
- Edit book
- List books
- Mark book as borrowed
- Mark book as returned
- Remove book
- Search books by title/author
- Filter by status (all, available, borrowed)
- Sort columns in the table

## Database rules (phase 2)
- `titulo` and `autor` cannot be empty
- `ano` must be `NULL` or between `1450` and `2100`
- `disponivel` only accepts `0` or `1`
- Audit columns: `criado_em` and `atualizado_em`
- Indexes on `titulo` and `autor`

## Structure
- `main.py`: graphical interface
- `database.py`: connection, schema and migrations
- `services.py`: business rules
- `models.py`: domain model (`Livro`)
- `schema.sql`: table creation
- `biblioteca.db`: SQLite database generated automatically on execution
- `tests/`: unit and integration tests
- `.github/workflows/ci.yml`: lint + test pipeline

## How to run
1. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the system:
   ```bash
   python main.py
   ```

On start, the system creates the `biblioteca.db` file automatically and applies `schema.sql`.

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