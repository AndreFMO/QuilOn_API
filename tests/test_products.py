import unittest
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API import app

class ProductApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.client.testing = True

    def setUp(self):
        # Pode ser necessário limpar o banco de dados antes de cada teste
        # Isso pode ser feito criando uma tabela temporária ou utilizando um banco de dados de teste
        pass

    def test_create_product(self):
        data = {
            "title": "Produto Teste",
            "category": "Categoria Teste",
            "description": "Descrição Teste",
            "production_time": "2024-11-01",
            "price": 100.0,
            "stock": 10,
            "idUsuario": 1
        }
        
        response = self.client.post('/product', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        response_json = json.loads(response.data)
        self.assertIn('id', response_json)

    def test_get_products(self):
        response = self.client.get('/products')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertIn('products', response_json)

    def test_get_product_by_id(self):
        # Primeiro, crie um produto (você pode usar o endpoint '/product' ou diretamente no banco de dados)
        product_data = {
            'title': 'Test Product',
            'category': 'Test Category',
            'description': 'Test Description',
            'production_time': '2024-12-01',
            'price': 100.0,
            'stock': 10,
            'idUsuario': 1
        }
        
        # Envie uma requisição POST para criar o produto
        response = self.client.post('/product', json=product_data)
        
        # Verifique se a criação do produto foi bem-sucedida
        self.assertEqual(response.status_code, 201)
        
        # Pegue o ID do produto criado
        product_id = response.json['id']

        # Agora, busque o produto criado pelo ID
        response = self.client.get(f'/product/{product_id}')
        
        # Verifique se a resposta é 200 e o produto retornado é o correto
        self.assertEqual(response.status_code, 200)
        product = response.json
        self.assertEqual(product['title'], 'Test Product')
        self.assertEqual(product['category'], 'Test Category')
        self.assertEqual(product['description'], 'Test Description')
        self.assertEqual(product['price'], 100.0)

    def test_update_product(self):
        product_id = 1  # Altere conforme um ID válido
        data = {
            "title": "Produto Atualizado",
            "category": "Categoria Atualizada",
            "description": "Descrição Atualizada",
            "production_time": "2024-11-02",
            "price": 120.0,
            "stock": 15
        }
        
        response = self.client.put(f'/product/{product_id}', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Produto atualizado com sucesso', response.data.decode())

    def test_delete_product(self):
        product_id = 1  # Altere conforme um ID válido
        response = self.client.delete(f'/product/{product_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Produto excluído com sucesso', response.data.decode())

    def test_upload_image(self):
        product_id = 1  # Altere conforme um ID válido

        # Usando o caminho correto da imagem na pasta 'img'
        image_path = 'img/quilon.png'

        # Verifica se o arquivo existe antes de tentar abrir
        if not os.path.exists(image_path):
            self.fail(f"Arquivo de imagem não encontrado: {image_path}")

        # Usando o 'with' para garantir que o arquivo será fechado corretamente após o uso
        with open(image_path, 'rb') as image_file:
            image_data = {
                'image': (image_file, 'quilon.png')  # Ajuste para o caminho correto
            }
            response = self.client.post(f'/productImage/{product_id}', data=image_data, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 201)
        self.assertIn('Imagem carregada com sucesso', response.data.decode())

    def test_get_total_images(self):
        product_id = 1  # Altere conforme um ID válido
        response = self.client.get(f'/productImage/{product_id}/total')
        self.assertEqual(response.status_code, 200)
        response_json = json.loads(response.data)
        self.assertIn('total_images', response_json)

    def test_get_image(self):
        product_id = 1  # Altere conforme um ID válido
        image_index = 1  # Altere conforme o índice da imagem
        response = self.client.get(f'/productImage/{product_id}/{image_index}')
        self.assertEqual(response.status_code, 200)
        # A imagem será retornada, por isso você pode testar o tipo de conteúdo (mimetype) aqui.

    def tearDown(self):
        # Limpeza após o teste, se necessário (exemplo: remover arquivos, etc)
        pass

    @classmethod
    def tearDownClass(cls):
        # Limpeza após todos os testes, caso necessário
        pass


if __name__ == '__main__':
    unittest.main()
