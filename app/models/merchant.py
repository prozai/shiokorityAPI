import pymysql
from flask import current_app, g
import bcrypt

class Merchant:

    # 143

    def createMerchant(self, merch_name, merch_email, merch_phone, merch_address):
        values = (merch_name, merch_email, merch_phone, merch_address)

        try:
            with pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'],
                                 password=current_app.config['MYSQL_PASSWORD'], database='merchant_management',
                                 cursorclass=pymysql.cursors.DictCursor) as connect:
              
                sqlQuery = """
                    INSERT INTO merchant (merch_name, merch_email, merch_phone, merch_address, pass_hash, date_created, date_updated_on, status)
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
                                 password=current_app.config['MYSQL_PASSWORD'], database='merchant_management',
                                 cursorclass=pymysql.cursors.DictCursor) as connect:

                with connect.cursor() as cursor:
                    sqlQuery = "SELECT * FROM merchant"
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
                                 password=current_app.config['MYSQL_PASSWORD'], database='merchant_management',
                                 cursorclass=pymysql.cursors.DictCursor) as connect:

                with connect.cursor() as cursor:
                    sqlQuery = "SELECT * FROM merchant WHERE merch_id = %s"
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
        
        connect = pymysql.connect(host=current_app.config['MYSQL_HOST'], user=current_app.config['MYSQL_USER'], password=current_app.config['MYSQL_PASSWORD'], database='merchant_management',
                                  cursorclass=pymysql.cursors.DictCursor)
        try:
            
            query = """UPDATE merchant_management.merchant 
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
                                  password=current_app.config['MYSQL_PASSWORD'], database='merchant_management',
                                  cursorclass=pymysql.cursors.DictCursor)
        try:
            with connect.cursor() as cursor:
                new_status = bool(int(status))  # Convert status to boolean
                sql = "UPDATE merchant SET status = %s, date_updated_on = NOW() WHERE merch_id = %s"

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
                database='merchant_management',
                cursorclass=pymysql.cursors.DictCursor
            )
        return g.db

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
                    VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), 'active')
                """
                cursor.execute(sql_query, (merch_email, pass_hash, merch_name, merch_phone, merch_address))
                connection.commit()
                return True, "Merchant created successfully"

        except pymysql.MySQLError as e:
            print(f"Error creating merchant: {e}")
            return False, f"Error creating merchant: {e}"

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

    def getMerchantByID(self, merchant_id):
        """Fetch merchant by ID from the database"""
        try:
            connection = self.getDBConnection()
            with connection.cursor() as cursor:
                sql_query = "SELECT * FROM Merchant WHERE merch_id = %s"
                cursor.execute(sql_query, (merchant_id,))
                merchant = cursor.fetchone()

                if not merchant:
                    return None  # No merchant found

                return merchant  # Merchant data fetched successfully

        except pymysql.MySQLError as e:
            print(f"Error fetching merchant: {e}")
            return None