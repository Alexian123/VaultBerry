import unittest
from scramp import ScramClient
from config import TestConfig
from app import create_app, db

class BaseTestCase(unittest.TestCase):
    
    example_email = "test@email.com"
    example_password = "TestPassword123!"
    
    example_register_data = {
        "account_info": {
            "email": example_email,
            "first_name": "Test",
            "last_name": "User"
        },
        "passwords": {
            "regular_password": example_password,
            "recovery_password": "test"
        },
        "keychain": {
            "salt": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "vault_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "recovery_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
        }
    }
    
    example_account_update_data = {
        "email": "test2@email.com"
    }
    
    example_password_change_data = {
        "passwords": {
            "regular_password": example_password,
            "recovery_password": "test"
        },
        "keychain": {
            "salt": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "vault_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
            "recovery_key": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
        },
        "re_encrypt": False
    }
    
    example_entry_preview1 = {
        "id": 1,
        "title": "Account 1"
    }
    
    example_entry_data1 = {
        "title": "Account 1",
        "url": "www.website.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    example_entry_preview2 = {
        "id": 2,
        "title": "Account 1"
    }
    
    example_entry_data2 = {
        "title": "Account 2",
        "url": "www.address.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    example_entry_preview1 = {
        "id": 2,
        "title": "Account 2"
    }
    
    example_entry_data3 = {
        "title": "Entry 1",
        "url": "www.website.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    example_entry_data4 = {
        "title": "Entry 2",
        "url": "www.address.com",
        "encrypted_username": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ=",
        "encrypted_password": "YWJjYWJjYWFhYWFhYWFhc2RzYWQ="
    }
    
    example_keywords_data = {
        "keywords": ["account", "website"]
    }
    
    scram_client: ScramClient
    
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

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
    
    def get_all_vault_entry_details(self):
        return self.client.get("/vault/details")
    
    def get_all_vault_entry_previews(self):
        return self.client.get("/vault/previews")
    
    def add_vault_entry(self, json_data):
        return self.client.post("/vault/add", json=json_data)
    
    def update_vault_entry(self, id, json_data):
        return self.client.patch(f"/vault/update/{id}", json=json_data)
    
    def delete_vault_entry(self, id):
        return self.client.delete(f"/vault/delete/{id}")
    
    def search_vault_entries_by_keyword(self, json_data):
        return self.client.post("/vault/search", json=json_data)
    
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