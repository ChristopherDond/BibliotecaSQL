# Sistema de Biblioteca (PyQt + SQL)

**[English Version](README.md)**

Projeto simples de biblioteca com:
- Interface grafica em PyQt6
- Banco de dados SQLite
- Script SQL para criar a tabela
- Regras de integridade no banco (constraints)
- Migracoes versionadas via PRAGMA user_version

## Funcionalidades
- Adicionar livro
- Listar livros
- Marcar livro como emprestado
- Marcar livro como devolvido
- Remover livro

## Regras de banco (fase 2)
- `titulo` e `autor` nao podem ser vazios
- `ano` deve ser `NULL` ou entre `1450` e `2100`
- `disponivel` so aceita `0` ou `1`
- Colunas de auditoria: `criado_em` e `atualizado_em`
- Indices em `titulo` e `autor`

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
