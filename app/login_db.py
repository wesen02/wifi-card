from psycopg2 import OperationalError, DatabaseError
from database import connect_db, hash_text

def login_database(user_info):
    conn = None
    cursor = None
    try:
        conn, cursor = connect_db()
        username = user_info['username']
        password = user_info['password']
        hashed_password = hash_text(password)
        search_query = """
        SELECT * FROM user_info WHERE username = %s
        """

        cursor.execute(search_query, (username,))
        conn.commit()

        user_data = cursor.fetchone()

        if user_data:
            verify_db = user_data[4]
            if not verify_db:
                return "This account has not verified"
            
            userpass_db = user_data[3]

            if userpass_db != hashed_password:
                return "Wrong Password"

        return True

    except OperationalError as e:
        # Handle specific operational errors (e.g., connection issues)
        return e
    except DatabaseError as e:
        # Handle database-related errors (e.g., invalid credentials or database not found)
        return e
    except Exception as e:
        # Catch any other exceptions
        return e
    finally:
        # Ensure the connection is closed when done
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")