import pymysql
from flask import current_app, g
import bcrypt

class Merchant:

    # 143

    def createMerchant(self, merch_name, merch_email, merch_phone, merch_address):
        values = (merch_name, merch_email, merch_phone, merch_address)

        try:
            with pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'],
                                 password=current_app.config['MYSQL_PASSWORD'], database=current_app.config['MERCHANT_SCHEMA'],
                                 cursorclass=pymysql.cursors.DictCursor) as connect:
              
                sqlQuery = """
                    INSERT INTO Merchant (merch_name, merch_email, merch_phone, merch_address, pass_hash, date_created, date_updated_on, status)
                    VALUES (%s, %s, %s, %s, 1, NOW(), NOW(), 1)
                """
                with connect.cursor() as cursor:
                    cursor.execute(sqlQuery, values)
                    connect.commit()
                return True  # Merchant created successfully

        except pymysql.MySQLError as e:
            print(f"Error creating merchant: {e}")
            return False  # Return False in case of an error

    # 144
    def getMerchantData(self):
        try:

            with pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'],
                                 password=current_app.config['MYSQL_PASSWORD'], database=current_app.config['MERCHANT_SCHEMA'], 
                                 cursorclass=pymysql.cursors.DictCursor) as connect:

                with connect.cursor() as cursor:
                    sqlQuery = "SELECT * FROM Merchant"
                    cursor.execute(sqlQuery)
                    merchant = cursor.fetchall()

                if not merchant:
                    return False  # No merchant data found

                return merchant  # Merchant data fetched successfully

        except pymysql.MySQLError as e:
            print(f"Error fetching merchant data: {e}")
            return False  # Return False in case of an error

    def getOneMerchant(self, id):
        try:

            with pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'],
                                 password=current_app.config['MYSQL_PASSWORD'], database=current_app.config['MERCHANT_SCHEMA'], 
                                 cursorclass=pymysql.cursors.DictCursor) as connect:

                with connect.cursor() as cursor:
                    sqlQuery = "SELECT * FROM Merchant WHERE merch_id = %s"
                    cursor.execute(sqlQuery, (id,))
                    merchant = cursor.fetchone()

                if merchant is None:
                    return False

                return merchant  # Merchant fetched successfully

        except pymysql.MySQLError as e:
            print(f"Error fetching merchant: {e}")
            return False  # Return False in case of an error

    # 146
    def updateMerchantDetails(self, merchID,merchData):
        
        connect = pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'], password=current_app.config['MYSQL_PASSWORD'], database=current_app.config['MERCHANT_SCHEMA'],
                                  cursorclass=pymysql.cursors.DictCursor)
        try:
            
            query = """UPDATE Merchant 
                    SET merch_name = %s, merch_email = %s, merch_phone = %s, date_updated_on = NOW()
                    WHERE merch_id = %s"""
            
            with connect.cursor() as cursor:
                affected_rows = cursor.execute(query, (merchData['merch_name'], merchData['merch_email'], merchData['merch_phone'], merchID))

                connect.commit()

            if affected_rows == 0:
                return False  # No rows were affected

            return True

        except pymysql.MySQLError as e:
            connect.rollback()
            print(f"Error updating merchant details: {e}")
            return False

    def updateMerchantStatus(self, merch_id, status):

        connect = pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'],
                                  password=current_app.config['MYSQL_PASSWORD'], database=current_app.config['MERCHANT_SCHEMA'],    
                                  cursorclass=pymysql.cursors.DictCursor)
        try:
            with connect.cursor() as cursor:
                new_status = bool(int(status))  # Convert status to boolean
                sql = "UPDATE Merchant SET status = %s, date_updated_on = NOW() WHERE merch_id = %s"

                validate = cursor.execute(sql, (new_status, merch_id))

                if validate == 0:

                    return False  # No rows affected

            
            connect.commit()
            return True

        except Exception as e:
            print(f"Error updating merchant status: {str(e)}")
            connect.rollback()
            return False
        finally:
            connect.close()

    def getDBConnection(self):
        if 'db' not in g:
            g.db = pymysql.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MERCHANT_SCHEMA'],
                cursorclass=pymysql.cursors.DictCursor
            )
        return g.db


    # 130
    def registerMerchant(self, merch_email, pass_hash, merch_name=None, merch_phone=None, merch_address=None):

        pass_hash = bcrypt.hashpw(pass_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        existing_merchant = self.getMerchantByEmail(merch_email)

        if existing_merchant:
            return False, "Email already in use"

        try:
            connection = self.getDBConnection()
            with connection.cursor() as cursor:
                sql_query = """
                    INSERT INTO Merchant (merch_email, pass_hash, merch_name, merch_phone, merch_address, date_created, date_updated_on, status)
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 1)
                """
                cursor.execute(sql_query, (merch_email, pass_hash, merch_name, merch_phone, merch_address))
                connection.commit()
                return True, "Merchant created successfully"

        except pymysql.MySQLError as e:
            print(f"Error creating merchant: {e}")
            return False, f"Error creating merchant: {e}"

    # 131
    def login(self, merch_email, pass_hash):
        # Login function using bcrypt
        try:
            merchant = self.getMerchantByEmail(merch_email)
            if not merchant:
                return False, "Invalid email"

            if not bcrypt.checkpw(pass_hash.encode('utf-8'), merchant['pass_hash'].encode('utf-8')):
                return False, "Invalid password"

            return True, merchant  # Login successful, return merchant data

        except pymysql.MySQLError as e:
            print(f"Error logging in: {e}")
            return False, "Error logging in"

    def getMerchantByEmail(self, merch_email):
        # Fetch merchant by email - used in login and create
        try:
            connection = self.getDBConnection()
            with connection.cursor() as cursor:
                sql_query = "SELECT * FROM Merchant WHERE merch_email = %s"
                cursor.execute(sql_query, (merch_email,))
                merchant = cursor.fetchone()  
                return merchant  # Merchant data fetched successfully

        except pymysql.MySQLError as e:
            print(f"Error fetching merchant by email: {e}")
            return None

    def getMerchantByID(self, merch_id):
        # Fetch merchant by ID from the database
        try:
            connection = self.getDBConnection()
            with connection.cursor() as cursor:
                sql_query = "SELECT * FROM Merchant WHERE merch_id = %s"
                cursor.execute(sql_query, (merch_id,))
                merchant = cursor.fetchone()

                if not merchant:
                    return None  # No merchant found

                return merchant  # Merchant data fetched successfully

        except pymysql.MySQLError as e:
            print(f"Error fetching merchant: {e}")
            return None
    
    # 133
    def addPayment(self, merch_email, amount):
        # Fetch the merchant by email
        merchant = self.getMerchantByEmail(merch_email)
        if not merchant:
            return False, "Merchant not found"

        merch_id = merchant['merch_id']
        connection = self.getDBConnection()

        try:
            with connection.cursor() as cursor:
                # Add the payment to the transaction record
                query = """
                    INSERT INTO transaction_management.Transaction (merch_id, amount, payment_date, status, date_created, date_updated_on)
                    VALUES (%s, %s, NOW(), 'completed', NOW(), NOW())
                """
                cursor.execute(query, (merch_id, amount))
                connection.commit()

            return True, "Payment added successfully"
        
        except pymysql.MySQLError as e:
            print(f"Error adding payment: {e}")
            return False, "Error adding payment"

    def getTransactionHistory(self, merch_id):
        try:
            connection = self.getDBConnection()
            with connection.cursor() as cursor:
                # Fetch all transactions for the merchant
                query = """
                    SELECT payment_id, amount, payment_date, status FROM transaction_management.Transaction
                    WHERE merch_id = %s
                """
                cursor.execute(query, (merch_id,))
                transactions = cursor.fetchall()

                # Calculate the total balance
                balance_query = """
                    SELECT SUM(amount) as total_balance FROM transaction_management.Transaction
                    WHERE merch_id = %s AND status = 'completed'
                """
                cursor.execute(balance_query, (merch_id,))
                balance = cursor.fetchone()['total_balance'] or 0.0

            return transactions, balance

        except pymysql.MySQLError as e:
            print(f"Error fetching transactions: {e}")
            return None, 0.0  # Return None for transactions and 0.0 for balance in case of an error