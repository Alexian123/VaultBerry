import unittest
from scramp import ScramClient
from config import TestConfig
from app import create_app, db

class BaseTestCase(unittest.TestCase):
    
    example_email = "x"
    example_password = "x"
    
    example_register_data = {
        "account": {
            "email": example_email
        },
        "keychain": {
            "salt": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "vault_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "recovery_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
        },
        "passwords": {
            "regular_password": example_password,
            "recovery_password": "abc"
        }
    }
    
    example_account_update_data = {
        "email": "test2@email.com"
    }
    
    example_password_change_data = {
        "keychain": {
            "salt": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "vault_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "recovery_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
        },
        "passwords": {
            "regular_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "recovery_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
        }
    }
    
    example_entry_data1 = {
        "timestamp": 1235,
        "title": "Account 1",
        "url": "www.website.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    example_entry_data2 = {
        "timestamp": 2000,
        "title": "Account 1",
        "url": "www.website.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    example_entry_data3 = {
        "timestamp": 1235,
        "title": "Account 2",
        "url": "www.website.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    scram_client: ScramClient
    
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
        return self.client.post("/register", json=json_data)
    
    def login_user_step1(self, email, password):
        self.scram_client = ScramClient(['SCRAM-SHA-256'], email, password)
        client_first_message = self.scram_client.get_client_first()
        return self.client.post("/login/step1", json={
            "email": email,
            "client_message": client_first_message
        })
    
    def login_user_step2(self, server_first_message):
        self.scram_client.set_server_first(server_first_message)
        client_final_message = self.scram_client.get_client_final()
        return self.client.post("/login/step2", json={
            "email": self.scram_client.username,
            "client_message": client_final_message
        })
        
    def login_user_step3(self, server_final_message):
        self.scram_client.set_server_final(server_final_message)
    
    def logout_user(self):
        return self.client.post("/logout")
    
    def get_vault_entries(self):
        return self.client.get("/entries")
    
    def add_vault_entry(self, json_data):
        return self.client.post("/entries", json=json_data)
    
    def update_vault_entry(self, json_data):
        return self.client.patch("/entries", json=json_data)
    
    def delete_vault_entry(self, timestamp):
        return self.client.delete(f"/entries/{timestamp}")
    
    def update_account(self, json_data):
        return self.client.patch("/account", json=json_data)
    
    def delete_account(self):
        return self.client.delete("/account")
    
    def change_password(self, json_data):
        return self.client.patch("/account/password", json=json_data)
    
    def setup_2fa(self):
        return self.client.post("/account/2fa/setup")
    
    def get_2fa_status(self):
        return self.client.get("/account/2fa/status")
    
    def disable_2fa(self):
        return self.client.post("/account/2fa/disable")