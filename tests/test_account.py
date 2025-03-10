from tests import BaseTestCase, unittest

class AccountTestCase(BaseTestCase):

    def test_update_account(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.update_account(self.example_account_update_data)
        self.assertEqual(response.status_code, 201)

    def test_delete_account(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.delete_account()
        self.assertEqual(response.status_code, 201)
        
        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 401)

    def test_update_keychain(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)

        response = self.update_keychain(self.example_keychain_update_data)
        self.assertEqual(response.status_code, 201)
        
    def test_2fa_setup(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user(self.example_login_data)
        self.assertEqual(response.status_code, 200)
        
        response = self.setup_2fa()
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()