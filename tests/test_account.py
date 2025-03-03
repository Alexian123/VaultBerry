import unittest
from config import TestConfig
from app import create_app, db

class AccountTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()  # Create tables

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database

    def test_update_account(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            },
            'password': 'test'
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'salt', response.data)

        response = self.client.post('/account', json={
            'email': 'test2@email.com'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'updated', response.data)

    def test_delete_account(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            },
            'password': 'test'
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'salt', response.data)

        response = self.client.delete('/account')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'deleted', response.data)

        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 401)

    def test_update_keychain(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            },
            'password': 'test'
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'salt', response.data)

        response = self.client.post('/account/keychain', json={
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key2',
            'recovery_key': 'also key'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'updated', response.data)

if __name__ == '__main__':
    unittest.main()