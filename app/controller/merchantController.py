# app/controller/merchantController.py
from flask import Blueprint, request, jsonify, session
from ..models.merchant import Merchant
import bcrypt

merchant_instance = Merchant()

# Create the Blueprint for merchant-related routes
merchantBlueprint = Blueprint('merchant', __name__)

# Route for creating a new merchant (registration)
@merchantBlueprint.route('/register-merchant', methods=['POST'])
def registerMerchant():
    data = request.get_json()
    
    # Extract data from request
    merch_email = data.get('merch_email')
    password = data.get('password') # Plain-text password entered by the user
    merch_name = data.get('merch_name')
    merch_phone = data.get('merch_phone')
    merch_address = data.get('merch_address')
    
    # Call the Merchant model to create the new merchant

    success, message = merchant_instance.registerMerchant(merch_email, password, merch_name, merch_phone, merch_address)

    
    if success:
        return jsonify({'success': True, 'message': message}), 201  # 201 = Created
    else:
        return jsonify({'success': False, 'message': message}), 400  # 400 = Bad Request


# Login Merchant Endpoint
@merchantBlueprint.route('/login', methods=['POST'])
def login_merchant():
    data = request.get_json()
    email = data['merch_email']
    password = data['password'] # Plain-text password entered by the user

    # Fetch the merchant from the database
    merchant = merchant_instance.getMerchantByEmail(email)

    # Verify the password using native bcrypt
    # The plain-text password (password) is compared with the hashed password (merchant['pass_hash'])
    if merchant and bcrypt.checkpw(password.encode('utf-8'), merchant['pass_hash'].encode('utf-8')):
        # Store the merchant ID in the session upon successful login
        session['merch_id'] = merchant['merch_id']
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401


# Fetch Merchant Profile Endpoint
@merchantBlueprint.route('/profile', methods=['GET'])
def profile():
    if 'merch_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 401

    # Fetch the merchant profile
    merchant = merchant_instance.getMerchantByID(session['merch_id'])
    if merchant:
        return jsonify({
            'success': True,
            'merchant': {
                'name': merchant['merch_name'],
                'email': merchant['merch_email'],
                'phone': merchant['merch_phone'],
                'address': merchant['merch_address']
            }
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Merchant not found'}), 404


# Update Merchant Details Endpoint
@merchantBlueprint.route('/update', methods=['PUT'])
def update_merchant():
    if 'merch_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 401

    data = request.get_json()
    result = merchant_instance.updateMerchantDetails(session['merch_id'], data)

    if result:
        return jsonify({'success': True, 'message': 'Merchant details updated successfully'}), 200
    else:
        return jsonify({'success': False, 'message': 'Error updating details'}), 500


# Logout Merchant Endpoint
@merchantBlueprint.route('/logout', methods=['POST'])
def logout():
    session.pop('merch_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200

# Route to send payment to merchant (via the "bank" page)
@merchantBlueprint.route('/bankpage', methods=['POST'])
def processPayment():
    data = request.get_json()
    merch_email = data.get('merch_email')
    amount = data.get('amount')

    # Find the merchant by email
    merchant = merchant_instance.getMerchantByEmail(merch_email)

    if not merchant:
        return jsonify({'success': False, 'message': 'Merchant not found'}), 404
    
    # Call the model to add the payment to the merchant's account
    success, message = merchant_instance.addPayment(merch_email, amount)

    if success:
        return jsonify({'success': True, 'message': 'Payment sent successfully'}), 200
    else:
        return jsonify({'success': False, 'message': message}), 400

# Route to fetch the merchant's transactions and balance
@merchantBlueprint.route('/merchant/transactions', methods=['GET'])
def merchant_transactions():
    merch_id = request.args.get('merch_id')  # Assuming merchant ID is passed as a query parameter
    transactions, balance = merchant_instance.getTransactionHistory(merch_id)

    if transactions is not None:
        return jsonify({
            'success': True,
            'transactions': transactions,
            'balance': balance
        }), 200
    else:
        return jsonify({'success': False, 'message': 'Merchant not found'}), 404