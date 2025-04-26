from tests import BaseTestCase, unittest

class AuthTestCase(BaseTestCase):
    
    def test_register(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)
        
    def test_register_existing_email(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)
        
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 409)

    def test_login_success(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)
        
        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])
        
    def test_login_fail(self):
        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 404)

    def test_logout_success(self):
        response = self.register_user(self.example_register_data)
        self.assertEqual(response.status_code, 201)
        
        response = self.login_user_step1(self.example_email, self.example_password)
        self.assertEqual(response.status_code, 200)
        response = self.login_user_step2(response.json["server_message"])
        self.assertEqual(response.status_code, 200)
        self.login_user_step3(response.json["server_message"])
        
        response = self.logout_user()
        self.assertEqual(response.status_code, 200)
        
    def test_logout_fail(self):
        response = self.logout_user()
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()