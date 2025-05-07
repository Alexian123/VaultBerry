from tests import BaseTestCase, unittest

class VaultTestCase(BaseTestCase):
    
    def test_add_entry(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

    def test_add_2_entries_with_equal_titles(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 409)

    def test_delete_entry(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        id = response.json["id"]
        response = self.delete_vault_entry(id)
        self.assertEqual(response.status_code, 200)

    def test_update_entry(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)
        id = response.json["id"]

        entry = {
            "last_modified": 1235,
            "title": "New Account",
        }
        response = self.update_vault_entry(id, entry)
        self.assertEqual(response.status_code, 200)
        
    def test_search_entries(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        response = self.add_vault_entry(self.example_entry_data2)
        self.assertEqual(response.status_code, 201)
        
        response = self.add_vault_entry(self.example_entry_data3)
        self.assertEqual(response.status_code, 201)
        
        response = self.add_vault_entry(self.example_entry_data4)
        self.assertEqual(response.status_code, 201)
        
        response = self.search_vault_entries_by_keyword(self.example_keywords_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

if __name__ == "__main__":
    unittest.main()