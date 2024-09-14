from flask import Blueprint, request, session, jsonify
from ..models.administrator import Administrator
from ..models.merchant import Merchant 
from werkzeug.exceptions import BadRequest

adminBlueprint = Blueprint('adminBlueprint', __name__)

@adminBlueprint.route("/login/admin", methods=['POST'])
def adminLogin():
    try:
        data = request.get_json()

        if not data:
            raise BadRequest("No input data provided")
        
        email = data.get('email', '')
        password = data.get('password', '')

        if not email or not password:
            raise BadRequest("Email and password are required")

        admin = Administrator.validateLogin(email, password)
        
        if admin:
            session['loggedIn'] = True
            return jsonify(success=True), 200
        
        else:
            return jsonify(success=False), 401

    except BadRequest as e:
        return jsonify(success=False, message=str(e)), 400
    
    except Exception as e:
        # Log the error here
        print(f"An error occurred: {str(e)}")
        return jsonify(success=False, message="An unexpected error occurred"), 500

@adminBlueprint.route("/logout/admin",methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

@adminBlueprint.route("/create-merchant", methods=['POST'])
def createMerchant():
    if request.method == 'POST':
        data = request.get_json()  # Get the JSON data from the request
        print(data)
        # Extract the necessary fields
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        address = data.get('address')

        createdMerchant = Merchant.createMerchant(name, email, phone, address)

        if createdMerchant:
            return jsonify(success=True), 200
        else:
            return jsonify(success=False), 400
    

@adminBlueprint.route('/admin/view-merchant', methods=['GET'])
def fetchMerchantList():
    try:
        if request.method == 'GET':
            merchants = Merchant().getMerchantData()
            if merchants:
                return jsonify(merchants), 200
            else:
                return jsonify(success=False), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@adminBlueprint.route('/admin/merchants/<int:merch_id>', methods=['GET'])
def getMerchant(merch_id):
    
    if request.method == 'GET':
        
        merchants = Merchant().getOneMerchant(merch_id)
        
        if merchants is not False:
            return jsonify(merchants), 200
        else:
            return jsonify({"error": "Could not fetch merchant data"}), 500


@adminBlueprint.route('/admin/merchants/<int:merch_id>', methods=['PUT'])
def submitMerchantUpdate(merch_id):
    
    if request.method == 'PUT':
        data = request.json
        updateStatus = Merchant().updateMerchantDetails(merch_id, data)
        
        if updateStatus:
            return jsonify(success=True), 200
        else:
            
            return jsonify(success=False), 400
        
    else:
        return jsonify(success=False), 500
    
    
@adminBlueprint.route('/admin/suspend-merchants/<int:merch_id>', methods=['PUT'])
def updateMerchantStatus(merch_id):
    
    if request.method == 'PUT':

        data = request.json
        status = data.get('status')

        updateStatus = Merchant().updateMerchantStatus(merch_id, status)
        
        if updateStatus:
            return jsonify(success=True), 200
        else:
            return jsonify(success=False), 400
        
    else:
        return jsonify(success=False), 500