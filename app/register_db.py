from psycopg2 import OperationalError, DatabaseError
from database import connect_db, hash_text

def register_database(user_info):
    conn = None
    cursor = None
    try:
        conn, cursor = connect_db()

        # SQL query to create a table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS user_info (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            password TEXT NOT NULL,
            verify BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''

        cursor.execute(create_table_query)
        conn.commit()

        password = user_info['password']
        email = user_info['email']
        username = user_info['username']
        hashed_password = hash_text(password)

        insert_query = """
        INSERT INTO user_info (username, email, password) 
        VALUES (%s, %s, %s);
        """

        cursor.execute(insert_query, (username, email, hashed_password))
        conn.commit()

        return "Success"

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