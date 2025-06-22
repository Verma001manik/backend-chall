import unittest
from main import app  # assuming your main file is named app.py

class PaymentAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'hello world', response.data)

    def test_boleto_payment(self):
        data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'cpf': '12345678900',
            'amount': '100',
            'type': 'boleto'
        }
        response = self.client.post('/handle-payment/1', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'boleto_number', response.data)

    def test_credit_card_payment(self):
        data = {
            'name': 'Alice',
            'email': 'alice@example.com',
            'cpf': '98765432100',
            'amount': '200',
            'type': 'creditcard',
            'cardholdername': 'Alice',
            'cardnumber': '4111111111111111',
            'cardexpiry': '12/25',
            'cardcvv': '123'
        }
        response = self.client.post('/handle-payment/2', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'payment successful', response.data)

    def test_missing_buyer_info(self):
        data = {
            'email': 'missing@example.com',
            'cpf': '12345678900',
            'amount': '100',
            'type': 'boleto'
        }
        response = self.client.post('/handle-payment/3', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing buyer info', response.data)

    def test_invalid_amount(self):
        data = {
            'name': 'Bad Amount',
            'email': 'bad@example.com',
            'cpf': '12345678900',
            'amount': '-50',
            'type': 'boleto'
        }
        response = self.client.post('/handle-payment/4', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid amount', response.data)

    def test_status_check(self):
        # First create a boleto payment
        data = {
            'name': 'Bob',
            'email': 'bob@example.com',
            'cpf': '11122233344',
            'amount': '300',
            'type': 'boleto'
        }
        self.client.post('/handle-payment/5', data=data)

        # Now check the status
        response = self.client.get('/status/5')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'pending', response.data)

    def test_status_not_found(self):
        response = self.client.get('/status/9999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Payment not found', response.data)

if __name__ == '__main__':
    unittest.main()
