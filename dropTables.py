import sqlite3

def drop_tables():
    try:
        connection = sqlite3.connect('Banco_QuilOn')
        cursor = connection.cursor()
        
        # Excluir tabela, se existir
        cursor.execute('''DROP TABLE IF EXISTS NomeDaTabela''')
        
        connection.commit()
        print("Tabelas excluídas com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao excluir tabelas: {e}")
    finally:
        connection.close()

# Chamar a função para excluir as tabelas
drop_tables()
