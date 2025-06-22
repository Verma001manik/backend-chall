from flask import Flask, request, jsonify,render_template

app = Flask(__name__)
import random 
# simple mock database
payments_db = {}

def get_card_issuer(card_number):
    if card_number.startswith('4'):
        return 'Visa'
    elif card_number.startswith('5'):
        return 'MasterCard'
    elif card_number.startswith('3'):
        return 'American Express'
    else:
        return 'Unknown'

def is_valid_card(card_number):
    card_number = card_number.replace(" ", "")
    total = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n = n * 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

@app.route('/')
def index():
    return render_template("checkout.html")

@app.route('/handle-payment', methods=['POST'])
def handle_payment():
    client_id = request.form.get('client_id')
    name = request.form.get('buyer_name')
    email = request.form.get('buyer_email')
    cpf = request.form.get('buyer_cpf')
    amount = request.form.get('payment_amount')
    payment_type = request.form.get('payment_type')

    if not all([client_id, name, email, cpf, amount, payment_type]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
    except ValueError:
        return jsonify({'error': 'Amount must be a number'}), 400

    payment_record = {
        'client_id': client_id,
        'buyer': {
            'name': name,
            'email': email,
            'cpf': cpf
        },
        'amount': amount,
        'type': payment_type
    }

    if payment_type == 'boleto':
        boleto_number =  str(random.randint(10**11, 10**12 - 1))
        payment_record['boleto_number'] = boleto_number
        payment_record['status'] = 'pending'
        payments_db[client_id] = payment_record
        return jsonify({'status': 'pending', 'boleto_number': boleto_number}), 200

    elif payment_type == 'credit' or payment_type == 'debit':
        card_holder = request.form.get('card_holder')
        card_number = request.form.get('card_number')
        card_expiration = request.form.get('card_expiration')
        card_cvv = request.form.get('card_cvv')

        if not all([card_holder, card_number, card_expiration, card_cvv]):
            return jsonify({'error': 'Missing card details'}), 400

        issuer = get_card_issuer(card_number)
        valid = is_valid_card(card_number)

        if not valid:
            payment_record['status'] = 'declined'
            payments_db[client_id] = payment_record
            return jsonify({'status': 'declined', 'reason': 'Invalid card number'}), 400

        payment_record['card'] = {
            'holder': card_holder,
            'number': card_number,
            'expiration': card_expiration,
            'cvv': card_cvv,
            'issuer': issuer
        }
        payment_record['status'] = 'approved'
        payments_db[client_id] = payment_record
        return jsonify({'status': 'approved', 'issuer': issuer}), 200

    else:
        return jsonify({'error': 'Invalid payment type'}), 400

@app.route('/status/<client_id>', methods=['GET'])
def check_status(client_id):
    payment = payments_db.get(client_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404

    return jsonify(payment), 200

if __name__ == '__main__':
    app.run(debug=True)
