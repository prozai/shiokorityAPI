import pymysql
from flask import current_app
import bcrypt
from pymysql.err import MySQLError

class Administrator():
    # 227
    def validateLogin(email, password):
        try:
            with pymysql.connect(
                host=current_app.config['MYSQL_HOST'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['USER_SCHEMA'],
                cursorclass=pymysql.cursors.DictCursor
            ) as connection:
                with connection.cursor() as cursor:
                    # Query to retrieve the hashed password and status
                    sql_query = '''
                        SELECT admin_id, admin_email, pass_hash, status 
                        FROM Admin 
                        WHERE admin_email = %s
                    '''
                    cursor.execute(sql_query, (email,))
                    user = cursor.fetchone()
                    
                    
                    if not user:
                        print(f"Login attempt failed: User not found for email {email}")
                        return False
                    
                    if user['status'] != 1:
                        print(f"Login attempt failed: Inactive account for email {email}")
                        return False
                    
                    # Retrieve the hashed password from the database
                    hashed_password = user['pass_hash'].encode('utf-8')
                    
                    # Check if the provided password matches the hashed password
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                        return True
                    
                    else:
                        print(f"Login attempt failed: Incorrect password for email {email}")
                        return False
                        

        except MySQLError as e:
            print(f"Database error during login validation: {str(e)}")
            raise

        except Exception as e:
            print(f"Unexpected error during login validation: {str(e)}")
            raise
    
    
    