# Sistema de Biblioteca (PyQt + SQL)

Projeto simples de biblioteca com:
- Interface grafica em PyQt6
- Banco de dados SQLite
- Script SQL para criar a tabela

## Funcionalidades
- Adicionar livro
- Listar livros
- Marcar livro como emprestado
- Marcar livro como devolvido
- Remover livro

## Estrutura
- `main.py`: interface grafica
- `database.py`: conexao e operacoes no banco
- `schema.sql`: criacao das tabelas
- `biblioteca.db`: banco SQLite gerado automaticamente ao executar

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
