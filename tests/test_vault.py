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

    def test_add_entries(self):
        self.client.post('/register', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries', json={
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry added successfully', response.data)

        response = self.client.post('/entries', json={
            'title': 'Account 2',
            'url': 'www.other.net',
            'encrypted_username': 'Hello',
            'encrypted_password': 'World'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry added successfully', response.data)

        response = self.client.post('/entries', json={
            'title': 'Account 3',
            'encrypted_username': 'John',
            'encrypted_password': 'blablabla'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry added successfully', response.data)

        response = self.client.get('/entries')
        print(response.data)


if __name__ == '__main__':
    unittest.main()