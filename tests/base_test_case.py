import unittest
from config import TestConfig
from app import create_app, db

class BaseTestCase(unittest.TestCase):
    
    example_register_data = {
        'account': {
            'email': 'test@email.com'
        },
        'keychain': {
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        },
        'passwords': {
            'regular_password': 'test',
            'recovery_password': 'abc'
        }
    }
    
    example_login_data = {
        'email': 'test@email.com',
        'password': 'test'
    }
    
    example_2fa_login_data = {
        'email': 'test@email.com',
        'password': 'test',
        'token': '000000'
    }
    
    example_account_update_data = {
        'email': 'test2@email.com'
    }
    
    example_password_change_data = {
        'keychain': {
            'salt': 'abcdefghabcdefghabcdefgh',
            'vault_key': 'key',
            'recovery_key': 'also key'
        },
        'passwords': {
            'regular_password': 'test1',
            'recovery_password': 'abc1'
        }
    }
    
    example_entry_data1 = {
        'timestamp': 1235,
        'title': 'Account 1',
        'url': 'www.website.com',
        'encrypted_username': 'abcdefg',
        'encrypted_password': 'zxc'
    }
    
    example_entry_data2 = {
        'timestamp': 2000,
        'title': 'Account 1',
        'url': 'www.website.com',
        'encrypted_username': 'abcdefg',
        'encrypted_password': 'zxc'
    }
    
    example_entry_data3 = {
        'timestamp': 1235,
        'title': 'Account 2',
        'url': 'www.website.com',
        'encrypted_username': 'abcdefg',
        'encrypted_password': 'zxc'
    }
    
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()  # Create tables

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database
            
    def register_user(self, json_data):
        return self.client.post('/register', json=json_data)
    
    def login_user(self, json_data):
        return self.client.post('/login', json=json_data)
    
    def logout_user(self):
        return self.client.post('/logout')
    
    def get_vault_entries(self):
        return self.client.get('/entries')
    
    def add_vault_entry(self, json_data):
        return self.client.post('/entries', json=json_data)
    
    def update_vault_entry(self, json_data):
        return self.client.patch('/entries', json=json_data)
    
    def delete_vault_entry(self, timestamp):
        return self.client.delete(f'/entries/{timestamp}')
    
    def update_account(self, json_data):
        return self.client.patch('/account', json=json_data)
    
    def delete_account(self):
        return self.client.delete('/account')
    
    def change_password(self, json_data):
        return self.client.patch('/account/password', json=json_data)
    
    def setup_2fa(self):
        return self.client.post('/account/2fa/setup')
    
    def get_2fa_status(self):
        return self.client.get('/account/2fa/status')
    
    def disable_2fa(self):
        return self.client.post('/account/2fa/disable')
    
    def verify_2fa(self, json_data):
        return self.client.post('/2fa/verify', json=json_data)