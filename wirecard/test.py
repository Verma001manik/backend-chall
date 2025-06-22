import unittest
from main import app

class PaymentAPITestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_boleto_payment(self):
        data = {
            'client_id': '1',
            'buyer_name': 'John Doe',
            'buyer_email': 'john@example.com',
            'buyer_cpf': '12345678900',
            'payment_amount': '100',
            'payment_type': 'boleto'
        }
        response = self.client.post('/handle-payment', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'boleto_number', response.data)

    def test_credit_card_payment_valid(self):
        data = {
            'client_id': '2',
            'buyer_name': 'Alice',
            'buyer_email': 'alice@example.com',
            'buyer_cpf': '98765432100',
            'payment_amount': '200',
            'payment_type': 'credit',
            'card_holder': 'Alice',
            'card_number': '4111111111111111',  # Valid Visa
            'card_expiration': '12/25',
            'card_cvv': '123'
        }
        response = self.client.post('/handle-payment', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'approved', response.data)

    def test_credit_card_payment_invalid(self):
        data = {
            'client_id': '3',
            'buyer_name': 'Bob',
            'buyer_email': 'bob@example.com',
            'buyer_cpf': '98765432100',
            'payment_amount': '200',
            'payment_type': 'credit',
            'card_holder': 'Bob',
            'card_number': '1234567890123456',  # Invalid card
            'card_expiration': '12/25',
            'card_cvv': '123'
        }
        response = self.client.post('/handle-payment', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid card number', response.data)

    def test_missing_required_fields(self):
        data = {
            'client_id': '4',
            'buyer_email': 'missing@example.com',
            'buyer_cpf': '12345678900',
            'payment_amount': '100',
            'payment_type': 'boleto'
        }
        response = self.client.post('/handle-payment', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_invalid_amount(self):
        data = {
            'client_id': '5',
            'buyer_name': 'Bad Amount',
            'buyer_email': 'bad@example.com',
            'buyer_cpf': '12345678900',
            'payment_amount': '-50',
            'payment_type': 'boleto'
        }
        response = self.client.post('/handle-payment', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid amount', response.data)

    def test_status_check_existing(self):
        # First create a boleto payment
        data = {
            'client_id': '6',
            'buyer_name': 'Charlie',
            'buyer_email': 'charlie@example.com',
            'buyer_cpf': '12345678900',
            'payment_amount': '150',
            'payment_type': 'boleto'
        }
        self.client.post('/handle-payment', data=data)

        response = self.client.get('/status/6')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'pending', response.data)

    def test_status_not_found(self):
        response = self.client.get('/status/9999')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Payment not found', response.data)

if __name__ == '__main__':
    unittest.main()
