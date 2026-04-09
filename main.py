import sys
from datetime import date

from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import Database


class BibliotecaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Biblioteca")
        self.resize(760, 500)
        self.ano_atual = date.today().year

        self.db = Database()
        self._setup_ui()
        self.carregar_livros()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout_principal = QVBoxLayout(central)

        # Formulario de cadastro
        formulario = QFormLayout()

        self.input_titulo = QLineEdit()
        self.input_titulo.setPlaceholderText("Ex: Clean Code")

        self.input_autor = QLineEdit()
        self.input_autor.setPlaceholderText("Ex: Robert C. Martin")

        self.input_ano = QSpinBox()
        self.input_ano.setRange(0, self.ano_atual)
        self.input_ano.setSpecialValueText("Sem ano")

        formulario.addRow("Titulo:", self.input_titulo)
        formulario.addRow("Autor:", self.input_autor)
        formulario.addRow("Ano:", self.input_ano)

        layout_principal.addLayout(formulario)

        botoes_topo = QHBoxLayout()

        self.btn_adicionar = QPushButton("Adicionar livro")
        self.btn_adicionar.clicked.connect(self.adicionar_livro)

        self.btn_atualizar = QPushButton("Atualizar lista")
        self.btn_atualizar.clicked.connect(self.carregar_livros)

        botoes_topo.addWidget(self.btn_adicionar)
        botoes_topo.addWidget(self.btn_atualizar)
        layout_principal.addLayout(botoes_topo)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Titulo", "Autor", "Ano", "Status"])
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setStretchLastSection(True)

        layout_principal.addWidget(QLabel("Livros cadastrados:"))
        layout_principal.addWidget(self.tabela)

        botoes_acao = QHBoxLayout()

        self.btn_emprestar = QPushButton("Marcar emprestado")
        self.btn_emprestar.clicked.connect(self.marcar_emprestado)

        self.btn_devolver = QPushButton("Marcar devolvido")
        self.btn_devolver.clicked.connect(self.marcar_devolvido)

        self.btn_remover = QPushButton("Remover livro")
        self.btn_remover.clicked.connect(self.remover_livro)

        botoes_acao.addWidget(self.btn_emprestar)
        botoes_acao.addWidget(self.btn_devolver)
        botoes_acao.addWidget(self.btn_remover)
        layout_principal.addLayout(botoes_acao)

    def _notificar(self, mensagem: str):
        self.statusBar().showMessage(mensagem, 4000)

    def _livro_selecionado_id(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Atencao", "Selecione um livro na tabela.")
            return None

        item_id = self.tabela.item(linha, 0)
        if item_id is None:
            return None

        return int(item_id.text())

    def _livro_selecionado_status(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            return None

        item_status = self.tabela.item(linha, 4)
        return None if item_status is None else item_status.text()

    def _validar_formulario(self, titulo: str, autor: str, ano: int | None):
        if not titulo or not autor:
            QMessageBox.warning(self, "Validacao", "Titulo e autor sao obrigatorios.")
            return False

        if len(titulo) < 2 or len(autor) < 2:
            QMessageBox.warning(self, "Validacao", "Titulo e autor devem ter ao menos 2 caracteres.")
            return False

        if len(titulo) > 120 or len(autor) > 120:
            QMessageBox.warning(self, "Validacao", "Titulo e autor devem ter no maximo 120 caracteres.")
            return False

        if ano is not None and (ano < 1450 or ano > self.ano_atual):
            QMessageBox.warning(
                self,
                "Validacao",
                f"Ano invalido. Informe entre 1450 e {self.ano_atual}.",
            )
            return False

        return True

    def carregar_livros(self):
        try:
            livros = self.db.listar_livros()
            self.tabela.setRowCount(0)

            for livro in livros:
                linha = self.tabela.rowCount()
                self.tabela.insertRow(linha)

                status = "Disponivel" if livro["disponivel"] == 1 else "Emprestado"
                valores = [
                    str(livro["id"]),
                    livro["titulo"],
                    livro["autor"],
                    "" if livro["ano"] is None else str(livro["ano"]),
                    status,
                ]

                for coluna, valor in enumerate(valores):
                    self.tabela.setItem(linha, coluna, QTableWidgetItem(valor))
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar livros: {exc}")

    def adicionar_livro(self):
        titulo = self.input_titulo.text().strip()
        autor = self.input_autor.text().strip()
        ano = self.input_ano.value()
        ano = None if ano == 0 else ano

        if not self._validar_formulario(titulo, autor, ano):
            return

        try:
            self.db.adicionar_livro(titulo, autor, ano)
            self.input_titulo.clear()
            self.input_autor.clear()
            self.input_ano.setValue(0)
            self.carregar_livros()
            self._notificar("Livro adicionado com sucesso.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar livro: {exc}")

    def marcar_emprestado(self):
        livro_id = self._livro_selecionado_id()
        if livro_id is None:
            return

        status = self._livro_selecionado_status()
        if status == "Emprestado":
            QMessageBox.information(self, "Aviso", "O livro selecionado ja esta emprestado.")
            return

        try:
            self.db.atualizar_disponibilidade(livro_id, 0)
            self.carregar_livros()
            self._notificar("Livro marcado como emprestado.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar livro: {exc}")

    def marcar_devolvido(self):
        livro_id = self._livro_selecionado_id()
        if livro_id is None:
            return

        status = self._livro_selecionado_status()
        if status == "Disponivel":
            QMessageBox.information(self, "Aviso", "O livro selecionado ja esta disponivel.")
            return

        try:
            self.db.atualizar_disponibilidade(livro_id, 1)
            self.carregar_livros()
            self._notificar("Livro marcado como devolvido.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar livro: {exc}")

    def remover_livro(self):
        livro_id = self._livro_selecionado_id()
        if livro_id is None:
            return

        resposta = QMessageBox.question(
            self,
            "Confirmacao",
            "Deseja remover o livro selecionado?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.No:
            return

        try:
            self.db.remover_livro(livro_id)
            self.carregar_livros()
            self._notificar("Livro removido com sucesso.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao remover livro: {exc}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BibliotecaWindow()
    window.show()
    sys.exit(app.exec())
