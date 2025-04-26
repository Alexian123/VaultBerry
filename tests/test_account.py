from tests import BaseTestCase, unittest

class AccountTestCase(BaseTestCase):

    def test_update_account(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.update_account(self.example_account_update_data)
        self.assertEqual(response.status_code, 200)

    def test_delete_account(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.delete_account()
        self.assertEqual(response.status_code, 200)
        
        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 404)

    def test_change_password(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])

        response = self.change_password(self.example_password_change_data)
        self.assertEqual(response.status_code, 200)
        
    def test_2fa_setup(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)

        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])
        
        response = self.setup_2fa()
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()