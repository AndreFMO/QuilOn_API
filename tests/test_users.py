import unittest
import json
from io import BytesIO
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API import app

class UserRoutesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuração inicial do banco de dados"""
        # Criar um banco de dados em memória para testes
        cls.app = app.test_client()
        cls.app.testing = True

    def test_create_user(self):
        """Teste para criar um novo usuário"""
        data = {
            'nome': 'João Silva',
            'dataNasc': '1985-10-15',
            'sexo': 'M',
            'cpf': '12345678900',
            'rg': 'MG1234567',
            'celular': '31987654321',
            'telefone': '31987654321',
            'email': 'joao@example.com',
            'senha': 'senha123',
            'representante': 1
        }
        
        response = self.app.post('/user', data=json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertIn('idUsuario', json_data)
        self.assertEqual(json_data['representante'], 1)

    def test_get_users(self):
        """Teste para listar todos os usuários"""
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIsInstance(json_data['users'], list)

    def test_get_user(self):
        """Teste para obter os detalhes de um usuário específico"""
        # Criar um usuário antes de testar
        data = {
            'nome': 'Maria Souza',
            'dataNasc': '1990-05-21',
            'sexo': 'F',
            'cpf': '98765432100',
            'rg': 'SP9876543',
            'celular': '31987654322',
            'telefone': '31987654322',
            'email': 'maria@example.com',
            'senha': 'senha123',
            'representante': 0
        }
        response = self.app.post('/user', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(response.data)['idUsuario']

        response = self.app.get(f'/user/{user_id}')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['idUsuario'], user_id)
        self.assertEqual(json_data['nome'], 'Maria Souza')

    def test_update_user(self):
        """Teste para atualizar um usuário"""
        data = {
            'nome': 'Carlos Pereira',
            'dataNasc': '1987-07-30',
            'sexo': 'M',
            'cpf': '12398765432',
            'rg': 'MG9876543',
            'celular': '31987654323',
            'telefone': '31987654323',
            'email': 'carlos@example.com',
            'senha': 'novaSenha123',
            'representante': 1
        }
        # Criando o usuário para atualizar
        response = self.app.post('/user', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(response.data)['idUsuario']
        
        update_data = {
            'nome': 'Carlos Pereira Atualizado',
            'dataNasc': '1987-07-30',
            'sexo': 'M',
            'cpf': '12398765432',
            'rg': 'MG9876543',
            'celular': '31987654323',
            'telefone': '31987654323',
            'email': 'carlos_atualizado@example.com',
            'senha': 'senhaAtualizada123',
            'representante': 1
        }
        
        response = self.app.put(f'/user/{user_id}', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], 'Usuário atualizado com sucesso')

    def test_delete_user(self):
        """Teste para excluir um usuário"""
        data = {
            'nome': 'Paulo Silva',
            'dataNasc': '1995-08-14',
            'sexo': 'M',
            'cpf': '12311223344',
            'rg': 'SP1122334',
            'celular': '31987654324',
            'telefone': '31987654324',
            'email': 'paulo@example.com',
            'senha': 'senhaPaulo123',
            'representante': 0
        }
        response = self.app.post('/user', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(response.data)['idUsuario']

        response = self.app.delete(f'/user/{user_id}')
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data['message'], 'Usuário excluído com sucesso')

    def test_upload_user_image(self):
        """Teste para fazer upload da imagem de um usuário"""
        # Criando um usuário para associar a imagem
        data = {
            'nome': 'Lucas Almeida',
            'dataNasc': '1993-11-21',
            'sexo': 'M',
            'cpf': '99987654321',
            'rg': 'RJ1231234',
            'celular': '31987654325',
            'telefone': '31987654325',
            'email': 'lucas@example.com',
            'senha': 'senhaLucas123',
            'representante': 0
        }
        response = self.app.post('/user', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(response.data)['idUsuario']

        # Fazendo upload da imagem
        with open('tests/test_image.png', 'wb') as f:
            f.write(b'fakeimagecontent')
        
        with open('tests/test_image.png', 'rb') as img_file:
            response = self.app.post(
                f'/userImage/{user_id}',
                data={'image': (img_file, 'profile.png')},
                content_type='multipart/form-data'
            )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('Imagem do usuário carregada com sucesso', response.data.decode())

    def test_get_user_image(self):
        """Teste para obter a imagem de um usuário"""
        data = {
            'nome': 'Giovana Costa',
            'dataNasc': '1994-03-10',
            'sexo': 'F',
            'cpf': '11122334455',
            'rg': 'PR9988776',
            'celular': '31987654326',
            'telefone': '31987654326',
            'email': 'giovana@example.com',
            'senha': 'senhaGiovana123',
            'representante': 0
        }
        response = self.app.post('/user', data=json.dumps(data), content_type='application/json')
        user_id = json.loads(response.data)['idUsuario']

        response = self.app.get(f'/userImage/{user_id}')
        self.assertEqual(response.status_code, 404)  # Caso a imagem não tenha sido carregada ainda

if __name__ == '__main__':
    unittest.main()
