from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOADS_FOLDER = 'uploads'

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

# Rota para chamar imagem
@app.route('/upload/<int:product_id>/<int:image_index>', methods=['GET'])
def get_image(product_id, image_index):
    product_folder = os.path.join(UPLOADS_FOLDER, str(product_id))
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']  # Adicione mais extensões se necessário
    
    for ext in image_extensions:
        image_path = os.path.join(product_folder, f"{image_index}{ext}")
        if os.path.exists(image_path):
            return send_file(image_path, mimetype=f'image/{ext[1:]}')
    
    return "Imagem não encontrada", 404

# Rota para obter o número total de imagens na pasta do produto
@app.route('/upload/<int:product_id>/total', methods=['GET'])
def get_total_images(product_id):
    product_folder = os.path.join(UPLOADS_FOLDER, str(product_id))
    if os.path.exists(product_folder):
        images = [filename for filename in os.listdir(product_folder) if os.path.isfile(os.path.join(product_folder, filename))]
        total_images = len(images)
        return jsonify({'total_images': total_images})
    else:
        return jsonify({'total_images': 0})

# Rota para criar um novo produto
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
        'idUsuario': data['idUsuario']  # Capturando o idUsuario do JSON
    })
    connection.commit()
    connection.close()
    return 'Produto criado com sucesso', 201

# Rota para listar todos os produtos
@app.route('/products', methods=['GET'])
def get_products():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products')
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

# Rotas CRUD para a tabela user

# Rota para criar um novo usuário
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO user (nome, dataNasc, sexo, cpf, rg, celular, telefone, email, senha)
        VALUES (:nome, :dataNasc, :sexo, :cpf, :rg, :celular, :telefone, :email, :senha)
    ''', {
        'nome': data['nome'],
        'dataNasc': data['dataNasc'],
        'sexo': data['sexo'],
        'cpf': data['cpf'],
        'rg': data['rg'],
        'celular': data['celular'],
        'telefone': data.get('telefone'),  # Telefone pode ser opcional
        'email': data['email'],
        'senha': data['senha']
    })
    connection.commit()
    
    user_id = cursor.lastrowid  # Obtendo o ID do usuário recém-criado
    connection.close()
    
    return jsonify({'idUsuario': user_id}), 201

# Rota para listar todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    connection.close()
    return jsonify({'users': users})

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
            'senha': user[9]
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
        SET nome = :nome, dataNasc = :dataNasc, sexo = :sexo, cpf = :cpf, rg = :rg, celular = :celular, telefone = :telefone, email = :email, senha = :senha
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
        'idUsuario': idUsuario
    })
    connection.commit()
    connection.close()
    return 'Usuário atualizado com sucesso'

# Rota para excluir um usuário
@app.route('/user/<int:idUsuario>', methods=['DELETE'])
def delete_user(idUsuario):
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM user WHERE idUsuario = :idUsuario', {'idUsuario': idUsuario})
    connection.commit()
    connection.close()
    return 'Usuário excluído com sucesso'

# Rotas CRUD para a tabela address

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

# Rota para login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Verificar se o email e a senha correspondem a um usuário no banco de dados
    connection = sqlite3.connect('Banco_QuilOn')
    cursor = connection.cursor()
    cursor.execute('SELECT idUsuario, email, senha FROM user WHERE email = ?', (email,))
    user = cursor.fetchone()
    connection.close()

    if user and user[2] == password:
        # Credenciais válidas, login bem-sucedido
        return jsonify({'idUsuario': user[0], 'email': user[1]}), 200
    else:
        # Credenciais inválidas, login falhou
        return jsonify({'error': 'Credenciais inválidas'}), 401


if __name__ == '__main__':
    create_tables()  # Certifica-se de que as tabelas existem antes de iniciar o aplicativo
    app.run(debug=True, host="0.0.0.0", port=5000)
