CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL CHECK (length(trim(titulo)) > 0),
    autor TEXT NOT NULL CHECK (length(trim(autor)) > 0),
    ano INTEGER CHECK (ano IS NULL OR ano BETWEEN 1450 AND 2100),
    disponivel INTEGER NOT NULL DEFAULT 1 CHECK (disponivel IN (0, 1)),
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_livros_titulo ON livros (titulo);
CREATE INDEX IF NOT EXISTS idx_livros_autor ON livros (autor);
