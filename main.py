import sys
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
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
from services import BibliotecaService


class BibliotecaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Biblioteca")
        self.resize(760, 500)
        self.ano_atual = date.today().year
        self.livro_em_edicao_id: int | None = None
        self.ordem_coluna = "id"
        self.ordem_direcao = "DESC"

        self.service = BibliotecaService(Database())
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

        filtros = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar por titulo ou autor")
        self.input_busca.textChanged.connect(self.carregar_livros)

        self.filtro_status = QComboBox()
        self.filtro_status.addItem("Todos", "todos")
        self.filtro_status.addItem("Disponiveis", "disponivel")
        self.filtro_status.addItem("Emprestados", "emprestado")
        self.filtro_status.currentIndexChanged.connect(self.carregar_livros)

        filtros.addWidget(QLabel("Buscar:"))
        filtros.addWidget(self.input_busca)
        filtros.addWidget(QLabel("Status:"))
        filtros.addWidget(self.filtro_status)
        layout_principal.addLayout(filtros)

        self.tabela = QTableWidget(0, 5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Titulo", "Autor", "Ano", "Status"])
        self.tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela.setSortingEnabled(True)
        self.tabela.itemSelectionChanged.connect(self._atualizar_estado_botoes)
        cabecalho = self.tabela.horizontalHeader()
        cabecalho.setStretchLastSection(True)
        cabecalho.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        cabecalho.sortIndicatorChanged.connect(self._ao_mudar_ordenacao)

        layout_principal.addWidget(QLabel("Livros cadastrados:"))
        layout_principal.addWidget(self.tabela)

        botoes_acao = QHBoxLayout()

        self.btn_emprestar = QPushButton("Marcar emprestado")
        self.btn_emprestar.clicked.connect(self.marcar_emprestado)

        self.btn_devolver = QPushButton("Marcar devolvido")
        self.btn_devolver.clicked.connect(self.marcar_devolvido)

        self.btn_remover = QPushButton("Remover livro")
        self.btn_remover.clicked.connect(self.remover_livro)

        self.btn_editar = QPushButton("Editar livro")
        self.btn_editar.clicked.connect(self.iniciar_edicao_livro)

        self.btn_cancelar_edicao = QPushButton("Cancelar edicao")
        self.btn_cancelar_edicao.clicked.connect(self.cancelar_edicao_livro)

        botoes_acao.addWidget(self.btn_emprestar)
        botoes_acao.addWidget(self.btn_devolver)
        botoes_acao.addWidget(self.btn_editar)
        botoes_acao.addWidget(self.btn_remover)
        botoes_acao.addWidget(self.btn_cancelar_edicao)
        layout_principal.addLayout(botoes_acao)

        self._atualizar_estado_botoes()

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

    def _atualizar_estado_botoes(self):
        selecionado = self.tabela.currentRow() >= 0
        self.btn_emprestar.setEnabled(selecionado)
        self.btn_devolver.setEnabled(selecionado)
        self.btn_remover.setEnabled(selecionado)
        self.btn_editar.setEnabled(selecionado)
        self.btn_cancelar_edicao.setEnabled(self.livro_em_edicao_id is not None)

    def _ao_mudar_ordenacao(self, indice_coluna: int, ordem):
        colunas = {
            0: "id",
            1: "titulo",
            2: "autor",
            3: "ano",
            4: "disponivel",
        }
        self.ordem_coluna = colunas.get(indice_coluna, "id")
        self.ordem_direcao = "ASC" if ordem == Qt.SortOrder.AscendingOrder else "DESC"
        self.carregar_livros()

    def _limpar_formulario(self):
        self.input_titulo.clear()
        self.input_autor.clear()
        self.input_ano.setValue(0)

    def _entrar_modo_edicao(self, livro_id: int):
        self.livro_em_edicao_id = livro_id
        self.btn_adicionar.setText("Salvar edicao")
        self._atualizar_estado_botoes()

    def cancelar_edicao_livro(self):
        self.livro_em_edicao_id = None
        self.btn_adicionar.setText("Adicionar livro")
        self._limpar_formulario()
        self._atualizar_estado_botoes()
        self._notificar("Edicao cancelada.")

    def iniciar_edicao_livro(self):
        livro_id = self._livro_selecionado_id()
        if livro_id is None:
            return

        try:
            livro = self.service.obter_livro(livro_id)
            if livro is None:
                QMessageBox.warning(self, "Atencao", "Livro nao encontrado.")
                return

            self.input_titulo.setText(livro.titulo)
            self.input_autor.setText(livro.autor)
            self.input_ano.setValue(0 if livro.ano is None else livro.ano)
            self._entrar_modo_edicao(livro.id)
            self._notificar("Edicao iniciada.")
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao iniciar edicao: {exc}")

    def carregar_livros(self):
        try:
            livros = self.service.listar_livros(
                termo=self.input_busca.text().strip(),
                filtro_status=self.filtro_status.currentData(),
                ordenar_por=self.ordem_coluna,
                ordem=self.ordem_direcao,
            )
            self.tabela.setRowCount(0)

            for livro in livros:
                linha = self.tabela.rowCount()
                self.tabela.insertRow(linha)

                valores = [
                    str(livro.id),
                    livro.titulo,
                    livro.autor,
                    "" if livro.ano is None else str(livro.ano),
                    livro.status,
                ]

                for coluna, valor in enumerate(valores):
                    self.tabela.setItem(linha, coluna, QTableWidgetItem(valor))

            self._atualizar_estado_botoes()
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
            if self.livro_em_edicao_id is None:
                self.service.adicionar_livro(titulo, autor, ano)
                self._notificar("Livro adicionado com sucesso.")
            else:
                self.service.editar_livro(self.livro_em_edicao_id, titulo, autor, ano)
                self.cancelar_edicao_livro()
                self._notificar("Livro atualizado com sucesso.")

            self._limpar_formulario()
            self.carregar_livros()
        except ValueError as exc:
            QMessageBox.warning(self, "Validacao", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao adicionar livro: {exc}")

    def marcar_emprestado(self):
        livro_id = self._livro_selecionado_id()
        if livro_id is None:
            return

        try:
            self.service.marcar_emprestado(livro_id)
            self.carregar_livros()
            self._notificar("Livro marcado como emprestado.")
        except ValueError as exc:
            QMessageBox.information(self, "Aviso", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao atualizar livro: {exc}")

    def marcar_devolvido(self):
        livro_id = self._livro_selecionado_id()
        if livro_id is None:
            return

        try:
            self.service.marcar_devolvido(livro_id)
            self.carregar_livros()
            self._notificar("Livro marcado como devolvido.")
        except ValueError as exc:
            QMessageBox.information(self, "Aviso", str(exc))
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
            self.service.remover_livro(livro_id)
            if self.livro_em_edicao_id == livro_id:
                self.cancelar_edicao_livro()
            self.carregar_livros()
            self._notificar("Livro removido com sucesso.")
        except ValueError as exc:
            QMessageBox.information(self, "Aviso", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao remover livro: {exc}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BibliotecaWindow()
    window.show()
    sys.exit(app.exec())
