from PySide6.QtWidgets import *
import db_commands as db
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

categorys = [
        'teoria', 'pratica', 'atividade', 'resposta', 'formulario',"slide", "apostila/livro", "projeto", "referencia"
        , "outro"
    ]
types = ['PDF', 'WORD', 'POWERPOINT', 'EXCEL', "SQL", "PYTHON", "JAVA", "JAVASCRIPT", "HTML", "CSS", "C", "C#",
         "C++", "TXT", "IMG"]


class EditPage(QDialog):
    def __init__(self, id, table, file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Arquivo")
        self.resize(600, 450)

        self.id = id
        self.table = table
        self.file = file
        self.parent = parent

        self.main_layout = QVBoxLayout(self)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scrollable_frame = QWidget()
        scroll_layout = QVBoxLayout(scrollable_frame)

        # Campo: archive
        scroll_layout.addWidget(QLabel("Selecione o arquivo: (se não quiser mudalo deixe o espaço em branco)"))
        self.archive_path = QLineEdit()
        self.archive_path.setReadOnly(True)
        scroll_layout.addWidget(self.archive_path)

        browse_button = QPushButton("Procurar")
        browse_button.clicked.connect(self.browse_file)
        scroll_layout.addWidget(browse_button)

        # Campo: Nome do Arquivo
        scroll_layout.addWidget(QLabel("Dê um nome ao arquivo:"))
        self.name = QLineEdit()
        self.name.setText(self.file["name_archive"])
        scroll_layout.addWidget(self.name)

        # Campo: Categoria
        scroll_layout.addWidget(QLabel("Qual o tipo de conteúdo do arquivo:"))
        self.select_category = QComboBox()
        self.select_category.addItems(["selecione um conteúdo"] + categorys)
        self.select_category.setCurrentText(self.file["category"])
        scroll_layout.addWidget(self.select_category)

        # Campo: Tipo de Arquivo
        scroll_layout.addWidget(QLabel("Selecione o tipo de arquivo:"))
        self.select_type = QComboBox()
        self.select_type.addItems(["selecione um tipo de arquivo"] + types)
        self.select_type.setCurrentText(self.file["type_archive"])
        scroll_layout.addWidget(self.select_type)

        # Campo: Descrição
        scroll_layout.addWidget(QLabel("Dê uma descrição ao arquivo (opcional):"))
        self.description = QTextEdit()
        self.description.setText(self.file["description_archive"])
        scroll_layout.addWidget(self.description)

        # Botão de Conclusão
        self.button = QPushButton("Pronto?")
        self.button.clicked.connect(self.update_file)
        scroll_layout.addWidget(self.button)

        # Configuração da ScrollArea
        scroll_area.setWidget(scrollable_frame)
        self.main_layout.addWidget(scroll_area)
        self.setLayout(self.main_layout)

    def update_file(self):
        file_content = self.file["archive"]
        if self.archive_path.text().strip() != "":
            try:
                with open(self.archive_path.text().strip(), "rb") as file:
                    file_content = file.read()
            except FileNotFoundError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Arquivo não encontrado. Selecione um arquivo válido.")
                msg.setWindowTitle("Erro")
                retval = msg.exec()
                return

        new_data = {
            "archive": file_content,
            "name_archive": self.name.text().strip(),
            "category": self.select_category.currentText(),
            "type_archive": self.select_type.currentText(),
            "description_archive": self.description.toPlainText().strip()
        }

        resp = db.update_db(table=self.table, new=new_data, id=self.id)

        if "sucesso" in resp:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(resp)
            msg.setWindowTitle("Sucesso >_<")
            retval = msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(resp)
            msg.setWindowTitle("Erro")
            retval = msg.exec()
    def browse_file(self):
        # Abre uma janela para selecionar o arquivo
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Selecione o arquivo")
        if file_path:
            self.archive_path.setText(file_path)

    def closeEvent(self, event):
        if self.parent:
            self.parent.apply_filters()
        super().closeEvent(event)


class CreateTable(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar nova tabela")
        self.resize(200, 150)

        self.parent = parent

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Insira o nome da tabela: "))
        self.table_name = QLineEdit()
        layout.addWidget(self.table_name)

        create_button = QPushButton("Criar tabela")
        create_button.clicked.connect(self.create_table)
        layout.addWidget(create_button)

    def create_table(self):
        table_name = self.table_name.text().strip()

        if not table_name:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("O nome da tabela não pode estar vazio!")
            msg.setWindowTitle("Erro")
            retval = msg.exec()
            return

        resp = db.create_table_db(table_name)
        if "sucesso" in resp:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(resp)
            msg.setWindowTitle("Sucesso >_<")
            retval = msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(resp)
            msg.setWindowTitle("Erro")
            retval = msg.exec()

    def closeEvent(self, event):
        if self.parent:
            self.parent.load_tables()
        super().closeEvent(event)


class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sisiteminha do balacubacu")
        self.resize(600, 450)

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal
        self.main_layout = QVBoxLayout(main_widget)

        # Placeholder para a barra de navegação
        self.nav_bar_container = QHBoxLayout()
        self.main_layout.addLayout(self.nav_bar_container)

        # Placeholder para o conteúdo principal
        self.page_container = QVBoxLayout()
        self.main_layout.addLayout(self.page_container)

        # Inicializar a página inicial e a barra de navegação
        self.load_home_nav_bar()
        self.load_home_page()

    def clear_layout(self, layout):
        """Remove todos os widgets de um layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # navs_bars
    def load_home_nav_bar(self):
        """Carrega a barra de navegação da página inicial."""
        self.clear_layout(self.nav_bar_container)

        database_button = QPushButton("Banco de Dados")
        chatbot_button = QPushButton("Chatbot")

        database_button.clicked.connect(self.load_database_page)
        chatbot_button.clicked.connect(self.load_chatbot_page)

        self.nav_bar_container.addWidget(database_button)
        self.nav_bar_container.addWidget(chatbot_button)

    def load_database_nav_bar(self):
        """Carrega a barra de navegação específica do Banco de Dados."""
        self.clear_layout(self.nav_bar_container)

        back_button = QPushButton("<-")
        back_button.clicked.connect(self.load_home_page)

        home_button = QPushButton("HOME")
        home_button.clicked.connect(self.load_database_page)

        db_add_button = QPushButton("ADD")
        db_add_button.clicked.connect(self.load_add_database_page)

        db_list_button = QPushButton("LIST")
        db_list_button.clicked.connect(self.load_list_database_page)

        db_table_button = QPushButton("TABLE")
        db_table_button.clicked.connect(self.load_create_table_page)

        self.nav_bar_container.addWidget(back_button)
        self.nav_bar_container.addWidget(home_button)
        self.nav_bar_container.addWidget(db_add_button)
        self.nav_bar_container.addWidget(db_list_button)
        self.nav_bar_container.addWidget(db_table_button)


    def load_chatbot_nav_bar(self):
        self.clear_layout(self.nav_bar_container)

        back_button = QPushButton("<-")
        back_button.clicked.connect(self.load_home_page)

        test = QPushButton("teste")

        self.nav_bar_container.addWidget(back_button)
        self.nav_bar_container.addWidget(test)

    #pagina home
    def load_home_page(self):
        """Carrega a página inicial."""
        self.clear_layout(self.page_container)
        self.load_home_nav_bar()

        label = QLabel("Bem-vindo à Página Inicial!")
        label.setStyleSheet("font-size: 20px;")

        self.page_container.addWidget(label)

    #paginas do banco de dados
    def load_database_page(self):
        """Carrega a página do Banco de Dados."""
        self.clear_layout(self.page_container)
        self.load_database_nav_bar()

        bd_instructions_text = """
        Bem-vindo ao programa de gerenciamento de arquivos e tabelas! 🎉
        Aqui está um guia rápido para usar tudo certinho:

        1. Filtrar Arquivos(LIST):
           - Selecione a tabela que você quer usar no filtro.
           - Use as opções para procurar arquivos específicos (por nome, categoria ou tipo).
           - Clique em "Editar" no arquivo desejado para fazer alterações.

        2. Adicionar Arquivos(ADD):
           - Clique no botão "Adicionar Arquivo".
           - Preencha as informações necessárias: nome, tipo, categoria e descrição.
           - Escolha o arquivo do seu computador e pronto!

        3. Editar Arquivos(LIST):
           - Na lista de arquivos, clique em "Editar".
           - Altere os dados que precisar, exceto a tabela.
           - Se quiser substituir o conteúdo do arquivo, selecione um novo.

        4. Gerenciar Tabelas(TABLE):
           - Vá para a página de Tabelas.
           - Criar Tabela: Clique no botão "Criar nova tabela", dê um nome e pronto!
           - Excluir Tabela: Use o botão "Excluir" na lista, mas cuidado! Isso apaga tudo dentro da tabela.

        💡 Dica Importante:
        Certifique-se de usar nomes claros para os arquivos e tabelas para evitar confusão. Não se preocupe, o programa avisa se algo der errado!
        """

        bd_home_instructions = QLabel(bd_instructions_text)
        bd_home_instructions.setWordWrap(True)  # Permite que o texto quebre em várias linhas
        bd_home_instructions.setStyleSheet("""
            QLabel {
                background-color: #f9f9f9;  /* Fundo claro */
                border: 2px solid #cfcfcf;  /* Borda cinza */
                border-radius: 10px;        /* Bordas arredondadas */
                padding: 15px;              /* Espaço interno */
                color: #333333;             /* Texto escuro */
                font-size: 14px;            /* Tamanho da fonte */
                font-family: 'Arial', sans-serif; /* Fonte */
            }
        """)

        scroll_area = QScrollArea()
        scroll_area.setWidget(bd_home_instructions)
        scroll_area.setWidgetResizable(True)  # Permite que o conteúdo se redimensione
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;  /* Remove bordas extras da área de rolagem */
            }
        """)

        self.page_container.addWidget(scroll_area)

    def load_add_database_page(self):

        self.clear_layout(self.page_container)
        self.load_database_nav_bar()

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scrollable_frame = QWidget()
        scroll_layout = QVBoxLayout(scrollable_frame)

        #campo: tabela

        scroll_layout.addWidget(QLabel("Qual a materia do arquivo:"))
        self.select_table = QComboBox()
        tables = db.list_bd()
        self.select_table.addItems(["selecione um conteúdo"] + tables)
        scroll_layout.addWidget(self.select_table)

        # Campo: Arquivo
        scroll_layout.addWidget(QLabel("Selecione o arquivo:"))
        self.archive_path = QLineEdit()
        self.archive_path.setReadOnly(True)
        scroll_layout.addWidget(self.archive_path)

        browse_button = QPushButton("Procurar")
        browse_button.clicked.connect(self.browse_file)
        scroll_layout.addWidget(browse_button)

        # Campo: Nome do Arquivo
        scroll_layout.addWidget(QLabel("Dê um nome ao arquivo:"))
        self.name = QLineEdit()
        scroll_layout.addWidget(self.name)

        # Campo: Categoria
        scroll_layout.addWidget(QLabel("Qual o tipo de conteúdo do arquivo:"))
        self.select_category = QComboBox()
        self.select_category.addItems(["selecione um conteúdo"] + categorys)
        scroll_layout.addWidget(self.select_category)

        # Campo: Tipo de Arquivo
        scroll_layout.addWidget(QLabel("Selecione o tipo de arquivo:"))
        self.select_type = QComboBox()
        self.select_type.addItems(["selecione um tipo de arquivo"] + types)
        scroll_layout.addWidget(self.select_type)

        # Campo: Descrição
        scroll_layout.addWidget(QLabel("Dê uma descrição ao arquivo (opcional):"))
        self.description = QTextEdit()
        scroll_layout.addWidget(self.description)

        # Botão de Conclusão
        self.button = QPushButton("Pronto?")
        self.button.clicked.connect(self.save_to_db)
        scroll_layout.addWidget(self.button)

        # Configuração da ScrollArea
        scroll_area.setWidget(scrollable_frame)
        self.page_container.addWidget(scroll_area)

    def browse_file(self):
        # Abre uma janela para selecionar o arquivo
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Selecione o arquivo")
        if file_path:
            self.archive_path.setText(file_path)

    def save_to_db(self):
        # Recupera os valores dos campos
        selected_table = self.select_table.currentText()
        selected_archive = self.archive_path.text().strip()
        selected_name = self.name.text().strip()
        selected_cat = self.select_category.currentText()
        selected_type = self.select_type.currentText()
        selected_desc = self.description.toPlainText().strip()

        if selected_desc == "":
            selected_desc = None

        verificador = f"{selected_cat}, {selected_type}, {selected_table}"
        if not(all([selected_archive, selected_name])) or "selecione" in verificador:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Preencha todos os espaços obrigatorios!!!")
            msg.setWindowTitle("Erro")
            retval = msg.exec()
            return

        _, file_extension = os.path.splitext(selected_archive)

        if not file_extension:  # Caso o arquivo não tenha extensão
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Erro: Arquivo selecionado não possui extensão!")
            msg.setWindowTitle("Erro")
            retval = msg.exec()
            return

        resp = db.add_bd(selected_table, f"{selected_name}{file_extension}", selected_type, selected_cat, selected_archive, selected_desc)

        if "erro" in resp.lower():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(resp)
            msg.setWindowTitle("Erro")
            retval = msg.exec()
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText("O arquivo foi adicionado com sucesso")
        msg.setWindowTitle("Sucesso >_<")
        retval = msg.exec()


    def load_list_database_page(self):
        self.clear_layout(self.page_container)
        self.load_database_nav_bar()

        label = QLabel("Filtros:")
        label.setStyleSheet("font-size: 20px;")

        self.page_container.addWidget(label)

        # Filtros
        filter_frame = QWidget()
        filter_layout = QHBoxLayout(filter_frame)

        # Campo de busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o nome do arquivo...")
        filter_layout.addWidget(QLabel("Busca:"))
        filter_layout.addWidget(self.search_input)

        # Filtro por categoria
        self.category_filter = QComboBox()
        self.category_filter.addItems(["Todos"] + categorys)
        filter_layout.addWidget(QLabel("Categoria:"))
        filter_layout.addWidget(self.category_filter)

        # Filtro por tabela
        self.table_filter = QComboBox()
        self.table_filter.addItems(db.list_bd())
        filter_layout.addWidget(QLabel("materia:"))
        filter_layout.addWidget(self.table_filter)

        # Filtro por tipo de arquivo
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todos"] + types)
        filter_layout.addWidget(QLabel("Tipo:"))
        filter_layout.addWidget(self.type_filter)

        # Botão de aplicação do filtro
        filter_button = QPushButton("Aplicar Filtro")
        filter_button.clicked.connect(self.apply_filters)

        self.page_container.addWidget(filter_frame)
        self.page_container.addWidget(filter_button)


        #mostra os arquivos
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(7)
        self.file_table.setHorizontalHeaderLabels(["Nome do Arquivo", "Categoria", "Tipo", "Descrição", "[Editar]",
                                                   "[Excluir]", "[Download]"])
        self.file_table.setSortingEnabled(True)
        self.page_container.addWidget(self.file_table)

        self.files = db.select_bd(self.table_filter)

    def delete(self, name, id):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(f"Tem certeza q quer excluir {name}")
        msg.setWindowTitle("Delete")
        yes = msg.addButton("Sim", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        retval = msg.exec()

        if msg.clickedButton() == yes:
            db.delete_bd(self.table_filter.currentText(), id)
            self.apply_filters()

    def download(self, file_name, id):
        file_path = QFileDialog.getExistingDirectory(
                None, "Salvar Arquivo"
            )

        if file_path == "":
            return

        resp = db.download(id, self.table_filter.currentText(), file_path)

        if "salvo em" in resp:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(resp)
            msg.setWindowTitle("Sucesso >_<")
            retval = msg.exec()

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(resp)
            msg.setWindowTitle("Erro")
            retval = msg.exec()

    def load_files(self, filtered_files=None):
        self.file_table.setRowCount(0)
        files_to_load = filtered_files if filtered_files is not None else self.files

        for _, file in files_to_load.iterrows():
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            self.file_table.setItem(row_position, 0, QTableWidgetItem(file["name_archive"]))
            self.file_table.setItem(row_position, 1, QTableWidgetItem(file["category"]))
            self.file_table.setItem(row_position, 2, QTableWidgetItem(file["type_archive"]))
            self.file_table.setItem(row_position, 3, QTableWidgetItem(file["description_archive"]))

            # Botão de edição
            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(
                lambda checked, current_file=file: EditPage(
                    table=self.table_filter.currentText(),
                    file=current_file,
                    id=current_file["id"],
                    parent=self
                ).exec()
            )
            self.file_table.setCellWidget(row_position, 4, edit_button)

            # Botão de Exclusão
            delete_button = QPushButton("Excluir")
            delete_button.clicked.connect(lambda _, f_id=file["id"], f_name=file["name_archive"]:
                                          self.delete(name=f_name, id=f_id))
            self.file_table.setCellWidget(row_position, 5, delete_button)


            # Botão de Download
            download_button = QPushButton("Download")
            download_button.clicked.connect(lambda _, f_id=file["id"], f_name=file["name_archive"]:
                                            self.download(file_name=f_name, id=f_id))
            self.file_table.setCellWidget(row_position, 6, download_button)


    def apply_filters(self):
        """Aplica os filtros e atualiza a tabela."""
        table = self.table_filter.currentText()
        search_text = self.search_input.text().lower()
        selected_category = self.category_filter.currentText()
        selected_type = self.type_filter.currentText()

        self.files = db.select_bd(table)

        filtered_files = self.files.copy()

        if selected_type != "Todos":
            filtered_files = filtered_files[filtered_files["type_archive"] == selected_type]

            # Filtrar pela categoria, se não for "Todos"
        if selected_category != "Todos":
            filtered_files = filtered_files[filtered_files["category"] == selected_category]

        filtered_files["combined"] = (filtered_files["name_archive"].fillna("") + " " +
                                      filtered_files["description_archive"].fillna(""))

        if search_text != "":
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(filtered_files["combined"])

            input_vec = vectorizer.transform([search_text])
            similarity_score = cosine_similarity(input_vec, tfidf_matrix)
            indices = similarity_score.argsort()[0][::-1]
            filtered_files = filtered_files.iloc[indices].reset_index(drop=True)

        self.load_files(filtered_files)

    def load_create_table_page(self):
        self.clear_layout(self.page_container)
        self.load_database_nav_bar()

        create_table_button = QPushButton("Criar nova tabela")
        create_table_button.clicked.connect(lambda: CreateTable(parent=self).exec())
        self.page_container.addWidget(create_table_button)

        self.show_tables = QTableWidget()
        self.show_tables.setColumnCount(2)
        self.show_tables.setHorizontalHeaderLabels(["tabela", "[Excluir]"])
        self.show_tables.setSortingEnabled(True)
        self.page_container.addWidget(self.show_tables)

        self.load_tables()

    def load_tables(self):
        self.tables = db.list_bd()
        self.show_tables.setRowCount(0)

        for table_name in self.tables:
            row_position = self.show_tables.rowCount()
            self.show_tables.insertRow(row_position)

            # Coluna: Nome da tabela
            self.show_tables.setItem(row_position, 0, QTableWidgetItem(table_name))

            # Coluna: Botão Excluir
            delete_button = QPushButton("Excluir")
            delete_button.clicked.connect(lambda checked, t=table_name: self.delete_table(t))
            self.show_tables.setCellWidget(row_position, 1, delete_button)

    def delete_table(self, table_name):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(f"Tem certeza q quer excluir a tabela: {table_name}")
        msg.setWindowTitle("Delete")
        yes = msg.addButton("Sim", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        retval = msg.exec()

        if msg.clickedButton() == yes:
            resp = db.drop_table(table_name)

            if "sucesso" in resp:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setText(resp)
                msg.setWindowTitle("Sucesso >_<")
                retval = msg.exec()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(resp)
                msg.setWindowTitle("Erro")
                retval = msg.exec()
        self.load_tables()


    #paginas do bot
    def load_chatbot_page(self):
        """Carrega a página do Chatbot."""
        self.clear_layout(self.page_container)
        self.load_chatbot_nav_bar()  # Reutiliza a barra inicial para o Chatbot (ou crie outra)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scrollable_frame = QWidget()
        scroll_layout = QVBoxLayout(scrollable_frame)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("background-color: #f4f4f4; padding: 10px;")
        scroll_layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Digite sua pergunta aqui...")
        input_layout.addWidget(self.user_input)

        self.send_button = QPushButton("Enviar")
        #self.send_button.clicked.connect()
        input_layout.addWidget(self.send_button)

        scroll_area.setWidget(scrollable_frame)
        self.page_container.layout().addWidget(scroll_area)  # Adiciona a área de rolagem ao container

        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        self.page_container.layout().addWidget(input_widget)

        self.selected_table = None

        bot_response = "HI"
        self.chat_history.append(f"<b>Bot:</b> {bot_response}")


    def send_message(self):
        """Obtém a mensagem do usuário e processa a interação."""
        user_message = self.user_input.text().strip()
        if not user_message:
            return  # Não faz nada se o campo estiver vazio

        self.chat_history.append(f"<b>Você:</b> {user_message}")
        self.user_input.clear()  # Limpa o campo de entrada

        # Lógica para processar a resposta do bot
        self.chatbot_response(user_message)

    def chatbot_response(self, user_message):
        """Simula a resposta do chatbot (placeholder por enquanto)."""
        # Resposta simulada por enquanto
        bot_response = "Ainda estou aprendendo a responder perguntas baseadas no banco de dados. 😅"
        self.chat_history.append(f"<b>Bot:</b> {bot_response}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainPage()
    window.show()
    app.exec()
