import psycopg2
from psycopg2 import OperationalError, DatabaseError
import hashlib
import os
import random

DB_NAME = "wifi_card"
DB_USER = "admin"
DB_PASS = "admin"
DB_HOST = "db"
DB_PORT = "5432"

def hash_text(text):
    # Encode the text to bytes, then hash using SHA-256
    hashed = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return hashed

def connect_db():
    # Connect to the database
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Database connected successfully")
    
    # Create a cursor object
    cursor = conn.cursor()

    return conn, cursor

def read_ads_db(shop_location):
    conn = None
    cursor = None
    try:
        conn, cursor = connect_db()

        database_name = f"ad_campaigns_{shop_location['target_state']}_{shop_location['target_area']}"

        # Define your SQL query
        query = f"SELECT * FROM {database_name}"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result
        rows = cursor.fetchall()

        conn.commit()

        return rows

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
    finally:
        # Close the cursor and connection
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def shop_database(shop_info):
    if shop_info is None:
        return "No data found"
    else:
        shop_name = shop_info["shop_name"]
        phone_num = shop_info["phone_num"]
        wifi_name = shop_info["wifi_name"]
        wifi_password = shop_info["wifi_password"]
        security_type = shop_info["security_type"]
        target_state = shop_info["target_state"]
        target_area = shop_info["target_area"]

        shop_code = hash_text(shop_name + wifi_name)[:6]

        try:
            conn, cursor = connect_db()

            # SQL query to create a table if it doesn't exist
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS wifi_shops (
                id SERIAL PRIMARY KEY,
                shop_code VARCHAR(255) NOT NULL,
                shop_name VARCHAR(255) NOT NULL,
                phone_num VARCHAR(15) NOT NULL,
                wifi_name VARCHAR(255) NOT NULL,
                wifi_password VARCHAR(255) NOT NULL,
                security_type VARCHAR(10) NOT NULL CHECK (security_type IN ('WPA', 'WPA2', 'WEP', 'Open')),
                target_state TEXT NOT NULL,
                target_area TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            '''

            # Execute the query
            cursor.execute(create_table_query)

            # Commit the transaction
            conn.commit()

            check_query = """
            SELECT EXISTS (
                SELECT *
                FROM wifi_shops 
                WHERE shop_name = %s
            );
            """
            cursor.execute(check_query, (shop_name,))
            exists = cursor.fetchone()[0]  # Fetch the result

            if exists:
                return "Shop Exists"
            else:
                print("Table created successfully (if it didn't exist already).")

                insert_query = """
                INSERT INTO wifi_shops (shop_name, shop_code, phone_num, wifi_name, wifi_password, security_type, target_state, target_area)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """

                # Execute the query
                cursor.execute(insert_query, (shop_name, shop_code, phone_num, wifi_name, wifi_password, security_type, target_state, target_area))
                
                # Commit the transaction
                conn.commit()

                return "Data inserted successfully!"

        except OperationalError as e:
            # Handle specific operational errors (e.g., connection issues)
            print(f"OperationalError: {e}")
        except DatabaseError as e:
            # Handle database-related errors (e.g., invalid credentials or database not found)
            print(f"DatabaseError: {e}")
        except Exception as e:
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
        finally:
            # Ensure the connection is closed when done
            if 'conn' in locals() and conn:
                conn.close()
                print("Database connection closed.")

def ads_db(form_data, ad_video):
    print(form_data)
    company_name = form_data["company_name"]
    budget = form_data["budget"]
    campaign_title = form_data["campaign_title"]
    start_date = form_data["start_date"]
    duration = form_data["duration"]
    ad_category = form_data["ad_category"]
    notes = form_data["notes"]
    url_link = form_data["url_link"]

    target_state = form_data["target_state"]
    target_area = form_data["target_area"]
    
    exposure = 0

    ad_video = os.path.join(os.getcwd(), ad_video)

    # video_name_hash = hash_text(company_name + start_date)[:6] + ".mp4"
    # rename_file(video_path, video_name_hash)

    try:
        conn, cursor = connect_db()

        database_name = f"ad_campaigns_{target_state}_{target_area}"

        # SQL query to create a table if it doesn't exist
        create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {database_name} (
            id SERIAL PRIMARY KEY,
            company_name TEXT NOT NULL,
            budget NUMERIC(10, 2) NOT NULL,
            campaign_title TEXT NOT NULL,
            start_date DATE NOT NULL,
            duration INT NOT NULL,
            ad_category TEXT NOT NULL,
            notes TEXT,
            ad_video TEXT NOT NULL,
            url_link TEXT NOT NULL, 
            exposure INT NOT NULL,
            target_state TEXT NOT NULL,
            target_area TEXT NOT NULL,
            verify BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''

        # Execute the query
        cursor.execute(create_table_query)

        # Commit the transaction
        conn.commit()

        print("Table created successfully (if it didn't exist already).")

        insert_query = f"""
        INSERT INTO {database_name} (company_name, budget, campaign_title, start_date, duration, ad_category, notes, ad_video, url_link, exposure, target_state, target_area) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Execute the query
        cursor.execute(insert_query, (company_name, budget, campaign_title, start_date, duration, ad_category, notes, ad_video, url_link, exposure, target_state, target_area))
        
        # Commit the transaction
        conn.commit()

        return "Data inserted successfully!"

    except OperationalError as e:
        # Handle specific operational errors (e.g., connection issues)
        print(f"OperationalError: {e}")
    except DatabaseError as e:
        # Handle database-related errors (e.g., invalid credentials or database not found)
        print(f"DatabaseError: {e}")
    except Exception as e:
        # Catch any other exceptions
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed when done
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

def ad_info(selected_ad, shop_location):
    try:
        conn, cursor = connect_db()

        database_name = f"ad_campaigns_{shop_location['target_state']}_{shop_location['target_area']}"

        search_query = f"""
        SELECT * FROM {database_name} WHERE id = %s
        """

        cursor.execute(search_query, (selected_ad,))
        conn.commit()

        ad_data = cursor.fetchone()

        data_json = {}

        if ad_data:
            url_link = ad_data[-5]
            media_path = ad_data[-6]

            media_path = "/static" + media_path.split("static")[-1]

            data_json = {
                "media_path": media_path,
                "url_link": url_link
            }

            exposure = ad_data[-4] + 1

            update_query = f"""
                UPDATE {database_name}
                SET exposure = %s
                WHERE id = %s
            """

            cursor.execute(update_query, (exposure, selected_ad))
            conn.commit()
            conn.close()
            return data_json

    except OperationalError as e:
        # Handle specific operational errors (e.g., connection issues)
        print(f"OperationalError: {e}")
    except DatabaseError as e:
        # Handle database-related errors (e.g., invalid credentials or database not found)
        print(f"DatabaseError: {e}")
    except Exception as e:
        # Catch any other exceptions
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed when done
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

def get_location(shop_code):
    try:
        conn, cursor = connect_db()

        search_query = """
        SELECT * FROM wifi_shops WHERE shop_code = %s
        """

        cursor.execute(search_query, (shop_code,))
        conn.commit()

        ad_data = cursor.fetchone()

        if ad_data:
            location = {
                "target_state": ad_data[-3],
                "target_area": ad_data[-2],
            }

            return location
        else:
            return {}
    
    except OperationalError as e:
        # Handle specific operational errors (e.g., connection issues)
        print(f"OperationalError: {e}")
    except DatabaseError as e:
        # Handle database-related errors (e.g., invalid credentials or database not found)
        print(f"DatabaseError: {e}")
    except Exception as e:
        # Catch any other exceptions
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed when done
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")