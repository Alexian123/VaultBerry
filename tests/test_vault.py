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

    def test_add_2_entries_with_equal_titles(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com',
                'password': 'test'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            }
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'timestamp': 1234,
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.post('/entries/add', json={
            'timestamp': 1235,
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'error', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)

    def test_add_2_entries_with_equal_timestamp(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com',
                'password': 'test'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            }
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'timestamp': 1234,
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.post('/entries/add', json={
            'timestamp': 1234,
            'title': 'Account 2',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 500)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)

    def test_add_entry(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com',
                'password': 'test'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            }
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'timestamp': 1234,
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)

    def test_delete_entry(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com',
                'password': 'test'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            }
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'timestamp': 1234,
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.post('/entries/add', json={
            'timestamp': 1235,
            'title': 'Account 2',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)

        timestamp = (response.json)[0]['timestamp']
        response = self.client.delete(f'/entries/delete/{timestamp}')
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry deleted successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)

    def test_update_entry(self):
        response = self.client.post('/register', json={
            'account': {
                'email': 'test@email.com',
                'password': 'test'
            },
            'keychain': {
                'salt': 'abcdefghabcdefghabcdefgh',
                'vault_key': 'key',
                'recovery_key': 'also key'
            }
        })

        self.client.post('/login', json={
            'email': 'test@email.com',
            'password': 'test'
        })

        response = self.client.post('/entries/add', json={
            'timestamp': 1235,
            'title': 'Account 1',
            'url': 'www.website.com',
            'encrypted_username': 'abcdefg',
            'encrypted_password': 'zxc'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.post('/entries/add', json={
            'timestamp': 1236,
            'title': 'Account 2',
            'url': 'www.other.net',
            'encrypted_username': 'Hello',
            'encrypted_password': 'World'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)

        second_entry = list(response.json)[1]
        second_entry['title'] = 'Account 3'
        second_entry['encrypted_username'] = 'New Username'
        response = self.client.post('/entries/update', json=second_entry)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Entry modified successfully', response.data)

        response = self.client.get('/entries')
        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main()