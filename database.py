import sqlite3
#--- Arquivo destinado a manutenção das tabelas e realização de testes ---#

# Dropar tabelas se necessario
def drop_tables():
    try:
        connection = sqlite3.connect('Banco_QuilOn')
        cursor = connection.cursor()
        
        # Excluir tabela, se existir
        # cursor.execute('''DROP TABLE IF EXISTS NomeDaTabela''')
        
        connection.commit()
        print("Tabelas excluídas com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao excluir tabelas: {e}")
    finally:
        connection.close()
drop_tables()

# Função para criar as tabelas de produtos, usuários e endereços no banco de dados SQLite
def create_tables():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    
    # Criação da tabela products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            production_time INTEGER NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            idUsuario INTEGER,
            FOREIGN KEY (idUsuario) REFERENCES user(idUsuario)
        )
    ''')

    # Criação da tabela user
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            dataNasc TEXT NOT NULL,
            sexo TEXT NOT NULL,
            cpf TEXT NOT NULL,
            rg TEXT NOT NULL,
            celular TEXT NOT NULL,
            telefone TEXT,
            email TEXT NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    # Criação da tabela address
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS address (
            idEndereco INTEGER PRIMARY KEY AUTOINCREMENT,
            idUsuario INTEGER NOT NULL,
            endereco TEXT NOT NULL,
            bairro TEXT NOT NULL,
            numero TEXT NOT NULL,
            cidade TEXT NOT NULL,
            uf TEXT NOT NULL,
            complemento TEXT,
            FOREIGN KEY (idUsuario) REFERENCES user (idUsuario)
        )
    ''')

    # Criação da tabela quilombo com idUsuario como chave estrangeira
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quilombo (
            idQuilombo INTEGER PRIMARY KEY AUTOINCREMENT,
            idUsuario INTEGER NOT NULL,
            name TEXT NOT NULL,
            certificationNumber TEXT NOT NULL,
            latAndLng TEXT NOT NULL,
            kmAndComplement TEXT,
            FOREIGN KEY (idUsuario) REFERENCES user(idUsuario)
        )
    ''')


    # Criação da tabela favorites
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            idFav INTEGER PRIMARY KEY AUTOINCREMENT,
            idUsuario INTEGER NOT NULL,
            idProduto INTEGER NOT NULL,
            FOREIGN KEY (idUsuario) REFERENCES user(idUsuario),
            FOREIGN KEY (idProduto) REFERENCES products(id)
        )
    ''')

    # Criação da tabela searched
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searched (
            idBusca INTEGER PRIMARY KEY AUTOINCREMENT,
            idUsuario INTEGER NOT NULL,
            conteudoBuscado TEXT NOT NULL,
            FOREIGN KEY (idUsuario) REFERENCES user(idUsuario)
        )
    ''')

    connection.commit()
    connection.close()

create_tables()  # Certifica-se de que as tabelas existem antes de iniciar o aplicativo


## TESTES ##

# ------  RECOMENDAÇÃO BASEADA NO KNN ------ #
# # Função para transformar categorias em uma representação numérica
# def encode_categories(categories, all_categories):
#     return [all_categories.index(category) for category in categories if category in all_categories]

# # Função para recomendar produtos com base nas categorias mais pesquisadas pelo usuário usando KNN
# def recommend_similar_products(user_id, k=5):
#     print(f"Recommending similar products for user {user_id}")
#     connection = sqlite3.connect('Banco_QuilOn')
#     cursor = connection.cursor()

#     # Consulta para recuperar as categorias mais buscadas pelo usuário
#     cursor.execute('''
#         SELECT conteudoBuscado, COUNT(*) as freq
#         FROM searched
#         WHERE idUsuario = ?
#         GROUP BY conteudoBuscado
#         ORDER BY freq DESC
#     ''', (user_id,))
#     user_categories = cursor.fetchall()
#     user_categories = [category[0] for category in user_categories]

#     if not user_categories:
#         print("No search history found for the user.")
#         connection.close()
#         return []

#     # Recuperar todas as categorias de produtos no banco de dados
#     cursor.execute('SELECT DISTINCT category FROM products')
#     all_categories = [row[0] for row in cursor.fetchall()]

#     # Verificar se todas as categorias buscadas pelo usuário estão na lista de todas as categorias
#     user_category_indices = encode_categories(user_categories, all_categories)

#     if not user_category_indices:
#         print("None of the user's searched categories match the available product categories.")
#         connection.close()
#         return []

#     # Criar um vetor de categorias dos produtos
#     cursor.execute('SELECT id, category FROM products')
#     products = cursor.fetchall()
#     product_ids = [product[0] for product in products]
#     product_categories = [product[1] for product in products]
#     product_category_indices = encode_categories(product_categories, all_categories)

#     # Treinar o modelo KNN
#     X = np.array(product_category_indices).reshape(-1, 1)
#     knn = NearestNeighbors(n_neighbors=k)
#     knn.fit(X)

#     # Encontrar os k produtos mais próximos das categorias mais buscadas pelo usuário
#     distances, indices = knn.kneighbors(np.array(user_category_indices).reshape(-1, 1))

#     recommended_product_ids = set()
#     for idx_list in indices:
#         for idx in idx_list:
#             recommended_product_ids.add(product_ids[idx])

#     # Recuperar os detalhes dos produtos recomendados
#     recommended_products = []
#     for product_id in recommended_product_ids:
#         cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
#         product = cursor.fetchone()
#         if product:
#             recommended_products.append(product)

#     connection.close()

#     print(f"Recommended products: {recommended_products}")
#     return recommended_products

# # Rota para recomendar produtos semelhantes ao usuário
# @app.route('/recommendations/<int:user_id>', methods=['GET'])
# def get_recommendations(user_id):
#     recommended_products = recommend_similar_products(user_id)
#     return jsonify({'recommended_products': recommended_products})
