import os.path

import mysql.connector
import pandas as pd

def connect_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", #put your MySQL password 
        database="" #put your database name
    )

def list_bd():
    conexao = connect_bd()
    cursor = conexao.cursor()
    cursor.execute("SHOW TABLES")
    tabelas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return [tabela[0] for tabela in tabelas]


def add_bd(table, name_archive, archive_type, category, archive, description=None):
    conexao = connect_bd()
    cursor = conexao.cursor()

    table = table.lower().strip()
    table = table.replace(" ", "_")
    name_archive = name_archive.strip().lower()
    try:
        with open(archive.strip(), "rb") as file:
            file_content = file.read()
    except FileNotFoundError:
        return "Erro: arquivo não encontrado no caminho especificado."
    except PermissionError:
        return "Erro: permissão negada para acessar o arquivo."

    if verification_name_bd(name_archive=name_archive, table=table, cursor=cursor):
        return f"Erro: Já existe um arquivo com o nome '{name_archive}' no banco de dados."

    '''if verification_archive_bd(archive=archive, table=table, cursor=cursor):
        return f"Erro: arquivo ja existente"'''

    if not table.isidentifier():
        return "Erro: Nome da tabela inválido."

    #archive.replace("\\", "/")

    query = (f"INSERT INTO {table} (name_archive, type_archive, category, description_archive, archive) "
             f"VALUES (%s, %s, %s, %s, %s)")
    values = (name_archive, archive_type.upper(), category.strip().lower(), description, file_content)

    try:
        cursor.execute(query, values)
        conexao.commit()
        return "arquivo adicionado ao banco de dados com sucesso."
    except Exception as e:
        conexao.rollback()
        return f"Erro: {str(e)}"
    finally:
        cursor.close()
        conexao.close()


def verification_name_bd(name_archive, table, cursor):
    query_check = f"SELECT COUNT(*) FROM {table} WHERE name_archive = %s"
    cursor.execute(query_check, (name_archive,))
    result = cursor.fetchone()
    return result[0] > 0

def verification_archive_bd(archive, table, cursor):
    query_check = f"SELECT COUNT(*) FROM {table} WHERE archive = %s"
    cursor.execute(query_check, (archive,))
    result = cursor.fetchone()
    return result[0] > 0

def verification_id(id, table, cursor):
    query_check = f"SELECT COUNT(*) FROM {table} WHERE id = %s"
    cursor.execute(query_check, (id,))
    result = cursor.fetchone()
    return result[0] == 0


def select_bd(table, column="*"):
    conexao = connect_bd()
    cursor = conexao.cursor()

    try:
        cursor.execute(F"SELECT {column} FROM {table}")
        linhas = cursor.fetchall()
        colunas = [desc[0] for desc in cursor.description]
        df_linhas = pd.DataFrame(linhas, columns=colunas)
        return df_linhas
    except mysql.connector.errors.ProgrammingError:
        return "tabela ou coluna invalido"
    finally:
        cursor.close()
        conexao.close()

def update_db(table, new, id):
    conexao = connect_bd()
    cursor = conexao.cursor()

    try:
        query_old = (f"SELECT name_archive, category, type_archive,description_archive, archive FROM {table} WHERE id = "
                     f"%s")
        cursor.execute(query_old, (id,))
        old_data = cursor.fetchone()

        if not old_data:
            return "Arquivo não encontrado no banco de dados."

        colunas = ["name_archive", "category", "type_archive", "description_archive", "archive"]
        old_df = pd.DataFrame([old_data], columns=colunas)
        new_df = pd.DataFrame([new], columns=colunas)

        update_fields = []
        update_values = []

        for coluna in colunas:
            if old_df[coluna][0] != new_df[coluna][0]:
                update_fields.append(f"{coluna} = %s")
                update_values.append(new_df[coluna][0])

        if not update_fields:
            return "Nenhuma alteração detectada"

        update_query = f"UPDATE {table} SET {', '.join(update_fields)} WHERE id = %s"
        update_values.append(id)
        cursor.execute(update_query, tuple(update_values))
        conexao.commit()

        return "Arquivo atualizado com sucesso!!!"

    except Exception as e:
        print(f"Erro ao atualizar o arquivo: {e}")
        return f"Erro ao atualizar o arquivo: {e}"
    finally:
        cursor.close()
        conexao.close()


def delete_bd(table, id):
    conexao = connect_bd()
    cursor = conexao.cursor()

    if verification_id(id=id, table=table, cursor=cursor):
        return f"Erro: sem linha com ID = {id} no banco de dados."

    if not table.isidentifier():
        return "Erro: Nome da tabela inválido."

    query = F"DELETE FROM {table} WHERE id = %s"
    values = (id, )

    try:
        cursor.execute(query, values)
        conexao.commit()
        return f"linha deletada com sucesso"
    except:
        conexao.rollback()
        return "falha ao deletar dado"
    finally:
        cursor.close()
        conexao.close()


def create_table_db(table_name):
    conexao = connect_bd()
    cursor = conexao.cursor()
    table_name = table_name.lower().strip()
    table_name = table_name.replace(" ", "_")

    def is_valid_table_name(table_name):
        reserved_words = {"select", "insert", "delete", "update", "table"}  # Adicione mais palavras
        return table_name.isidentifier() and table_name.lower() not in reserved_words

    if not is_valid_table_name(table_name):
        return "Nome da tabela é inválido ou reservado."

    if not table_name.isidentifier():
        return "Erro: Nome da tabela ja existente."

    try:
        # Verifica se a tabela já existe
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        if cursor.fetchone():
            return "Erro: Tabela já existente."

        cursor.execute(f"""
                    CREATE TABLE {table_name} (
                        id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
                        name_archive VARCHAR(100) NOT NULL,
                        type_archive VARCHAR(100) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        description_archive VARCHAR(250) NULL,
                        archive MEDIUMBLOB NOT NULL
                    )
                """)
        conexao.commit()
        return "tabela criada com sucesso!!!"
    except:
        conexao.rollback()
        return "erro ao criar a tabela"
    finally:
        cursor.close()
        conexao.close()


def drop_table(table_name):

    if not table_name.isidentifier():
        return f"Erro: Nome da tabela '{table_name}' é inválido."

    conexao = connect_bd()
    cursor = conexao.cursor()

    try:
        cursor.execute(f"DROP TABLE {table_name}")
        conexao.commit()
        return f"tabela '{table_name}' deletada com sucesso!!!"
    except Exception as e:
        conexao.rollback()
        return f"erro ao deletar a tabela '{table_name}': {e}"
    finally:
        cursor.close()
        conexao.close()

def download(id, table, save_path):
    conexao = connect_bd()
    cursor = conexao.cursor()

    try:
        query = f"SELECT name_archive, archive FROM {table} WHERE id = %s"
        cursor.execute(query, (id, ))
        result = cursor.fetchall()

        if result:
            file_name, file_blob = result[0][0], result[0][1]

            full_path = os.path.join(save_path, file_name)

            with open(full_path, "wb") as file:
                file.write(file_blob)
            print(f"Arquivo '{file_name}' salvo em: {full_path}")
            return f"Arquivo '{file_name}' salvo em: {full_path}"
        else:
            print("Arquivo não encontrado")
            return "Arquivo não encontrado"
    except Exception as e:
        print(f"Erro ao fazer o download: {e}")
        return f"Erro ao fazer o download: {e}"
    finally:
        cursor.close()
        conexao.close()
