import unittest
from app.config import TestConfig
from app import create_app, db
from app.models import User

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()  # Create tables

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database

    def test_register(self):
        response = self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test',
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'User registered successfully', response.data)

        with self.app.app_context():
            user = User.query.filter_by(email='test@email.com').first()
            self.assertIsNotNone(user)

    def test_login_success(self):
        response = self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test',
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user', response.data)

    def test_login_fail(self):
        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b'Invalid credentials', response.data)

    def test_logout(self):
        response = self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test',
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user', response.data)

        response = self.client.post('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout successful', response.data)


if __name__ == '__main__':
    unittest.main()