from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

### --- IMAGENS DOS PRODUTOS ----###
PRODUCTS_FOLDER = 'uploads/products'
app.config['PRODUCTS_FOLDER'] = PRODUCTS_FOLDER
if not os.path.exists(PRODUCTS_FOLDER):
    os.makedirs(PRODUCTS_FOLDER)

### --- IMAGENS DOS USUARIOS ----###
USERS_FOLDER = 'uploads/users'
app.config['USERS_FOLDER'] = USERS_FOLDER
if not os.path.exists(USERS_FOLDER):
    os.makedirs(USERS_FOLDER)

### --- IMAGENS DOS QUILOMBOS ----###
QUILOMBOS_FOLDER = 'uploads/quilombos'
app.config['QUILOMBOS_FOLDER'] = QUILOMBOS_FOLDER
if not os.path.exists(QUILOMBOS_FOLDER):
    os.makedirs(QUILOMBOS_FOLDER)

### --- IMAGENS DOS INFORMATIVOS ----###
INFORMATIVE_FOLDER = 'uploads/informatives'
app.config['INFORMATIVE_FOLDER'] = INFORMATIVE_FOLDER
if not os.path.exists(INFORMATIVE_FOLDER):
    os.makedirs(INFORMATIVE_FOLDER)

# Rota para cadastrar imagens do produto
@app.route('/productImage/<int:product_id>', methods=['POST'])
def upload_image(product_id):
    if 'image' not in request.files:
        return "Nenhuma imagem encontrada na solicitação", 400

    image = request.files['image']
    product_folder = os.path.join(PRODUCTS_FOLDER, str(product_id))

    if not os.path.exists(product_folder):
        os.makedirs(product_folder)

    # Contar o número de imagens já presentes na pasta
    existing_images = [f for f in os.listdir(product_folder) if os.path.isfile(os.path.join(product_folder, f))]
    image_count = len(existing_images) + 1  # Nova imagem será numerada como próximo número

    # Salvar a imagem com o próximo número disponível
    image_path = os.path.join(product_folder, f"{image_count}.png")
    image.save(image_path)

    return "Imagem carregada com sucesso", 201

# Rota para chamar imagem
@app.route('/productImage/<int:product_id>/<int:image_index>', methods=['GET'])
def get_image(product_id, image_index):
    product_folder = os.path.join(PRODUCTS_FOLDER, str(product_id))
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']  # Adicione mais extensões se necessário
    
    for ext in image_extensions:
        image_path = os.path.join(product_folder, f"{image_index}{ext}")
        if os.path.exists(image_path):
            return send_file(image_path, mimetype=f'image/{ext[1:]}')
    
    return "Imagem não encontrada", 404

# Rota para obter o número total de imagens na pasta do produto
@app.route('/productImage/<int:product_id>/total', methods=['GET'])
def get_total_images(product_id):
    product_folder = os.path.join(PRODUCTS_FOLDER, str(product_id))
    if os.path.exists(product_folder):
        images = [filename for filename in os.listdir(product_folder) if os.path.isfile(os.path.join(product_folder, filename))]
        total_images = len(images)
        return jsonify({'total_images': total_images})
    else:
        return jsonify({'total_images': 0})


# Rota para cadastrar a imagem do usuário
@app.route('/userImage/<int:user_id>', methods=['POST'])
def upload_user_image(user_id):
    if 'image' not in request.files:
        return "Nenhuma imagem encontrada na solicitação", 400

    image = request.files['image']
    user_folder = os.path.join(USERS_FOLDER, str(user_id))

    # Criar a pasta do usuário se não existir
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    # Caminho da imagem, sempre substituindo a imagem existente
    image_path = os.path.join(user_folder, "profile.png")
    image.save(image_path)

    return "Imagem do usuário carregada com sucesso", 201

# Rota para chamar a imagem do usuário
@app.route('/userImage/<int:user_id>', methods=['GET'])
def get_user_image(user_id):
    user_folder = os.path.join(USERS_FOLDER, str(user_id))
    image_path = os.path.join(user_folder, "profile.png")
    
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    
    return "Imagem do usuário não encontrada", 404

# Rota para cadastrar a imagem do quilombo
@app.route('/quilomboImage/<int:quilombo_id>', methods=['POST'])
def upload_quilombo_image(quilombo_id):
    if 'image' not in request.files:
        return "Nenhuma imagem encontrada na solicitação", 400

    image = request.files['image']
    quilombo_folder = os.path.join(QUILOMBOS_FOLDER, str(quilombo_id))

    # Criar a pasta do quilombo se não existir
    if not os.path.exists(quilombo_folder):
        os.makedirs(quilombo_folder)

    # Caminho da imagem, sempre substituindo a imagem existente
    image_path = os.path.join(quilombo_folder, "quilombo.png")
    image.save(image_path)

    return "Imagem do quilombo carregada com sucesso", 201

# Rota para chamar a imagem do quilombo
@app.route('/quilomboImage/<int:quilombo_id>', methods=['GET'])
def get_quilombo_image(quilombo_id):
    quilombo_folder = os.path.join(QUILOMBOS_FOLDER, str(quilombo_id))
    image_path = os.path.join(quilombo_folder, "quilombo.png")
    
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    
    return "Imagem do quilombo não encontrada", 404


### --- PRODUTOS ----###

# Rota para cadastrar um produto
@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO products (title, category, description, production_time, price, stock, idUsuario)
        VALUES (:title, :category, :description, :production_time, :price, :stock, :idUsuario)
    ''', {
        'title': data['title'],
        'category': data['category'],
        'description': data['description'],
        'production_time': data['production_time'],
        'price': data['price'],
        'stock': data['stock'],
        'idUsuario': data['idUsuario']
    })
    connection.commit()
    product_id = cursor.lastrowid
    connection.close()
    return jsonify({'id': product_id}), 201

# Rota para listar todos os produtos com quantidade maior que 0
@app.route('/products', methods=['GET'])
def get_products():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE stock > 0')  # Filtra produtos com quantidade maior que 0
    products = cursor.fetchall()
    connection.close()
    return jsonify({'products': products})

# Rota para listar os IDs de todos os produtos
@app.route('/product-ids', methods=['GET'])
def get_product_ids():
    category = request.args.get('category')
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    if category:
        cursor.execute('SELECT id FROM products WHERE category = :category', {'category': category})
    else:
        cursor.execute('SELECT id FROM products')

    product_ids = [product[0] for product in cursor.fetchall()]
    connection.close()

    return jsonify(product_ids)

# Rota para obter os detalhes de um produto específico
@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE id = :product_id', {'product_id': product_id})
    product = cursor.fetchone()
    connection.close()

    if product:
        product_details = {
            'id': product[0],
            'title': product[1],
            'category': product[2],
            'description': product[3],
            'production_time': product[4],
            'price': product[5],
            'stock': product[6],
            'idUsuario': product[7] 
        }
        return jsonify(product_details)
    else:
        return jsonify({'error': 'Produto não encontrado'}), 404

# Rota para atualizar um produto
@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE products
        SET title = :title, category = :category, description = :description, production_time = :production_time, price = :price, stock = :stock
        WHERE id = :product_id
    ''', {
        'title': data['title'],
        'category': data['category'],
        'description': data['description'],
        'production_time': data['production_time'],
        'price': data['price'],
        'stock': data['stock'],
        'product_id': product_id
    })
    connection.commit()
    connection.close()
    return 'Produto atualizado com sucesso'

# Rota para excluir um produto
@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM products WHERE id = :product_id', {'product_id': product_id})
    connection.commit()
    connection.close()
    return 'Produto excluído com sucesso'

# Rota para obter todos os produtos de um usuário específico
@app.route('/products/<int:idUsuario>', methods=['GET'])
def get_products_by_user(idUsuario):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE idUsuario = :idUsuario', {'idUsuario': idUsuario})
    products = cursor.fetchall()
    connection.close()
    return jsonify({'products': products})

# Rota para obter os detalhes de um produto específico de um usuário
@app.route('/product/<int:idUsuario>/<int:product_id>', methods=['GET'])
def get_product_by_user(idUsuario, product_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE id = :product_id AND idUsuario = :idUsuario', {'product_id': product_id, 'idUsuario': idUsuario})
    product = cursor.fetchone()
    connection.close()

    if product:
        product_details = {
            'id': product[0],
            'title': product[1],
            'category': product[2],
            'description': product[3],
            'production_time': product[4],
            'price': product[5],
            'stock': product[6],
            'idUsuario': product[7]  # Incluindo idUsuario nos detalhes do produto
        }
        return jsonify(product_details)
    else:
        return jsonify({'error': 'Produto não encontrado'}), 404

# Rota para atualizar um produto de um usuário específico
@app.route('/product/<int:idUsuario>/<int:product_id>', methods=['PUT'])
def update_product_by_user(idUsuario, product_id):
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE products
        SET title = :title, category = :category, description = :description, production_time = :production_time, price = :price, stock = :stock
        WHERE id = :product_id AND idUsuario = :idUsuario
    ''', {
        'title': data['title'],
        'category': data['category'],
        'description': data['description'],
        'production_time': data['production_time'],
        'price': data['price'],
        'stock': data['stock'],
        'product_id': product_id,
        'idUsuario': idUsuario
    })
    connection.commit()
    connection.close()
    return 'Produto atualizado com sucesso'

# Rota para excluir um produto de um usuário específico
@app.route('/product/<int:idUsuario>/<int:product_id>', methods=['DELETE'])
def delete_product_by_user(idUsuario, product_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM products WHERE id = :product_id AND idUsuario = :idUsuario', {'product_id': product_id, 'idUsuario': idUsuario})
    connection.commit()
    connection.close()
    return 'Produto excluído com sucesso'


### --- USUARIOS ----###

# Rota para criar um novo usuário
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO user (nome, dataNasc, sexo, cpf, rg, celular, telefone, email, senha, representante)
        VALUES (:nome, :dataNasc, :sexo, :cpf, :rg, :celular, :telefone, :email, :senha, :representante)
    ''', {
        'nome': data['nome'],
        'dataNasc': data['dataNasc'],
        'sexo': data['sexo'],
        'cpf': data['cpf'],
        'rg': data['rg'],
        'celular': data['celular'],
        'telefone': data.get('telefone'),
        'email': data['email'],
        'senha': data['senha'],
        'representante': data.get('representante', 0)
    })
    connection.commit()

    user_id = cursor.lastrowid
    representante = data.get('representante', 0)
    
    connection.close()

    # Agora o valor de 'representante' também será retornado na resposta
    return jsonify({'idUsuario': user_id, 'representante': representante}), 201

# Rota para listar todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    connection.close()
    
    # Mapeia os resultados para um dicionário com nomes de coluna
    users_list = []
    for user in users:
        users_list.append({
            'idUsuario': user[0],
            'nome': user[1],
            'dataNasc': user[2],
            'sexo': user[3],
            'cpf': user[4],
            'rg': user[5],
            'celular': user[6],
            'telefone': user[7],
            'email': user[8],
            'senha': user[9],
            'representante': user[10]  # Novo campo
        })
    
    return jsonify({'users': users_list})

# Rota para obter os detalhes de um usuário específico
@app.route('/user/<int:idUsuario>', methods=['GET'])
def get_user(idUsuario):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user WHERE idUsuario = :idUsuario', {'idUsuario': idUsuario})
    user = cursor.fetchone()
    connection.close()

    if user:
        user_details = {
            'idUsuario': user[0],
            'nome': user[1],
            'dataNasc': user[2],
            'sexo': user[3],
            'cpf': user[4],
            'rg': user[5],
            'celular': user[6],
            'telefone': user[7],
            'email': user[8],
            'senha': user[9],
            'representante': user[10]  # Novo campo
        }
        return jsonify(user_details)
    else:
        return jsonify({'error': 'Usuário não encontrado'}), 404

# Rota para atualizar um usuário
@app.route('/user/<int:idUsuario>', methods=['PUT'])
def update_user(idUsuario):
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE user
        SET nome = :nome, dataNasc = :dataNasc, sexo = :sexo, cpf = :cpf, rg = :rg, celular = :celular, telefone = :telefone, email = :email, senha = :senha, representante = :representante
        WHERE idUsuario = :idUsuario
    ''', {
        'nome': data['nome'],
        'dataNasc': data['dataNasc'],
        'sexo': data['sexo'],
        'cpf': data['cpf'],
        'rg': data['rg'],
        'celular': data['celular'],
        'telefone': data.get('telefone'),
        'email': data['email'],
        'senha': data['senha'],
        'representante': data.get('representante', 0),  # Atualiza ou usa 0 como padrão
        'idUsuario': idUsuario
    })
    connection.commit()
    connection.close()
    return jsonify({'message': 'Usuário atualizado com sucesso'}), 200

# Rota para excluir um usuário
@app.route('/user/<int:idUsuario>', methods=['DELETE'])
def delete_user(idUsuario):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM user WHERE idUsuario = :idUsuario', {'idUsuario': idUsuario})
    connection.commit()
    connection.close()
    return jsonify({'message': 'Usuário excluído com sucesso'}), 200


### --- ENDEREÇOS ----###

# Rota para criar um novo endereço
@app.route('/address', methods=['POST'])
def create_address():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO address (idUsuario, endereco, bairro, numero, cidade, uf, complemento)
        VALUES (:idUsuario, :endereco, :bairro, :numero, :cidade, :uf, :complemento)
    ''', {
        'idUsuario': data['idUsuario'],
        'endereco': data['endereco'],
        'bairro': data['bairro'],
        'numero': data['numero'],
        'cidade': data['cidade'],
        'uf': data['uf'],
        'complemento': data.get('complemento')  # Complemento pode ser opcional
    })
    connection.commit()
    connection.close()
    return 'Endereço criado com sucesso', 201

# Rota para listar todos os endereços
@app.route('/addresses', methods=['GET'])
def get_addresses():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM address')
    addresses = cursor.fetchall()
    connection.close()
    return jsonify({'addresses': addresses})

# Rota para obter os detalhes de um endereço específico
@app.route('/address/<int:idEndereco>', methods=['GET'])
def get_address(idEndereco):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM address WHERE idEndereco = :idEndereco', {'idEndereco': idEndereco})
    address = cursor.fetchone()
    connection.close()

    if address:
        address_details = {
            'idEndereco': address[0],
            'idUsuario': address[1],
            'endereco': address[2],
            'bairro': address[3],
            'numero': address[4],
            'cidade': address[5],
            'uf': address[6],
            'complemento': address[7]
        }
        return jsonify(address_details)
    else:
        return jsonify({'error': 'Endereço não encontrado'}), 404

# Rota para atualizar um endereço
@app.route('/address/<int:idEndereco>', methods=['PUT'])
def update_address(idEndereco):
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE address
        SET idUsuario = :idUsuario, endereco = :endereco, bairro = :bairro, numero = :numero, cidade = :cidade, uf = :uf, complemento = :complemento
        WHERE idEndereco = :idEndereco
    ''', {
        'idUsuario': data['idUsuario'],
        'endereco': data['endereco'],
        'bairro': data['bairro'],
        'numero': data['numero'],
        'cidade': data['cidade'],
        'uf': data['uf'],
        'complemento': data.get('complemento'),
        'idEndereco': idEndereco
    })
    connection.commit()
    connection.close()
    return 'Endereço atualizado com sucesso'

# Rota para excluir um endereço
@app.route('/address/<int:idEndereco>', methods=['DELETE'])
def delete_address(idEndereco):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM address WHERE idEndereco = :idEndereco', {'idEndereco': idEndereco})
    connection.commit()
    connection.close()
    return 'Endereço excluído com sucesso'


### --- QUILOMBOS ----###

# Rota para cadastrar um novo quilombo
@app.route('/quilombo', methods=['POST'])
def create_quilombo():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO quilombo (idUsuario, name, certificationNumber, latAndLng, kmAndComplement)
        VALUES (:idUsuario, :name, :certificationNumber, :latAndLng, :kmAndComplement)
    ''', {
        'idUsuario': data['idUsuario'],  # Adicionando o idUsuario
        'name': data['name'],
        'certificationNumber': data['certificationNumber'],
        'latAndLng': data['latAndLng'],
        'kmAndComplement': data.get('kmAndComplement')  # Complemento de km é opcional
    })
    connection.commit()
    connection.close()
    return 'Quilombo cadastrado com sucesso', 201

# Rota para obter os detalhes de todos os quilombos
@app.route('/quilombos', methods=['GET'])
def get_quilombos():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM quilombo')
    quilombos = cursor.fetchall()
    connection.close()
    return jsonify({'quilombos': quilombos})

# Rota para obter os dados de um quilombo pelo ID do usuário
@app.route('/quilombouser/<int:id_usuario>', methods=['GET'])
def get_quilombo_by_user(id_usuario):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM quilombo WHERE idUsuario = ?', (id_usuario,))
    quilombo = cursor.fetchone()
    connection.close()
    
    if quilombo:
        return jsonify({'quilombo': quilombo}), 200
    else:
        return jsonify({'message': 'Quilombo não encontrado para o ID do usuário fornecido'}), 404

# Rota para atualizar um quilombo
@app.route('/quilombo/<int:idQuilombo>', methods=['PUT'])
def update_quilombo(idQuilombo):
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        cursor.execute('''
            UPDATE quilombo
            SET name = :name,
                certificationNumber = :certificationNumber,
                latAndLng = :latAndLng,
                kmAndComplement = :kmAndComplement
            WHERE idQuilombo = :idQuilombo
        ''', {
            'name': data['name'],
            'certificationNumber': data['certificationNumber'],
            'latAndLng': data['latAndLng'],
            'kmAndComplement': data.get('kmAndComplement', ''),  # kmAndComplement é opcional
            'idQuilombo': idQuilombo
        })

        if cursor.rowcount == 0:
            return jsonify({'error': 'Quilombo não encontrado'}), 404

        connection.commit()
        return jsonify({'message': 'Dados do quilombo atualizados com sucesso'}), 200

    except sqlite3.Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()

# Rota para deletar um quilombo
@app.route('/quilombo/<int:idQuilombo>', methods=['DELETE'])
def delete_quilombo(idQuilombo):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        cursor.execute('DELETE FROM quilombo WHERE idQuilombo = ?', (idQuilombo,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Quilombo não encontrado'}), 404

        connection.commit()
        return jsonify({'message': 'Quilombo deletado com sucesso'}), 200

    except sqlite3.Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()


### --- BUSCAS ----###

# Rota para cadastrar uma nova busca
@app.route('/search', methods=['POST'])
def create_search():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO searched (idUsuario, conteudoBuscado)
        VALUES (:idUsuario, :conteudoBuscado)
    ''', {
        'idUsuario': data['idUsuario'],
        'conteudoBuscado': data['conteudoBuscado']
    })
    connection.commit()
    connection.close()
    return 'Busca cadastrada com sucesso', 201 

# Rota para cadastrar várias buscas de uma vez
@app.route('/searches', methods=['POST'])
def create_searches():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Os dados devem estar em formato de lista de buscas JSON'}), 400

    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    try:
        for search in data:
            cursor.execute('''
                INSERT INTO searched (idUsuario, conteudoBuscado)
                VALUES (?, ?)
            ''', (search['idUsuario'], search['conteudoBuscado']))
    except sqlite3.IntegrityError:
        connection.rollback()
        return jsonify({'error': 'Erro ao inserir as buscas'}), 500
    else:
        connection.commit()
        connection.close()
        return 'Buscas cadastradas com sucesso', 201


### --- COMPRAS ----###

# Rota para cadastrar uma nova compra
@app.route('/purchase', methods=['POST'])
def create_purchase():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        # Iniciar a transação
        cursor.execute('BEGIN')

        # Inserindo na tabela purchase
        cursor.execute('''
            INSERT INTO purchase (userId, addressId, totalValue, purchaseDate)
            VALUES (:userId, :addressId, :totalValue, :purchaseDate)
        ''', {
            'userId': data['userId'],
            'addressId': data['addressId'],
            'totalValue': data['totalValue'],
            'purchaseDate': data['purchaseDate'],
        })
        
        purchase_id = cursor.lastrowid  # ID da compra recém-criada

        # Inserindo os itens da compra e atualizando o estoque
        for product_id, quantity in zip(data['productIds'], data['quantities']):
            cursor.execute('''
                INSERT INTO purchase_items (purchaseId, productId, quantity)
                VALUES (:purchaseId, :productId, :quantity)
            ''', {
                'purchaseId': purchase_id,
                'productId': product_id,
                'quantity': quantity,
            })

            # Atualizar o estoque do produto
            cursor.execute('''
                UPDATE products
                SET stock = stock - :quantity
                WHERE id = :productId
            ''', {
                'quantity': quantity,
                'productId': product_id,
            })

        # Confirmar a transação
        connection.commit()
        return jsonify({'id': purchase_id}), 201

    except Exception as e:
        # Reverter a transação em caso de erro
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()

# Rota para listar todas as compras
@app.route('/purchases', methods=['GET'])
def get_purchases():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM purchase')
    purchases = cursor.fetchall()
    connection.close()

    # Formatar os resultados para incluir os itens da compra
    purchase_list = []
    for purchase in purchases:
        cursor.execute('SELECT * FROM purchase_items WHERE purchaseId = ?', (purchase[0],))
        items = cursor.fetchall()
        purchase_list.append({
            'id': purchase[0],
            'userId': purchase[1],
            'addressId': purchase[2],
            'totalValue': purchase[3],
            'purchaseDate': purchase[4],
            'items': [{'productId': item[1], 'quantity': item[2]} for item in items]
        })

    return jsonify({'purchases': purchase_list})

# Rota para obter os detalhes de uma compra específica
@app.route('/purchase/<int:purchase_id>', methods=['GET'])
def get_purchase(purchase_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    
    # Obter detalhes da compra
    cursor.execute('SELECT * FROM purchase WHERE id = ?', (purchase_id,))
    purchase = cursor.fetchone()

    if purchase:
        cursor.execute('SELECT * FROM purchase_items WHERE purchaseId = ?', (purchase_id,))
        items = cursor.fetchall()
        
        purchase_details = {
            'id': purchase[0],
            'userId': purchase[1],
            'addressId': purchase[2],
            'totalValue': purchase[3],
            'purchaseDate': purchase[4],
            'items': [{'productId': item[1], 'quantity': item[2]} for item in items]
        }
        connection.close()
        return jsonify(purchase_details)
    else:
        connection.close()
        return jsonify({'error': 'Compra não encontrada'}), 404

# Rota para atualizar uma compra
@app.route('/purchase/<int:purchase_id>', methods=['PUT'])
def update_purchase(purchase_id):
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    # Atualizar informações da compra
    cursor.execute('''
        UPDATE purchase
        SET userId = :userId, addressId = :addressId, totalValue = :totalValue, purchaseDate = :purchaseDate
        WHERE id = :purchase_id
    ''', {
        'userId': data['userId'],
        'addressId': data['addressId'],
        'totalValue': data['totalValue'],
        'purchaseDate': data['purchaseDate'],
        'purchase_id': purchase_id
    })

    # Excluir itens antigos
    cursor.execute('DELETE FROM purchase_items WHERE purchaseId = ?', (purchase_id,))

    # Inserir novos itens da compra
    for product_id, quantity in zip(data['productIds'], data['quantities']):
        cursor.execute('''
            INSERT INTO purchase_items (purchaseId, productId, quantity)
            VALUES (:purchaseId, :productId, :quantity)
        ''', {
            'purchaseId': purchase_id,
            'productId': product_id,
            'quantity': quantity,
        })

    connection.commit()
    connection.close()
    return jsonify({'message': 'Compra atualizada com sucesso'}), 200

# Rota para excluir uma compra
@app.route('/purchase/<int:purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    # Excluir itens da compra
    cursor.execute('DELETE FROM purchase_items WHERE purchaseId = ?', (purchase_id,))
    # Excluir a compra
    cursor.execute('DELETE FROM purchase WHERE id = ?', (purchase_id,))
    connection.commit()
    connection.close()
    return jsonify({'message': 'Compra excluída com sucesso'}), 200

# Rota para cadastrar várias compras de uma vez
@app.route('/purchases', methods=['POST'])
def create_multiple_purchases():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        # Iniciar a transação
        cursor.execute('BEGIN')

        # Loop para cadastrar múltiplas compras
        for purchase in data['purchases']:
            # Inserindo na tabela purchase
            cursor.execute('''
                INSERT INTO purchase (userId, addressId, totalValue, purchaseDate)
                VALUES (:userId, :addressId, :totalValue, :purchaseDate)
            ''', {
                'userId': purchase['userId'],
                'addressId': purchase['addressId'],
                'totalValue': purchase['totalValue'],
                'purchaseDate': purchase['purchaseDate'],
            })
            
            purchase_id = cursor.lastrowid  # ID da compra recém-criada

            # Inserindo os itens da compra e atualizando o estoque
            for product_id, quantity in zip(purchase['productIds'], purchase['quantities']):
                cursor.execute('''
                    INSERT INTO purchase_items (purchaseId, productId, quantity)
                    VALUES (:purchaseId, :productId, :quantity)
                ''', {
                    'purchaseId': purchase_id,
                    'productId': product_id,
                    'quantity': quantity,
                })

                # Atualizar o estoque do produto
                cursor.execute('''
                    UPDATE products
                    SET stock = stock - :quantity
                    WHERE id = :productId
                ''', {
                    'quantity': quantity,
                    'productId': product_id,
                })

        # Confirmar a transação
        connection.commit()
        return jsonify({'message': 'Compras cadastradas com sucesso!'}), 201

    except Exception as e:
        # Reverter a transação em caso de erro
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()


### --- VENDAS ----###

# Rota para obter os produtos vendidos por um usuario
@app.route('/vendas/<int:idUsuario>', methods=['GET'])
def get_sold_products(idUsuario):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        # Consulta para buscar os produtos do usuário e as informações de compra
        cursor.execute('''
            SELECT 
                p.id,                -- ID do produto
                p.title,             -- Nome do produto
                p.category,          -- Categoria do produto
                pi.quantity,         -- Quantidade vendida
                pur.purchaseDate,    -- Data da compra
                (p.price * pi.quantity) AS totalSaleValue  -- Valor total da venda (preço * quantidade)
            FROM 
                products AS p
            INNER JOIN 
                purchase_items AS pi ON p.id = pi.productId
            INNER JOIN 
                purchase AS pur ON pi.purchaseId = pur.id
            WHERE 
                p.idUsuario = ?
        ''', (idUsuario,))

        # Buscar os resultados
        sold_products = cursor.fetchall()

        if not sold_products:
            return jsonify({'message': 'Nenhum produto vendido encontrado para este usuário.'}), 404

        # Organizar os resultados em uma lista de dicionários
        result = []
        for product in sold_products:
            result.append({
                'productId': product[0],         # ID do produto
                'title': product[1],             # Nome do produto
                'category': product[2],          # Categoria
                'quantity': product[3],          # Quantidade vendida
                'purchaseDate': product[4],      # Data da compra
                'totalSaleValue': product[5]     # Valor total da venda
            })

        return jsonify(result), 200

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()


### --- INFORMATIVO ----###

@app.route('/informative', methods=['POST'])
def upsert_informative():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        # Verificar se já existe um informativo para o idQuilombo fornecido
        cursor.execute('''
            SELECT idInformative FROM communityInformative WHERE idQuilombo = :idQuilombo
        ''', {'idQuilombo': data['idQuilombo']})
        
        result = cursor.fetchone()

        if result:
            # Se existir, atualizar o informativo existente
            cursor.execute('''
                UPDATE communityInformative
                SET population = :population, history = :history
                WHERE idQuilombo = :idQuilombo
            ''', {
                'population': data['population'],
                'history': data['history'],
                'idQuilombo': data['idQuilombo']
            })
            connection.commit()
            return jsonify({'message': 'Informativo atualizado com sucesso'}), 200
        else:
            # Se não existir, criar um novo informativo
            cursor.execute(''' 
                INSERT INTO communityInformative (idQuilombo, population, history)
                VALUES (:idQuilombo, :population, :history)
            ''', {
                'idQuilombo': data['idQuilombo'],
                'population': data['population'],
                'history': data['history']
            })
            connection.commit()
            informative_id = cursor.lastrowid
            return jsonify({'idInformative': informative_id, 'message': 'Informativo criado com sucesso'}), 201

    except sqlite3.Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()

# Rota para cadastrar imagens do informativo
@app.route('/informativeImages/<int:quilombo_id>', methods=['POST'])
def upload_informative_images(quilombo_id):
    if 'images' not in request.files:
        return "Nenhuma imagem encontrada na solicitação", 400

    images = request.files.getlist('images')
    if len(images) > 3:
        return "Você pode enviar no máximo 3 imagens", 400

    informative_folder = os.path.join(INFORMATIVE_FOLDER, str(quilombo_id))
    
    # Cria a pasta do quilombo se não existir
    if not os.path.exists(informative_folder):
        os.makedirs(informative_folder)

    # Salvar as imagens
    for index, image in enumerate(images):
        if image.filename == '':
            return "Nenhuma imagem selecionada", 400
        
        # Define o caminho para salvar a imagem
        image_path = os.path.join(informative_folder, f"{index + 1}.png")  # Renomeia como 1.png, 2.png, 3.png
        image.save(image_path)

    return "Imagens carregadas com sucesso", 201

# Rota para obter os dados do informativo de uma comunidade pelo idQuilombo
@app.route('/informative/<int:idQuilombo>', methods=['GET'])
def get_informative(idQuilombo):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    try:
        cursor.execute('''
            SELECT population, history FROM communityInformative WHERE idQuilombo = :idQuilombo
        ''', {'idQuilombo': idQuilombo})
        
        result = cursor.fetchone()

        if result:
            return jsonify({
                'population': result[0],
                'history': result[1]
            }), 200
        else:
            return jsonify({'error': 'Informativo não encontrado'}), 404

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500

    finally:
        connection.close()

# Rota para obter imagem específica do informativo
@app.route('/informativeImages/<int:quilombo_id>/<int:image_index>', methods=['GET'])
def get_informative_image(quilombo_id, image_index):
    informative_folder = os.path.join(INFORMATIVE_FOLDER, str(quilombo_id))
    image_extensions = ['.png', '.jpg', '.jpeg']  # Adicione mais extensões se necessário
    
    # Verifica a existência da imagem nas possíveis extensões
    for ext in image_extensions:
        image_path = os.path.join(informative_folder, f"{image_index}{ext}")
        if os.path.exists(image_path):
            return send_file(image_path, mimetype=f'image/{ext[1:]}')
    
    return "Imagem não encontrada", 404

### --- LOGIN ----###

# Rota para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verificar se o email e a senha correspondem a um usuário no banco de dados
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT idUsuario, email, senha, representante FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()
    connection.close()

    if user and user[2] == password:
        # Credenciais válidas, login bem-sucedido
        return jsonify({'idUsuario': user[0], 'email': user[1], 'representante': user[3]}), 200
    else:
        # Credenciais inválidas, login falhou
        return jsonify({'error': 'Credenciais inválidas'}), 401
   

### --- RECOMENDAÇÃO / IA ----###

# ------  RECOMENDAÇÃO SEM KNN ------ #
# Função para recomendar produtos com base nas categorias mais pesquisadas pelo usuário
def recommend_similar_products(user_id):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()

    # Consulta para recuperar as categorias mais buscadas pelo usuário
    cursor.execute(''' 
        SELECT conteudoBuscado, COUNT(*) as freq 
        FROM searched 
        WHERE idUsuario = ? 
        GROUP BY conteudoBuscado 
        ORDER BY freq DESC 
    ''', (user_id,))
    categories = cursor.fetchall()

    # Recuperar produtos relacionados às categorias mais buscadas, excluindo os com quantidade 0
    recommended_products = []
    for category, _ in categories:
        cursor.execute(''' 
            SELECT * FROM products 
            WHERE category = ? AND stock > 0 
        ''', (category,))
        products = cursor.fetchall()
        recommended_products.extend(products)

    connection.close()
    return recommended_products

# Rota para recomendar produtos semelhantes ao usuário
@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    recommended_products = recommend_similar_products(user_id)
    return jsonify({'recommended_products': recommended_products})


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
