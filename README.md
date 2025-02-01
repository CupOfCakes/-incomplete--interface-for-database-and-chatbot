# -incomplete--interface-for-database-and-chatbot
This project is a Knowledge Base system to assist in studies, allowing the user to ask questions and receive relevant excerpts from files stored in the database.

Knowledge Base e database para Matérias da Faculdade
Este projeto é um sistema de Knowledge Base desenvolvido para auxiliar nos estudos das matérias da faculdade. Ele permite que o usuário selecione uma matéria e faça perguntas, retornando trechos relevantes dos arquivos armazenados no banco de dados.

#🔧 Funcionalidades

Identificação da matéria com base no input do usuário.

Seleção dos arquivos mais relevantes utilizando técnicas de fuzzy matching.

Extração de texto dos arquivos e busca pelos trechos mais relevantes utilizando TF-IDF.

Interface gráfica para a manipulação de database.

#🛠 Tecnologias Utilizadas

-Python (PySide6 para a interface gráfica)

-MySQL (armazenamento dos arquivos e metadados)

-Fuzzy Matching (para encontrar a matéria correta)

-TF-IDF (para identificar trechos relevantes)

-PyMuPDF, python-docx, python-pptx (para extração de texto)

#📌 Objetivo

Criar um sistema eficiente e leve para responder dúvidas acadêmicas com base nos materiais disponíveis, sem a necessidade de processamento pesado de IA, garantindo um bom desempenho mesmo em computadores mais limitados.
