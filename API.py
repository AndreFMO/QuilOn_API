from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Função para criar a tabela de produtos no banco de dados SQLite
def create_table():
    connection = sqlite3.connect('Banco_products')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            production_time INTEGER NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

# Rota para chamar imagem
@app.route('/upload/<image_name>', methods=['GET'])
def get_image(image_name):
    # Caminho para a pasta uploads
    uploads_path = 'uploads'
    
    # Verifica a extensão da imagem na pasta
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']  # Adicione mais extensões se necessário
    
    for ext in image_extensions:
        image_path = os.path.join(uploads_path, f"{image_name}{ext}")
        if os.path.exists(image_path):
            return send_file(image_path, mimetype=f'image/{ext[1:]}')
    
    return "Imagem não encontrada", 404


# Rota para criar um novo produto
@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    connection = sqlite3.connect('Banco_products')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO products (title, category, description, production_time, price, stock)
        VALUES (:title, :category, :description, :production_time, :price, :stock)
    ''', {
        'title': data['title'],
        'category': data['category'],
        'description': data['description'],
        'production_time': data['production_time'],
        'price': data['price'],
        'stock': data['stock']
    })
    connection.commit()
    return 'Produto criado com sucesso', 201
    


# Rota para listar todos os produtos
@app.route('/products', methods=['GET'])
def get_products():
    connection = sqlite3.connect('Banco_products')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    connection.close()
    return jsonify({'products': products})


# Rota para listar os IDs de todos os produtos
@app.route('/product-ids', methods=['GET'])
def get_product_ids():
    category = request.args.get('category')
    connection = sqlite3.connect('Banco_products')
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
    connection = sqlite3.connect('Banco_products')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM products WHERE id = :product_id', {'product_id': product_id})
    product = cursor.fetchone()
    connection.close()

    if product:
        # Retorna os detalhes do produto se encontrado
        product_details = {
            'id': product[0],
            'title': product[1],
            'category': product[2],
            'description': product[3],
            'production_time': product[4],
            'price': product[5],
            'stock': product[6]
        }
        return jsonify(product_details)
    else:
        # Retorna uma mensagem de erro se o produto não for encontrado
        return jsonify({'error': 'Produto não encontrado'}), 404


# Rota para atualizar um produto
@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    connection = sqlite3.connect('Banco_products')
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
    connection = sqlite3.connect('Banco_products')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM products WHERE id = :product_id', {'product_id': product_id})
    connection.commit()
    connection.close()
    return 'Produto excluído com sucesso'

if __name__ == '__main__':
    create_table()  # Certifica-se de que a tabela existe antes de iniciar o aplicativo
    app.run(debug=True, host="0.0.0.0", port=5000)

