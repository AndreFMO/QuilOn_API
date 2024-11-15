import os
import unittest
import json
from io import BytesIO
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API import app

class QuilombosTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configurações antes de todos os testes."""
        cls.quilombos_folder = 'uploads/quilombos'
        # Criar a pasta temporária de uploads, se não existir
        if not os.path.exists(cls.quilombos_folder):
            os.makedirs(cls.quilombos_folder)

    def setUp(self):
        """Configurações antes de cada teste."""
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        """Não faz nenhuma limpeza, preserva a pasta e arquivos."""
        pass  # Nada será removido após o teste

    def test_create_quilombo(self):
        """Teste para criar um novo quilombo."""
        data = {
            'idUsuario': 1,
            'name': 'Quilombo Teste',
            'certificationNumber': '12345',
            'latAndLng': '10.000,-20.000',
            'kmAndComplement': 'KM 10'
        }
        response = self.app.post('/quilombo', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Quilombo cadastrado com sucesso', response.data.decode('utf-8'))

    def test_get_quilombos(self):
        """Teste para obter todos os quilombos."""
        response = self.app.get('/quilombos')
        self.assertEqual(response.status_code, 200)
        self.assertIn('quilombos', response.data.decode('utf-8'))

    def test_get_quilombo_by_user(self):
        """Teste para obter quilombo por ID do usuário."""
        user_id = 1
        response = self.app.get(f'/quilombouser/{user_id}')
        if response.status_code == 200:
            self.assertIn('quilombo', response.data.decode('utf-8'))
        else:
            self.assertIn('Quilombo não encontrado', response.data.decode('utf-8'))

    def test_update_quilombo(self):
        """Teste para atualizar um quilombo."""
        quilombo_id = 1  # Assumindo que um quilombo com esse ID existe
        data = {
            'name': 'Novo Nome',
            'certificationNumber': '54321',
            'latAndLng': '20.000,-30.000',
            'kmAndComplement': 'KM 20'
        }
        response = self.app.put(f'/quilombo/{quilombo_id}', data=json.dumps(data), content_type='application/json')
        
        if response.status_code == 200:
            self.assertIn('Dados do quilombo atualizados com sucesso', response.data.decode('utf-8'))
        else:
            # Agora verificamos se a resposta contém o campo 'error' no JSON
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn('error', response_json)
            self.assertEqual(response_json['error'], 'Quilombo não encontrado')

    def test_delete_quilombo(self):
        """Teste para deletar um quilombo."""
        quilombo_id = 1  # Assumindo que um quilombo com esse ID existe
        response = self.app.delete(f'/quilombo/{quilombo_id}')
        
        if response.status_code == 200:
            self.assertIn('Quilombo deletado com sucesso', response.data.decode('utf-8'))
        else:
            # Agora verificamos se a resposta contém o campo 'error' no JSON
            response_json = json.loads(response.data.decode('utf-8'))
            self.assertIn('error', response_json)
            self.assertEqual(response_json['error'], 'Quilombo não encontrado')

    def test_upload_quilombo_image(self):
        """Teste para fazer upload de uma imagem para o quilombo."""
        quilombo_id = 1
        data = {
            'image': (BytesIO(b"fake image data"), 'test.png')
        }
        response = self.app.post(f'/quilomboImage/{quilombo_id}', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Imagem do quilombo carregada com sucesso', response.data.decode('utf-8'))

        # Para evitar o warning, você pode garantir que o arquivo seja fechado após o teste.
        image_path = os.path.join(self.quilombos_folder, str(quilombo_id), 'quilombo.png')
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                f.read()  # Isso vai garantir que o arquivo seja lido e fechado corretamente.

    def test_get_quilombo_image(self):
        """Teste para obter a imagem de um quilombo."""
        quilombo_id = 1
        # Simular upload de uma imagem primeiro
        image_path = os.path.join(self.quilombos_folder, str(quilombo_id), 'quilombo.png')
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(b"fake image data")

        # Agora tentar buscar a imagem
        response = self.app.get(f'/quilomboImage/{quilombo_id}')
        if response.status_code == 200:
            self.assertEqual(response.mimetype, 'image/png')
        else:
            self.assertIn('Imagem do quilombo não encontrada', response.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
