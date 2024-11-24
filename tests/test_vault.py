import unittest
from app.config import TestConfig
from app import create_app, db

class VaultTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()  # Create tables

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database

    def test_add_entry(self):
        self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test',
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'title', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        #print(response.json)

    def test_remove_entry(self):
        self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test',
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'title', response.data)

        response = self.client.post('/entries/add', json={
            'title': 'Account 2',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'title', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        #print(response.json)

        response = self.client.post('/entries/remove', json=list(response.json['entries'])[0])
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry removed successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        #print(response.json)

    def test_modify_entry(self):
        self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test',
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'title', response.data)

        response = self.client.post('/entries/add', json={
            'title': 'Account 2',
            'url': 'www.other.net',
            'encrypted_username': 'Hello',
            'encrypted_password': 'World'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'title', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        #print(response.json)

        second_entry = list(response.json['entries'])[1]
        #print(second_entry)
        second_entry['title'] = 'Account 3'
        second_entry['encrypted_username'] = 'New Username'
        response = self.client.post('/entries/modify', json=second_entry)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry modified successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)
        #print(response.json)



if __name__ == '__main__':
    unittest.main()