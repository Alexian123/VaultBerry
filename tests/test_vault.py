from tests import BaseTestCase, unittest

class VaultTestCase(BaseTestCase):
    
    def test_add_entry(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

    def test_add_2_entries_with_equal_titles(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        response = self.add_vault_entry(self.example_entry_data2)
        self.assertEqual(response.status_code, 400)

    def test_add_2_entries_with_equal_timestamp(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        response = self.add_vault_entry(self.example_entry_data3)
        self.assertEqual(response.status_code, 500)

    def test_delete_entry(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        response = self.get_vault_entries()
        self.assertEqual(response.status_code, 200)

        timestamp = (response.json)[0]['timestamp']
        response = self.delete_vault_entry(timestamp)
        self.assertEqual(response.status_code, 201)

    def test_update_entry(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.add_vault_entry(self.example_entry_data1)
        self.assertEqual(response.status_code, 201)

        response = self.get_vault_entries()
        self.assertEqual(response.status_code, 200)

        entry = list(response.json)[0]
        entry['title'] = 'Account 3'
        entry['encrypted_username'] = 'New Username'
        response = self.update_vault_entry(entry)
        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()